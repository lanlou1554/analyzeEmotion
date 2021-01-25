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

def predictRelative(lines):
    return predictAnything(r"D:\study\final\model\predictStage123Relative.pkl",lines,False)

def predictEmotion(lines):
    return predictAnything(r"D:\study\final\model\predictStage123Emotion.pkl", lines,True)

def predictAnything(modelPath,lines,isEmotion):
    convertLines = []
    for line in lines:
        convertLines.append(convertToJIEA(line,isJudgeEmotion=isEmotion))

    c = TextClassifier()
    with open(modelPath, 'rb') as file:
        c = pickle.loads(file.read())

    res = []
    for l in convertLines:
        res.append(c.predict(str(l))[0])
    return res



def filterIrrelative(content,likeNum):
    filteredContent = []
    filteredLikeNum = []
    tag = predictRelative(content)
    for i in range(len(tag)):
        if tag[i] == 'relative':
            filteredLikeNum.append(likeNum[i])
            filteredContent.append(content[i])
    return filteredContent,filteredLikeNum


def countEmotion(content,likeNum):
    angry = 0
    grateful = 0
    optimistic = 0
    rational = 0
    uneasy = 0

    tag = predictEmotion(content)

    for i in range(len(tag)):
        if tag[i] == 'angry':
            angry = angry + likeNum[i]
        if tag[i] == 'grateful':
            grateful = grateful + likeNum[i]
        if tag[i] == 'optimistic':
            optimistic = optimistic + likeNum[i]
        if tag[i] == 'rational':
            rational = rational + likeNum[i]
        if tag[i] == 'uneasy':
            uneasy = uneasy + likeNum[i]
    total = angry + grateful + optimistic + rational + uneasy
    return angry / total, grateful / total, optimistic / total, rational / total, uneasy / total


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #content,likeNum,titles = readData(r"b站评论——阶段4.xlsx")
    contentTemp = []
    with open(r"stageComment\pkl\stage4WB.pkl", 'rb') as file:
        contentTemp = pickle.loads(file.read())
    content = contentTemp
    likeNum = []
    for i in range(len(content)):
        likeNum.append(1)
    totalNum = len(content)
    contentlikeNum = filterIrrelative(content,likeNum)
    print("第四阶段b站一共获取的评论数："+str(totalNum))
    print("相关评论数是："+str(len(content))+"  不相关评论数是："+str(totalNum-len(content)))
    print("情绪占比是：（angry-grateful-optimistic-rational-uneasy）")
    print(countEmotion(content,likeNum))








