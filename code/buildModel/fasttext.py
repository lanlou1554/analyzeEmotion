import jieba
import pickle
import pandas as pd
import random
import fasttext


# r"D:\study\final\stageComment\pkl\"
def readData(path):
    res = []
    with open(path, 'rb') as file:
        res = pickle.loads(file.read())
    return res
def mergeTwoLists(a,b):
    for item in b:
        a.append(item)
    return a

def preprocess_text(content_lines, sentences, category):
    stopwords = pd.read_csv(r"D:\study\NLP_project\NLP_project\data\stopwords.txt", index_col=False, quoting=3,
                            sep="\t", names=['stopword'], encoding='utf-8')
    stopwords = stopwords['stopword'].values
    for line in content_lines:
#         try:
#             segs=jieba.lcut(line)
#             segs = filter(lambda x:len(x)>0, segs)
#             #segs = filter(lambda x:x not in stopwords, segs)
#             sentences.append((" ".join(segs), category))
#         except Exception as e:
#             print(line)
#             continue
        segs=jieba.lcut(line)
        segs = filter(lambda x:len(x)>0, segs)
        segs = filter(lambda x:x not in stopwords, segs)
        sentences.append("__label__"+str(category)+" , "+" ".join(segs))


def predict():
    stage1 = mergeTwoLists(readData(r"D:\study\final\stageComment\pkl\stage1BL.pkl"),readData(r"D:\study\final\stageComment\pkl\stage1WB.pkl"))
    stage2 = mergeTwoLists(readData(r"D:\study\final\stageComment\pkl\stage2BL.pkl"),readData(r"D:\study\final\stageComment\pkl\stage2WB.pkl"))
    stage3 = mergeTwoLists(readData(r"D:\study\final\stageComment\pkl\stage3BL.pkl"),readData(r"D:\study\final\stageComment\pkl\stage3WB.pkl"))
    stage4 = mergeTwoLists(readData(r"D:\study\final\stageComment\pkl\stage4BL.pkl"),readData(r"D:\study\final\stageComment\pkl\stage4WB.pkl"))
    stage1 = stage1[:10000]
    stage2 = stage2[:10000]
    stage3 = stage3[:10000]
    stage4 = stage4[:10000]

    sentences = []

    preprocess_text(stage1, sentences, 'stage1')
    preprocess_text(stage2, sentences, 'stage2')
    preprocess_text(stage3, sentences, 'stage3')
    preprocess_text(stage4, sentences, 'stage4')
    random.shuffle(sentences)

    print("writing data to fasttext format...")
    out = open('train_data.txt', 'w')
    for sentence in sentences:
        out.write(str(sentence.encode('utf8') + b"\n"))
    print("done!")

    classifier = fasttext.supervised('train_data.txt', 'classifier.model', label_prefix='__label__')
    result = classifier.test('train_data.txt')
    print('P@1:', result.precision)
    print('R@1:', result.recall)
    print('Number of examples:', result.nexamples)

predict()