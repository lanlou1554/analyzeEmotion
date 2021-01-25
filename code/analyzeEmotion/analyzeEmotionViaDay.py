import xlrd
import xlwt
import pickle
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
import jieba
import pandas as pd
import pickle


class TextClassifier():

    def __init__(self, classifier=MultinomialNB()):
        self.classifier = classifier
        self.vectorizer = CountVectorizer(analyzer='word', ngram_range=(1,4), max_features=20000)

    def features(self, X):
        return self.vectorizer.transform(X)

    def fit(self, X, y):
        self.vectorizer.fit(X)
        self.classifier.fit(self.features(X), y)

    def predict(self, x):
        return self.classifier.predict(self.features([x]))

    def score(self, X, y):
        return self.classifier.score(self.features(X), y)

def convertToJIEA(line,isJudgeEmotion):
    stopwords = pd.read_csv(r"D:\study\NLP_project\NLP_project\data\stopwords.txt", index_col=False, quoting=3,
                            sep="\t", names=['stopword'], encoding='utf-8')
    stopwords = stopwords['stopword'].values
    stopwordsEmotion = pd.read_csv(r"D:\study\NLP_project\NLP_project\data\停用词.txt", index_col=False, quoting=3,
                            sep="\t", names=['stopword'], encoding='utf-8')
    stopwordsEmotion = stopwordsEmotion['stopword'].values
    segs=jieba.lcut(line)
    segs = filter(lambda x:len(x)>0, segs)
    if isJudgeEmotion:
        segs = filter(lambda x:x not in stopwordsEmotion, segs)
    else:
        segs = filter(lambda x:x not in stopwords, segs)
    return " ".join(segs)

def predictEmotion(lines,model):
    return predictAnything(lines,model,True)


def predictAnything(lines,c,isEmotion):
    convertLines = []
    for line in lines:
        convertLines.append(convertToJIEA(line,isJudgeEmotion=isEmotion))

    res = []
    for l in convertLines:
        res.append(c.predict(str(l))[0])
    return res


def readData(path):
    data = []
    with open(path, 'rb') as file:
        data = pickle.loads(file.read())
    return data


def countEmotionWeibo(data,model):
    res = []
    for d in data:
        angry = 0
        grateful = 0
        optimistic = 0
        rational = 0
        uneasy = 0
        tempRes = [d[0]]
        tag = predictEmotion(d[1],model)
        for t in tag:
            if t == 'angry':
                angry = angry+1
            if t == 'grateful':
                grateful = grateful+1
            if t == 'optimistic':
                optimistic = optimistic+1
            if t == 'rational':
                rational = rational+1
            if t == 'uneasy':
                uneasy = uneasy+1
        total = angry + grateful + optimistic + rational + uneasy
        tempAnaPercent = [angry/total,grateful/total,optimistic/total,rational/total,uneasy/total]
        tempRes.append(tempAnaPercent)
        res.append(tempRes)
    return res

def countEmotionBilibili(data,model):
    res = []
    for d in data:
        angry = 0
        grateful = 0
        optimistic = 0
        rational = 0
        uneasy = 0
        tempRes = [d[0]]

        likeNum = []
        comments = []
        for dd in d[1]:
            likeNum.append(dd[0])
            comments.append(dd[1])
        tag = predictEmotion(comments,model)

        for i in range(len(tag)):
            if tag[i] == 'angry':
                angry = angry+likeNum[i]
            if tag[i] == 'grateful':
                grateful = grateful+likeNum[i]
            if tag[i] == 'optimistic':
                optimistic = optimistic+likeNum[i]
            if tag[i] == 'rational':
                rational = rational+likeNum[i]
            if tag[i] == 'uneasy':
                uneasy = uneasy+likeNum[i]
        total = angry + grateful + optimistic + rational + uneasy
        tempAnaPercent = [angry/total,grateful/total,optimistic/total,rational/total,uneasy/total]
        tempRes.append(tempAnaPercent)
        res.append(tempRes)
    return res

def savedata(path,data):
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)

    sheet = book.add_sheet("dayEmotionPerc",cell_overwrite_ok=True)

    col = ("日期","angry","grateful","optimistic","rational","uneasy")

    for i in range(len(col)):
        sheet.write(0,i,col[i])
        for j in range(1,len(data)+1):
            sheet.write(j,0,str(data[j-1][0]))
            for k in range(5):
                sheet.write(j,k+1,str(data[j-1][1][k]))

    book.save(path)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # model = TextClassifier()
    # with open(r"model\predictStage123Emotion.pkl", 'rb') as file:
    #     model = pickle.loads(file.read())
    # dataBilibili = readData(r"tempPKL/cutIntoDayArrayBilibili.pkl")
    # dataWeibo = readData(r"tempPKL/cutIntoDayArrayWeibo.pkl")
    # resBilibili = countEmotionBilibili(dataBilibili,model)
    # resWeibo = countEmotionWeibo(dataWeibo,model)
    # for rw in resWeibo:
    #     for rb in resBilibili:
    #         if rw[0] == rb[0]:
    #             for i in range(5):
    #                 rb[1][i] = (rb[1][i]+rw[1][i])/2
    #             break
    # output = open(r"result\dayEmotionPerc.pkl", 'wb')
    # temp = pickle.dumps(resBilibili)
    # output.write(temp)
    # output.close()
    resBilibili = []
    with open(r"../../result/dayEmotionPerc.pkl", 'rb') as file:
        resBilibili = pickle.loads(file.read())
    print(resBilibili)
    savedata(r"../../result/dayEmotionPerc.xls", resBilibili)

