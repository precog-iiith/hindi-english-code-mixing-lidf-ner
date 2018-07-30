import ast
import os
import collections
from sklearn.metrics import classification_report, confusion_matrix
import pycrfsuite
import numpy as np
import joblib
from subprocess import check_output

sentences = ['Delhi mein Audi A6 10 lakh only', 'Aaj toh Ravi ke ghar se Nehru Market jaayenge', 'Today is the day Anand ko yaad aayegi.']


############# Functions for feature extraction #############
#
#
def asciiPercentage(s):
	count = 0.
	for char in s:
		if ord(char) < 128:
			count += 1
	return count/len(s)

def vowelPercentage(s):
	vowels = "aeiou"
	count = 0.
	for char in s:
		if char in vowels:
			count += 1
	return count/len(s)

def capPercentage(s):
    count = 0.
    for ch in s:
        if ch.isupper():
            count += 1
    return count / len(s)

def getWordShape(token):
    wordTransform = ''
    
    for ch in token:
        if ch.isalpha():
            if ch.isupper():
                wordTransform += 'X'
            if ch.islower():
                wordTransform += 'x'
        else:
            try:
                int(ch)
                wordTransform += 'O'
            except ValueError:
                wordTransform += ch
    return wordTransform

def word2features(sent, i):

    # feature vector
    # [TOKEN, LANG, EPOS] 
    
    # Tweet level features
    allTokens = [sent[k][0] for k in range(len(sent))]
    
    tweetTitlePer = 0.
    for word in allTokens:
        if word.istitle():
            tweetTitlePer += 1
    tweetTitlePer /= len(allTokens)
    
    tweetCapPer = 0.
    
    for word in allTokens:
        tweetCapPer += capPercentage(word)
    tweetCapPer /= len(allTokens)
    
    word = sent[i][0]
    wordShape = getWordShape(word)
    cleanWord = ''.join([ch for ch in word if ch in 'asdfghjklqwertyuiopzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'])
    normalizedWord = cleanWord.lower()
    lang = sent[i][1]
    anyCap = any(char.isupper() for char in word)
    allCap = all(char.isupper() for char in word)
    hasSpecial = any( ord(char) > 32 and ord(char) < 65 for char in word)    
    hashTag = word[0] == '#'
    mention = word[0] == '@'
    epos = sent[i][2]
    
    features = {
                'token' : word,
                'wordShape' : wordShape,
                'cleanWord' : cleanWord,
                'normalizedWord' : normalizedWord,
                
                'lang' : lang,
                'isTitle' : word.istitle(),
                'wordLength' : len(word),
                'anyCap' : anyCap, 
                'allCap' : word.isupper(),
                'hasSpecial' : hasSpecial, 
                'asciiPer' : asciiPercentage(word),\
                
                'epos' : epos, 
                'hashtag' : hashTag, 
                'mention' : mention,
                'tweetCapPer' : tweetCapPer,
                'tweetTitlePer' : tweetTitlePer,
               }
    
    features['suffix5'] = word[-5:]
    features['prefix5'] = word[:5]
    features['suffix4'] = word[-4:]
    features['prefix4'] = word[:4]
    features['suffix3'] = word[-3:]
    features['prefix3'] = word[:3]
    features['suffix2'] = word[-2:]
    features['prefix2'] = word[:2]
    features['suffix1'] = word[-1:]
    features['prefix1'] = word[:1]  
    
    if i > 0:
        word1 = sent[i - 1][0]
        lang1 = sent[i - 1][1]

        features['-1:word.lang'] = lang1
        features['-1:word.lower'] = word1.lower()
        features['-1:word.epos'] = sent[i - 1][2]
        features['-1.BOS'] = False

    else:

        features['-1:word.lang'] = ''
        features['-1:word.lower'] = ''
        features['-1:word.epos'] = ''
        features['-1:BOS'] = True

    if i < len(sent) - 1:

        word1 = sent[i + 1][0]
        lang1 = sent[i + 1][1]

        features['+1:word.lang'] = lang1
        features['+1:word.lower'] = word1.lower()
        features['+1:word.epos'] = sent[i + 1][2]
        features['+1:EOS'] = False
    else:
        features['+1:word.lang'] = ''
        features['+1:word.lower'] = ''
        features['+1:word.epos'] = ''
        features['+1:EOS'] = True

    return features

def sent2features(sent):
    features = []
    for i in range(len(sent)):
        features.append(word2features(sent, i))
    return features

def sent2labels(sent):
    allLabels = []

    for i in sent:
        currLabel = i[-1]
        if currLabel == '@' or currLabel == 'B-@':
            currLabel = 'O'
        else:
            pass
        allLabels.append(currLabel)
            
    return allLabels

def sent2tokens(sent):

	allTokens = []

	for i in sent:
		allTokens.append(i[0])

	return allTokens
#
#
####################################################

####### Running CMU ARK Twitter POS tagging model #########
#
#
inputFileName = 'cmuPOSTaggerInput.txt'
with open(inputFileName, 'w') as fp:
    for sent in sentences:
        fp.write(sent + '\n')
command = os.environ['HINGLISH_ROOT_DIR'] + '/ner/ark_tweet/runTagger.sh --output-format conll %s' % inputFileName
out = check_output(command.split())
#
#
###########################################################

# Extracting the predicted pos tag for each token
# (removing confidence scores)

tokenized = []
currSent = []
for line in out.split('\n'):
    if len(line):
        currSent.append(line.split('\t')[:2])
    elif len(currSent):
        tokenized.append(currSent)
        currSent = []

# Generating token list for LIDF model, to detect language
tokens = []

for tweet in tokenized:
    tokens.append([])
    for token in tweet:
        tokens[-1].append([token[0]])

############# Running LIDF model ############################
#
#
command  = ['python', os.environ['HINGLISH_ROOT_DIR'] + '/lidf/demo.py', str(tokens)]
out = ast.literal_eval(check_output(command))
#
#
#############################################################

# Preparing data for NER model
for i in range(len(tokens)):
    for j in range(len(tokens[i])):
        tokens[i][j].append(out[i][j][-1]) # add language tag
        tokens[i][j].append(tokenized[i][j][1]) # add epos

X_test = [sent2features(s) for s in tokens]

########### Running NER Model ##############
#
#
tagger = pycrfsuite.Tagger()
tagger.open(os.environ['HINGLISH_ROOT_DIR'] + '/ner/models/nerModel')
y_pred = []
for xseq in X_test:
    y_pred.append(tagger.tag(xseq))
#
#
############################################

for i in range(len(tokens)):
    for j in range(len(tokens[i])):
        tokens[i][j].append(y_pred[i][j])
        print tokens[i][j]
    print '\n'
