import ast
import subprocess
import editdistance

# Tokenised list of tweets (3 dimensional)

allTweets = \
[
 [
  ['mee'],
  ['too'],
  ['but'],
  ['aaj'],
  ['jaldi'],
  ['chalke'],
  ['dekhte'],
  ['hai'],
  [':P']
 ],  \
 
 [
  ['Call'],
  ['kar'],
  ['leti'],
  ['hoon']
 ], \
 [
  ['Light'],
  ['hai'],
  ['abhi'],
  [','],
  ["I'll"],
  ['try'],
  ['attending'],
  ['one'],
  ['myself'],
  ['.']
 ],
 [
  ['they'], ['have'], ['night'], ['built'], ['what'], ['what'], ['has'], ['pagal']
 ],
[['they'], ['karega'], ['that'], ['built'], ['nhi']]
]


# Encoding for transliteration

devanagariChars   = [u'\u0900', u'\u0901', u'\u0902', u'\u0903', u'\u0904', u'\u0905', u'\u0906', u'\u0907', u'\u0908', u'\u0909', u'\u090a', u'\u090b', u'\u090c', u'\u090d', u'\u090e', u'\u090f', u'\u0910', u'\u0911', u'\u0912', u'\u0913', u'\u0914', u'\u0915', u'\u0916', u'\u0917', u'\u0918', u'\u0919', u'\u091a', u'\u091b', u'\u091c', u'\u091d', u'\u091e', u'\u091f', u'\u0920', u'\u0921', u'\u0922', u'\u0923', u'\u0924', u'\u0925', u'\u0926', u'\u0927', u'\u0928', u'\u0929', u'\u092a', u'\u092b', u'\u092c', u'\u092d', u'\u092e', u'\u092f', u'\u0930', u'\u0931', u'\u0932', u'\u0933', u'\u0934', u'\u0935', u'\u0936', u'\u0937', u'\u0938', u'\u0939', u'\u093a', u'\u093b', u'\u093c', u'\u093d', u'\u093e', u'\u093f', u'\u0940', u'\u0941', u'\u0942', u'\u0943', u'\u0944', u'\u0945', u'\u0946', u'\u0947', u'\u0948', u'\u0949', u'\u094a', u'\u094b', u'\u094c', u'\u094d', u'\u094e', u'\u094f', u'\u0950', u'\u0951', u'\u0952', u'\u0953', u'\u0954', u'\u0955', u'\u0956', u'\u0957', u'\u0958', u'\u0959', u'\u095a', u'\u095b', u'\u095c', u'\u095d', u'\u095e', u'\u095f', u'\u0960', u'\u0961', u'\u0962', u'\u0963', u'\u0964', u'\u0965', u'\u0966', u'\u0967', u'\u0968', u'\u0969', u'\u096a', u'\u096b', u'\u096c', u'\u096d', u'\u096e', u'\u096f', u'\u0970', u'\u0971', u'\u0972', u'\u0973', u'\u0974', u'\u0975', u'\u0976', u'\u0977', u'\u0978', u'\u0979', u'\u097a', u'\u097b', u'\u097c', u'\u097d', u'\u097e', u'\u097f']
englishCharacters = [u'a', u'b', u'c', u'd', u'e', u'f', u'g', u'h', u'i', u'j', u'k', u'l', u'm', u'n', u'o', u'p', u'q', u'r', u's', u't', u'u', u'v', u'w', u'x', u'y', u'z']

maxlen = 30

with open('../transliteration/transliterationModel/englishMap', 'r') as fp:
    EnglishMap = fp.read()
    EnglishMap = ast.literal_eval(EnglishMap)

    revEnglishMap = [0 for i in range(len(EnglishMap))]
    for key in EnglishMap:
        revEnglishMap[EnglishMap[key]] = key
        
with open('../transliteration/transliterationModel/hindiMap', 'r') as fp:
    HindiMap = fp.read()
    HindiMap = ast.literal_eval(HindiMap)

    revHindiMap = [0 for i in range(len(HindiMap))]
    for key in HindiMap:
        revHindiMap[HindiMap[key]] = key

for i in range(len(allTweets)):
    for j in range(len(allTweets[i])):
        
        # Create english encoding of clean text
        cleanText = ''.join([ch for ch in allTweets[i][j][0].lower() if ch in EnglishMap])
        englishEncoding = [str(EnglishMap[ch]) for ch in cleanText]
        allTweets[i][j] += [cleanText, englishEncoding]


tweetID = 0

print 'Original       :', ' '.join(map(lambda x : x[0], allTweets[tweetID]))
print 'Cleaned        :', ' '.join(map(lambda x : x[1], allTweets[tweetID]))

