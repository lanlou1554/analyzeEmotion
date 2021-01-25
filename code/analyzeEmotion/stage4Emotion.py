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
    return predictAnything(r"D:\study\final\model\predictRelativeTemp.pkl",lines,False)

def predictCountry(lines):
    return predictAnything(r"D:\study\final\model\predicCountry.pkl",lines,False)

def predictAbroadEmotion(lines):
    return predictAnything(r"D:\study\final\model\predictAbroadEmotion.pkl", lines,True)

def predictDomesticEmotion(lines):
    return predictAnything(r"D:\study\final\model\predictDomesticEmotion.pkl", lines,True)

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


def readData(path):
    workbook = xlrd.open_workbook(path)

    sheets = workbook.sheets()
    content = []
    likeNum = []
    titles = []
    for sheet in sheets:
        title = sheet.cell_value(1,1)
        rowNum = sheet.nrows
        for i in range(3,rowNum):
            content.append(sheet.cell_value(i,1))
            likeNum.append(int(sheet.cell_value(i,0)))
            titles.append(title)
    return content,likeNum,titles

def filterIrrelative(content,likeNum,titles):
    filteredContentWithTitles = []
    filteredContentWithoutTitles = []
    filteredLikeNum = []
    tag = predictRelative(content)
    for i in range(len(tag)):
        if tag[i] == 'relative':
            filteredLikeNum.append(likeNum[i])
            filteredContentWithTitles.append(content[i]+str(titles[i]))
            filteredContentWithoutTitles.append(content[i])
    return filteredContentWithTitles,filteredContentWithoutTitles,filteredLikeNum

def filterCountry(contentWithTitles,contentWithoutTitles,likeNum):
    abroadContent = []
    abroadLikeNum = []
    domesticContent = []
    domesticLikeNum = []
    #tag = predictCountry(contentWithTitles)
    tag = predictCountry(contentWithoutTitles)
    for i in range(len(tag)):
        if tag[i] == 'abroad':
            abroadContent.append(contentWithoutTitles[i])
            abroadLikeNum.append(likeNum[i])
        if tag[i] == 'domestic':
            domesticContent.append(contentWithoutTitles[i])
            domesticLikeNum.append(likeNum[i])
    return abroadContent,abroadLikeNum,domesticContent,domesticLikeNum

def countAbroadEmotion(content,likeNum):
    negative = 0
    neutral = 0
    pray_for_blessing = 0
    tag = predictAbroadEmotion(content)
    for i in range(len(tag)):
        if tag[i] == 'abroad-negative':
            negative = negative + int(likeNum[i])
        if tag[i] == 'abroad-neutral':
            neutral = neutral + int(likeNum[i])
        if tag[i] == 'abroad-prey_for_blessing':
            pray_for_blessing = pray_for_blessing + int(likeNum[i])
    total = neutral + negative + pray_for_blessing
    return negative/total,neutral/total,pray_for_blessing/total

def countDomesticEmotion(content,likeNum):
    neutral = 0
    positive = 0
    salute = 0
    tag = predictDomesticEmotion(content)
    for i in range(len(tag)):
        if tag[i] == 'domestic-neutral':
            neutral = neutral + int(likeNum[i])
        if tag[i] == 'domestic-positive':
            positive = positive + int(likeNum[i])
        if tag[i] == 'domestic-salute':
            salute = salute + int(likeNum[i])
    total = neutral + positive + salute
    return neutral/total,positive/total,salute/total


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    content,likeNum,titles = readData(r"b站评论——阶段4.xlsx")
    # content = []
    # with open(r"stageComment\pkl\stage4WB.pkl", 'rb') as file:
    #     content = pickle.loads(file.read())
    # likeNum = []
    # titles = []
    # for i in range(len(content)):
    #     likeNum.append(1)
    #     titles.append("")
    totalNum = len(content)
    contentWithTitle,contentWitoutTitle,likeNum = filterIrrelative(content,likeNum,titles)
    print("第四阶段weibo一共获取的评论数："+str(totalNum))
    print("相关评论数是："+str(len(contentWithTitle))+"  不相关评论数是："+str(totalNum-len(contentWithTitle)))
    abroadContent, abroadLikeNum, domesticContent, domesticLikeNum = filterCountry(contentWithTitle,contentWitoutTitle,likeNum)
    print("国外的评论数是："+str(len(abroadContent))+"  国内的评论数是："+str(len(domesticContent)))
    print("国外的情绪占比是：（负面-中立-祈福）")
    print(countAbroadEmotion(abroadContent,abroadLikeNum))

    # output = open("domesticContent.pkl", 'wb')
    # temp = pickle.dumps(domesticContent)
    # output.write(temp)
    # output.close()
    # output = open("domesticLikeNum.pkl", 'wb')
    # temp = pickle.dumps(domesticLikeNum)
    # output.write(temp)
    # output.close()

    # domesticContent = []
    # with open("domesticContent.pkl", 'rb') as file:
    #     domesticContent = pickle.loads(file.read())
    # domesticLikeNum = []
    # with open("domesticLikeNum.pkl", 'rb') as file:
    #     domesticLikeNum = pickle.loads(file.read())

    print("国内的情绪占比是：（中立-积极-致敬缅怀）")
    print(countDomesticEmotion(domesticContent,domesticLikeNum))





