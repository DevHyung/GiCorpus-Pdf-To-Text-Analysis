# -*-encoding:utf8-*-
import nltk
from nltk import *
import os
import codecs
from nltk.corpus import *
from urllib import urlopen
import requests
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
from nltk.corpus import swadesh
from nltk.corpus import conll2000
import sys
from docx import opendocx, getdocumenttext
import pdfminer
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager, rc
from matplotlib import style
style.use('ggplot')
import re
p = re.compile('[,;:.]+')
corpus_root = os.getcwd() + "/GICorpus2"
#filenames = ['gni-1-1-1.pdf', 'gni-1-1-7.pdf', 'gni-1-1-20.pdf', 'gni-1-1-32.pdf', 'gni-1-2-65.pdf']
#GIJournals = ['gni-1-1-1.pdf', 'gni-1-1-7.pdf']
GIJournals = ['gni-1-1-1.pdf', 'gni-1-1-7.pdf', 'gni-1-1-20.pdf', 'gni-1-1-32.pdf', 'gni-1-2-65.pdf']

def preprocessGICorpus():
    giCorpus = {}
    corpus_root = os.getcwd() + "/GICorpus/"

    filelists = PlaintextCorpusReader(corpus_root, '.*\.txt', encoding='utf-8')
    wnl = nltk.WordNetLemmatizer()
    print filelists.fileids()
    for file in filelists.fileids():
        wordlist = filelists.words(file)
        print "Printing size of  " + file + " original wordlist: " + str(len(wordlist))
        trimmedWordlist = [x for x in wordlist if not (x in swadesh.words('en')) and len(x) >= 1]
        # lemmatizedWordlist = [wnl.lemmatize(t) for t in trimmedWordlist]
        taggedWordlist = nltk.pos_tag(trimmedWordlist)
        print "Printing size of  " + file + " trimmed wordlist: " + str(len(trimmedWordlist))
        giCorpus[file] = taggedWordlist
        # fd = FreqDist(w for w in taggedWordlist)
    return giCorpus
#############
print sys.getdefaultencoding()

def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    str = retstr.getvalue()
    retstr.close()
    return str

def document_to_text(filename, file_path):
    if filename[-4:] == ".doc":
        cmd = ['antiword', file_path]
        p = Popen(cmd, stdout=PIPE)
        stdout, stderr = p.communicate()
        return stdout.decode('ascii', 'ignore')
    elif filename[-5:] == ".docx":
        document = opendocx(file_path)
        paratextlist = getdocumenttext(document)
        newparatextlist = []
        for paratext in paratextlist:
            newparatextlist.append(paratext.encode("utf-8"))
        return '\n\n'.join(newparatextlist)
    elif filename[-4:] == ".pdf":
        return convert_pdf_to_txt(file_path)


print "1. Converting PDF Files into TXT files.................."
ocrPDFJournalList = []
textPDFJournalList = []


def convertPDFIntoTXT(ocrPDFJournalList, textPDFJournalList):
    for fileName in GIJournals:
        print "converting " + fileName + " into txt..."
        fileString = document_to_text(fileName, corpus_root + "/" + fileName)

        if len(fileString) < 100:
            print fileName + ": " + str(len(fileString))
            ocrPDFJournalList += [fileName]
        else:
            print fileName + ": " + str(len(fileString))
            textPDFJournalList += [fileName]
            #text_file = open("GICorpus/"+fileName.split('.')[0]+'.txt', "w")
            #text_file.write(fileString)
            #text_file.close()
    return (ocrPDFJournalList, textPDFJournalList)


convertPDFIntoTXT(ocrPDFJournalList, textPDFJournalList)

print ocrPDFJournalList
print textPDFJournalList
#############

print "2. Preprocessing GICorpus .................."
giCorpus = preprocessGICorpus()


print "3. Analysis of Frequent Frequency Distribution ................"
allWordLists = []
for key in giCorpus.keys():
    allWordLists += giCorpus[key]
#print allWordLists
fdAllWords = FreqDist(w for w in allWordLists)