fp = open('wordsToTransliterate.txt', 'w')

for tweet in allTweets:
    for token in tweet:
        englishEncoding = token[2]
        if len(englishEncoding) != 0:
            fp.write(' '.join(englishEncoding) + '\n')

fp.close()

print 'Running transliteration script'

##################################################################
#
#	Run Transliteration model (bash script pred.sh)
#
process = subprocess.Popen('bash ../transliteration/pred.sh ../transliteration/transliterationModel/ wordsToTransliterate.txt wordsTransliterated.txt ../transliteration/transliterationModel/model.ckpt-66053', shell=True, stdout=subprocess.PIPE)
process.wait()
#
##################################################################

print 'Finished running transliteration script'

with open('wordsTransliterated.txt', 'r') as fp:
    transliteratedEncoding = fp.readlines()

transliteratedText  = []

for i in range(len(transliteratedEncoding)):
    transliteratedEncoding[i] = transliteratedEncoding[i].strip('\n').split(' ')
    string = ''
    for ch in transliteratedEncoding[i]:
        if ch != '':
            string += devanagariChars[int(ch)]
    transliteratedText.append(string)
    
mark = 0

for i in range(len(allTweets[:])):
    for j in range(len(allTweets[i])):
        englishEncoding = allTweets[i][j][2]
        if len(englishEncoding) != 0:
            allTweets[i][j] += [transliteratedEncoding[mark], transliteratedText[mark]]
            mark += 1
        else:
            allTweets[i][j] += [[], ""]

tweetID = 2

print 'Original       :', ' '.join(map(lambda x : x[0], allTweets[tweetID]))
print 'Cleaned        :', ' '.join(map(lambda x : x[1], allTweets[tweetID]))
print 'Transliterated :', ' '.join(map(lambda x : x[4], allTweets[tweetID]))



############################# Using language models

import numpy as np
import ast
import sys
import gc
import joblib

import keras.layers
from keras.models import Sequential
from keras.layers import Dense, Activation, BatchNormalization
from keras.layers import LSTM
from keras.optimizers import RMSprop, Adam

def getEnglishModel(rev = False):
    model = Sequential()

    model.add(LSTM(128, input_shape = (maxlen, len(EnglishMap)), return_sequences = True))
    if rev == True:
        model.add(Activation('relu'))
        model.add(BatchNormalization())
    else:
        model.add(BatchNormalization())
        model.add(Activation('relu'))
        
    model.add(keras.layers.Dropout(0.7))

    model.add(LSTM(128))
    if rev == True:
        model.add(Activation('relu'))
        model.add(BatchNormalization())
    else:
        model.add(BatchNormalization())
        model.add(Activation('relu'))
    model.add(keras.layers.Dropout(0.7))

    model.add(Dense(64))
    if rev == True:
        model.add(Activation('relu'))
        model.add(BatchNormalization())
    else:
        model.add(BatchNormalization())
        model.add(Activation('relu'))
    model.add(keras.layers.Dropout(0.7))

    model.add(Dense(len(EnglishMap)))
    model.add(Activation('softmax'))

    return model

def getHindiModel(rev = False):
    model = Sequential()
    
    model.add(LSTM(128, input_shape = (maxlen, len(HindiMap)), return_sequences = True))
    if rev == True:
        model.add(Activation('relu'))
        model.add(BatchNormalization())
    else:
        model.add(BatchNormalization())
        model.add(Activation('relu'))
    model.add(keras.layers.Dropout(0.7))

    model.add(LSTM(128))
    if rev == True:
        model.add(Activation('relu'))
        model.add(BatchNormalization())
    else:
        model.add(BatchNormalization())
        model.add(Activation('relu'))
    model.add(keras.layers.Dropout(0.7))

    model.add(Dense(64))
    if rev == True:
        model.add(Activation('relu'))
        model.add(BatchNormalization())
    else:
        model.add(BatchNormalization())
        model.add(Activation('relu'))
    model.add(keras.layers.Dropout(0.7))

    model.add(Dense(len(HindiMap)))
    model.add(Activation('softmax'))

    return model

##### Load weights

hindiModel = getHindiModel(rev = True)
englishModel = getEnglishModel(rev = True)

hindiModelFile   = 'models/lm_hi_99_rev'
englishModelFile = 'models/lm_en_99_rev'

hindiModel.load_weights(hindiModelFile)
englishModel.load_weights(englishModelFile)


romanTokens = []
devanagariTokens = []

