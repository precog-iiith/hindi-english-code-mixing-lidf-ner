import ast
import subprocess

# Tokenised text
text = [['mee'], ['too'], ['but'], ['aaj'], ['jaldi'], ['chalke'], ['dekhte'], ['hai'], [':P']]

devanagariChars   = [u'\u0900', u'\u0901', u'\u0902', u'\u0903', u'\u0904', u'\u0905', u'\u0906', u'\u0907', u'\u0908', u'\u0909', u'\u090a', u'\u090b', u'\u090c', u'\u090d', u'\u090e', u'\u090f', u'\u0910', u'\u0911', u'\u0912', u'\u0913', u'\u0914', u'\u0915', u'\u0916', u'\u0917', u'\u0918', u'\u0919', u'\u091a', u'\u091b', u'\u091c', u'\u091d', u'\u091e', u'\u091f', u'\u0920', u'\u0921', u'\u0922', u'\u0923', u'\u0924', u'\u0925', u'\u0926', u'\u0927', u'\u0928', u'\u0929', u'\u092a', u'\u092b', u'\u092c', u'\u092d', u'\u092e', u'\u092f', u'\u0930', u'\u0931', u'\u0932', u'\u0933', u'\u0934', u'\u0935', u'\u0936', u'\u0937', u'\u0938', u'\u0939', u'\u093a', u'\u093b', u'\u093c', u'\u093d', u'\u093e', u'\u093f', u'\u0940', u'\u0941', u'\u0942', u'\u0943', u'\u0944', u'\u0945', u'\u0946', u'\u0947', u'\u0948', u'\u0949', u'\u094a', u'\u094b', u'\u094c', u'\u094d', u'\u094e', u'\u094f', u'\u0950', u'\u0951', u'\u0952', u'\u0953', u'\u0954', u'\u0955', u'\u0956', u'\u0957', u'\u0958', u'\u0959', u'\u095a', u'\u095b', u'\u095c', u'\u095d', u'\u095e', u'\u095f', u'\u0960', u'\u0961', u'\u0962', u'\u0963', u'\u0964', u'\u0965', u'\u0966', u'\u0967', u'\u0968', u'\u0969', u'\u096a', u'\u096b', u'\u096c', u'\u096d', u'\u096e', u'\u096f', u'\u0970', u'\u0971', u'\u0972', u'\u0973', u'\u0974', u'\u0975', u'\u0976', u'\u0977', u'\u0978', u'\u0979', u'\u097a', u'\u097b', u'\u097c', u'\u097d', u'\u097e', u'\u097f']
englishCharacters = [u'a', u'b', u'c', u'd', u'e', u'f', u'g', u'h', u'i', u'j', u'k', u'l', u'm', u'n', u'o', u'p', u'q', u'r', u's', u't', u'u', u'v', u'w', u'x', u'y', u'z']


with open('./transliterationModel/englishMap', 'r') as fp:
    EnglishMap = fp.read()
    EnglishMap = ast.literal_eval(EnglishMap)

    revEnglishMap = [0 for i in range(len(EnglishMap))]
    for key in EnglishMap:
        revEnglishMap[EnglishMap[key]] = key
        
with open('./transliterationModel/hindiMap', 'r') as fp:
    HindiMap = fp.read()
    HindiMap = ast.literal_eval(HindiMap)

    revHindiMap = [0 for i in range(len(HindiMap))]
    for key in HindiMap:
        revHindiMap[HindiMap[key]] = key

print 'Encoding and writing to file'

for i in range(len(text)):

    cleanText = ''.join([ch for ch in text[i][0].lower() if ch in EnglishMap])
    englishEncoding = [str(EnglishMap[ch]) for ch in cleanText]
    text[i] += [cleanText, englishEncoding] 

fp = open('wordsToTransliterate.txt', 'w')
for token in text:
    englishEncoding = token[2]
    if len(englishEncoding) != 0:
        fp.write(' '.join(englishEncoding) + '\n')
fp.close()

print 'Running transliteration script'

##################################################################
#
#	Run Transliteration model (bash script pred.sh)
#
process = subprocess.Popen('bash pred.sh ./transliterationModel/ wordsToTransliterate.txt wordsTransliterated.txt ./transliterationModel/model.ckpt-66053', shell=True, stdout=subprocess.PIPE)
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

for i in range(len(text)):
    englishEncoding = text[i][2]
    if len(englishEncoding) != 0:
        text[i] += [transliteratedEncoding[mark], transliteratedText[mark]]
        mark += 1
    else:
        text[i] += [[], ""]

print 'Original       :', ' '.join(map(lambda x : x[0], text))
print 'Cleaned        :', ' '.join(map(lambda x : x[1], text))
print 'Transliterated :', ' '.join(map(lambda x : x[4], text))


for i in text:
    print i
