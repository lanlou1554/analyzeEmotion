from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import jieba
import pandas as pd
from sklearn.model_selection import train_test_split
import pickle
import argparse
import sys

import numpy as np
import pandas
from sklearn import metrics
import tensorflow as tf

learn = tf.contrib.learn

FLAGS = None

#文档最长长度
MAX_DOCUMENT_LENGTH = 100
#最小词频数
MIN_WORD_FREQUENCE = 2
#词嵌入的维度
EMBEDDING_SIZE = 20
#filter个数
N_FILTERS = 10
#感知野大小
WINDOW_SIZE = 20
#filter的形状
FILTER_SHAPE1 = [WINDOW_SIZE, EMBEDDING_SIZE]
FILTER_SHAPE2 = [WINDOW_SIZE, N_FILTERS]
#池化
POOLING_WINDOW = 4
POOLING_STRIDE = 2
n_words = 0

def cnn_model(features, target):
	"""
    2层的卷积神经网络，用于短文本分类
    """
	# 先把词转成词嵌入
	# 我们得到一个形状为[n_words, EMBEDDING_SIZE]的词表映射矩阵
	# 接着我们可以把一批文本映射成[batch_size, sequence_length, EMBEDDING_SIZE]的矩阵形式
	target = tf.one_hot(target, 15, 1, 0)
	word_vectors = tf.contrib.layers.embed_sequence(
			features, vocab_size=n_words, embed_dim=EMBEDDING_SIZE, scope='words')
	word_vectors = tf.expand_dims(word_vectors, 3)
	with tf.variable_scope('CNN_Layer1'):
		# 添加卷积层做滤波
		conv1 = tf.contrib.layers.convolution2d(
				word_vectors, N_FILTERS, FILTER_SHAPE1, padding='VALID')
		# 添加RELU非线性
		conv1 = tf.nn.relu(conv1)
		# 最大池化
		pool1 = tf.nn.max_pool(
				conv1,
				ksize=[1, POOLING_WINDOW, 1, 1],
				strides=[1, POOLING_STRIDE, 1, 1],
				padding='SAME')
		# 对矩阵进行转置，以满足形状
		pool1 = tf.transpose(pool1, [0, 1, 3, 2])
	with tf.variable_scope('CNN_Layer2'):
		# 第2个卷积层
		conv2 = tf.contrib.layers.convolution2d(
				pool1, N_FILTERS, FILTER_SHAPE2, padding='VALID')
		# 抽取特征
		pool2 = tf.squeeze(tf.reduce_max(conv2, 1), squeeze_dims=[1])

	# 全连接层
	logits = tf.contrib.layers.fully_connected(pool2, 15, activation_fn=None)
	loss = tf.losses.softmax_cross_entropy(target, logits)

	train_op = tf.contrib.layers.optimize_loss(
			loss,
			tf.contrib.framework.get_global_step(),
			optimizer='Adam',
			learning_rate=0.01)

	return ({
			'class': tf.argmax(logits, 1),
			'prob': tf.nn.softmax(logits)
	}, loss, train_op)


#构建数据集
#x_train = pandas.DataFrame(train_data)[1]
#y_train = pandas.Series(train_target)
#x_test = pandas.DataFrame(test_data)[1]
#y_test = pandas.Series(test_target)

def convertToList(temp):
    res = []
    for t in temp:
        res.append(t[0])
    return res

def preprocess_text(content_lines, sentences, category):
    stopwords = pd.read_csv(r"D:\study\NLP_project\NLP_project\data\停用词.txt", index_col=False, quoting=3, sep="\t",
                            names=['stopword'], encoding='utf-8')
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
        #segs = filter(lambda x:x not in stopwords, segs)
        sentences.append((" ".join(segs), category))


def readData(path):
	res = []
	with open(path, 'rb') as file:
		res = pickle.loads(file.read())
	return res

def getStageData(size):
	stage1 = mergeTwoLists(readData(r"D:\study\final\stageComment\pkl\stage1BL.pkl"),
						   readData(r"D:\study\final\stageComment\pkl\stage1WB.pkl"))
	stage2 = mergeTwoLists(readData(r"D:\study\final\stageComment\pkl\stage2BL.pkl"),
						   readData(r"D:\study\final\stageComment\pkl\stage2WB.pkl"))
	stage3 = mergeTwoLists(readData(r"D:\study\final\stageComment\pkl\stage3BL.pkl"),
						   readData(r"D:\study\final\stageComment\pkl\stage3WB.pkl"))
	stage4 = mergeTwoLists(readData(r"D:\study\final\stageComment\pkl\stage4BL.pkl"),
						   readData(r"D:\study\final\stageComment\pkl\stage4WB.pkl"))

	sentences = []

	preprocess_text(stage1[:size], sentences, 'stage1')
	preprocess_text(stage2[:size], sentences, 'stage2')
	preprocess_text(stage3[:size], sentences, 'stage3')
	preprocess_text(stage4[:size], sentences, 'stage4')
	return sentences

def getStage123EmotionData():
	return readData("emotionSentence.pkl")

def mergeTwoLists(a, b):
	for item in b:
		a.append(item)
	return a

def buildModel():


	sentences = getStage123EmotionData()

	x, y = zip(*sentences)
	train_data, test_data, train_target, test_target = train_test_split(x, y, random_state=1234)
	global n_words
	# 处理词汇
	vocab_processor = learn.preprocessing.VocabularyProcessor(MAX_DOCUMENT_LENGTH, min_frequency=MIN_WORD_FREQUENCE)
	x_train = np.array(list(vocab_processor.fit_transform(train_data)))
	x_test = np.array(list(vocab_processor.transform(test_data)))
	n_words = len(vocab_processor.vocabulary_)
	print('Total words: %d' % n_words)

	cate_dic = {'angry': 1, 'grateful': 2, 'optimistic': 3, 'rational': 4,'uneasy':5}
	train_target = map(lambda x: cate_dic[x], train_target)
	test_target = map(lambda x: cate_dic[x], test_target)
	y_train = pandas.Series(train_target)
	y_test = pandas.Series(test_target)

	# 构建模型
	classifier = learn.SKCompat(learn.Estimator(model_fn=cnn_model))

	# 训练和预测
	classifier.fit(x_train, y_train, steps=1000)
	y_predicted = classifier.predict(x_test)['class']
	score = metrics.accuracy_score(y_test, y_predicted)
	print('Accuracy: {0:f}'.format(score))

buildModel()
