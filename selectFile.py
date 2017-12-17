#-*-encoding:utf8-*-

import re
import os
import codecs
import nltk
from nltk import *
from nltk.corpus import *
import matplotlib.pyplot as plt
import numpy as np
from docx import opendocx, getdocumenttext
import pdfminer
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO

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

def convertPDFIntoTXT():
    corpus_root = os.getcwd()
    print "현재 PDF 리스트 ::",
    GIJournals = os.listdir(corpus_root + "/GICorpus2/")
    for fileName in GIJournals:
        print "converting " + fileName + " into txt..."
        fileString = document_to_text(fileName, corpus_root + "/GICorpus2/" + fileName)

        if len(fileString) < 100:
            print fileName + ": " + str(len(fileString))

        else:
            print fileName + ": " + str(len(fileString))
            text_file = open("GICorpus/"+fileName.split('.')[0]+'.txt', "w")
            text_file.write(fileString)
            text_file.close()



if __name__=="__main__":
    convertPDFIntoTXT()
    corpus_root = os.getcwd()
    print "현재 파일리스트 ::",
    print (os.listdir(corpus_root+"/GICorpus/"))
    file = raw_input("파일명 입력 ::")
    f = open(corpus_root + "/GICorpus/"+file,'r')
    txt = f.read()
    # 키워드 뽑는
    keyword = txt.split("Keywords:")[1].split('\n\n')[0]
    keyword = re.sub('\n', '', keyword)

    tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
    lemmatizer = nltk.stem.WordNetLemmatizer()

    tokens = tokenizer.tokenize(keyword)
    lemmas = [lemmatizer.lemmatize(t) for t in tokens]
    fdist = nltk.FreqDist(lemmas)
    common = fdist.items()

    # 파일 가져오기
    corpus_root2 = os.getcwd() + "/GICorpus/"
    filelists2 = PlaintextCorpusReader(corpus_root2, file, encoding='utf-8')
    wordlist2 = filelists2.words(filelists2.fileids())
    trimmedWordlist2 = [x for x in wordlist2 if not (x in swadesh.words('en')) and len(x) > 1]
    tokens2 = tokenizer.tokenize(' '.join(trimmedWordlist2))
    lemmas2 = [lemmatizer.lemmatize(t) for t in tokens2]
    fdist2 = nltk.FreqDist(lemmas2)
    common2 = fdist2.items()

    keyword_count = {}
    cntlist = []
    wordlist = [ x[0] for x in common]

    for word in wordlist:
        idx = 0
        for target in common2:
            if target[0].lower() == word.lower():#찾음
                idx += target[1]

        cntlist.append(idx)
    keyword_count[file] = cntlist
    for i in range(0,len(common)):
        print common[i][0],keyword_count[file][i]
    fig = plt.figure(1, figsize=(12, 8))
    ax = fig.add_subplot(111)
    pos = np.arange(len(keyword_count[file]))
    rects = plt.bar(pos, keyword_count[file], align='center', width=0.5)
    plt.xticks(pos, wordlist)
    for i, rect in enumerate(rects):
        ax.text(rect.get_x() + rect.get_width() / 2.0, 0.95 * rect.get_height(), str(keyword_count[file][i]),
                ha='center')
    plt.xlabel(file)
    plt.show()