for tweet in allTweets:
    for token in tweet:
        if len(token[2]):
            romanTokens.append(token[2])
            devanagariTokens.append(token[3])

try:
    del romanIn
except:
    pass

try:
    del devanagiriIn
except:
    pass

romanIn = np.zeros((len(romanTokens), maxlen, len(EnglishMap)))
devanagiriIn = np.zeros((len(devanagariTokens), maxlen, len(HindiMap)))

print "Encoding ..."
sys.stdout.flush()

for j in range(len(romanTokens)):
    for k in range(len(romanTokens[j]) - 1):
        romanIn[j, k, int(romanTokens[j][k])] = 1
        
for j in range(len(devanagariTokens)):
    for k in range(len(devanagariTokens[j]) - 1):
        devanagiriIn[j, k, int(devanagariTokens[j][k])] = 1

englishProbabilities = englishModel.predict_proba(romanIn, batch_size = 1024)
hindiProbabilities  = hindiModel.predict_proba(devanagiriIn, batch_size = 1024)

mark = 0

for i in range(len(allTweets)):
    for j in range(len(allTweets[i])):
        if len(allTweets[i][j][2]):
            allTweets[i][j].append(englishProbabilities[mark].tolist())
            allTweets[i][j].append(hindiProbabilities[mark].tolist())
            mark += 1
        else:
            allTweets[i][j].append(np.zeros_like(englishProbabilities[0]))
            allTweets[i][j].append(np.zeros_like(hindiProbabilities[0]))

# 0 -> Original Token
# 1 -> Clean token
# 2 -> Roman encoding
# 3 -> Devanagiri encoding
# 4 -> Hindi word
# 5 -> englishProbs
# 6 -> hindiProbs

numOtherFeatures = 4


def probFeatureExtractor(token):
    
    # 26 eng + 128 hin + 3 others
    
    features = np.concatenate((token[5], token[6])).tolist()
    
    return features
    
def otherFeatureExtractor(token):
    
    # other features
    features = []
    
    # 1. Fraction of chars removed after cleaning
    features.append((len(token[0]) - len(token[1])) / float(len(token[0])))
    
    # 2. Editdistance bw original and clean token
    features.append(float(editdistance.eval(token[0], token[1].lower())) / len(token[0]))
    
    # 3. First letter capitalised or not
    if token[0][0].isupper():
        features.append(1)
    else:
        features.append(0)

    # 4. Percentage of capitalised letters
    capCount = 0.
    for ch in token[0][0]:
        if ch.isupper():
            capCount += 1.
    features.append(capCount / len(token[0]))

    return features


X = []

for tweet in allTweets:
    for j in range(len(tweet)):
        token = tweet[j]
        
        currFeature = probFeatureExtractor(token)
        
        if j == 0:
            prevFeature = np.zeros_like(currFeature)
        else:
            prevFeature = probFeatureExtractor(tweet[j - 1])
        
        if j == (len(tweet) - 1):
            nextFeature = np.zeros_like(currFeature)
        else:
            nextFeature = probFeatureExtractor(tweet[j + 1])
        
        otherFeatures = otherFeatureExtractor(token)
        
        feature = np.concatenate((currFeature, otherFeatures))
        X.append(feature)

X = np.array(X)


############# LIDF model

lidf = Sequential()

lidf.add(Dense(256, input_shape = X.shape[1:]))
lidf.add(Activation('relu'))
lidf.add(keras.layers.BatchNormalization())
lidf.add(keras.layers.Dropout(0.5))

lidf.add(Dense(128))
lidf.add(Activation('relu'))
lidf.add(keras.layers.BatchNormalization())
lidf.add(keras.layers.Dropout(0.5))

lidf.add(Dense(64))
lidf.add(Activation('relu'))
lidf.add(keras.layers.BatchNormalization())
lidf.add(keras.layers.Dropout(0.5))

lidf.add(Dense(32))
lidf.add(Activation('relu'))
lidf.add(keras.layers.BatchNormalization())
lidf.add(keras.layers.Dropout(0.5))

lidf.add(Dense(3))
lidf.add(Activation('softmax'))

lidf.load_weights('./models/lidfModel.h5')
opt = keras.optimizers.Adam(lr = 0.0005)
lidf.compile(loss = 'categorical_crossentropy', optimizer = opt)

classMap = {0: 'hi', 1 : 'en', 2 : 're'}


modelPred = lidf.predict_classes(X)
lidfOutput = []

mark = 0
for tweet in allTweets:
    currResults = []
    for token in tweet:
        currResults.append([token[0], classMap[modelPred[mark]]])
        mark += 1
    lidfOutput.append(currResults)

print lidfOutput
