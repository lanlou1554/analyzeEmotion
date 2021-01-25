# -*- coding = utf-8 -*-
# @Time : 2021/1/25 11:29
# @Author : Xuqi
# @File : wordCloud.py
# @Software : PyCharm

from matplotlib import pyplot as plt
from wordcloud import WordCloud
from PIL import Image
import numpy as np

frequencies = {}    # 词频
for line in open(r"record.txt", encoding="utf-8"):
        arr = line.split(" ")
        frequencies[arr[0]] = float(arr[1])

img = Image.open(r'map.jpg')    # 遮罩图片
img_array = np.array(img)       # 将图片转为数组

wc = WordCloud(
    background_color='white',
    mask=img_array,
    font_path="msyh.ttc"    # 字体
)
word_cloud = wc.generate_from_frequencies(frequencies)

# 写词云图片
word_cloud.to_file("stage4-TR.jpg")

# 绘制图片
fig = plt.figure(1)
plt.imshow(word_cloud)
plt.axis('off')     # 是否显示坐标轴
plt.show()