####### "4. Applying RE-based Basic NP Chunker .................."
# same expr. in generator expression
def extractWordListofCategory(wordTagValList, myVal, myTag):
    giAllWordList2 = ((val, word, tag) for ((word, tag), val) in fdAllWords.items() if myVal > 10 and myTag == 'NN')
    return sorted(giAllWordList2)

"""
def findNPChunk():
    grammar = r'''
    NP: {<DT|PP\$>?<JJ>*<NN>} # chunk determiner/possessive, adjectives and nouns
    {<NNP>+} # chunk sequences of proper nouns
    '''
    cp = nltk.RegexpParser(grammar)

    #for file in giCorpus.keys():
        #print file + ": ",
        #print cp.parse(giCorpus[file])
    giAllWordList = []
    for file in giCorpus.keys():
        giAllWordList += giCorpus[file]
    fdAllWords = FreqDist(w for w in giAllWordList)

    for ((word, tag), val) in fdAllWords.items():
        if val > 10 and tag == 'NN':
            print (word, val,tag)
"""
versionList = {}
titleList = {}
nameList = {}
careerList = {}
keyWordList = {}
keyWordCountlist = {}
mywordlist = []
mywordCountList = {}
with open("word.txt",'r') as f:
    txt = f.read()
    mywordlist=txt.split(',')
def extractInfo():
    corpus_root = os.getcwd() + "/GICorpus/"
    filelists = PlaintextCorpusReader(corpus_root, '.*\.txt', encoding='utf-8')
    print filelists.fileids()
    figureidx = 1
    for file in filelists.fileids():
        tmplist = []
        tmplist2 = []
        with open(corpus_root + file, 'r') as f:
            txt = f.read()
            # 키워드 뽑는
            keyword = txt.split("Keywords:")[1].split('\n\n')[0]
            keyword = re.sub('\n', '', keyword)
            m = p.split(keyword)
            keyWordList[file] = m
            for tmp in keyWordList[file]:
                if str(tmp) != ' ':
                    cnt = txt.count(str(tmp).strip())
                    tmplist.append(cnt)
                else:
                    keyWordList[file].remove(tmp)
            keyWordCountlist[file] = tmplist
            for tmp in mywordlist:
                cnt = txt.count(tmp.strip())
                tmplist2.append(cnt)
            mywordCountList[file] = tmplist2
            # 기본정보 뽑기

            infoarea = txt.split('\n\n')[:7]
            if infoarea[0].find('Minireview') != -1:
                ver = infoarea[1]
                startidx = 1
            else:
                ver = infoarea[0]
                startidx = 0
            startidx += 1
            title = infoarea[startidx]
            startidx += 1
            name = infoarea[startidx]
            name = re.sub('[^a-zA-Z\\s]', '', name)
            startidx += 1
            idx = startidx
            for tmp in infoarea[startidx:]:
                if tmp in "Abstract " or tmp in "Introduction ":
                    break;
                idx +=1
            career = infoarea[idx-1]
            print "_"*20
            print "파일 :",file
            print "문서 :",ver
            print "제목 :",title
            print "저자 :",name
            print "경력 :",career
            print "_" * 20
            versionList[file] = ver
            titleList[file] = title
            nameList[file] = name
            careerList[file] = career
            #print infoarea
        fig = plt.figure(figureidx,figsize=(12, 8))
        figureidx+=1
        ax = fig.add_subplot(111)
        pos = np.arange(len(keyWordList[file]))
        rects = plt.bar(pos, keyWordCountlist[file], align='center', width=0.5)
        plt.xticks(pos, keyWordList[file])
        for i, rect in enumerate(rects):
            ax.text(rect.get_x() + rect.get_width() / 2.0, 0.95 * rect.get_height(), str(keyWordCountlist[file][i]),ha='center')
        plt.xlabel(file)
    print "단어 :"
    for idx in range(0, len(mywordlist)):
        for file in filelists.fileids():
             print mywordlist[idx].strip(), " => ", file, "논문에서 ",mywordCountList[file][idx], "번"
print "4. Analysis .................."
extractInfo()
plt.show()
print keyWordList
print keyWordCountlist
#print mywordlist
#print mywordCountList
#findNPChunk()

# convertGIJournalsIntoText()
