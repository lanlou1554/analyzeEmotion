# coding = Utf-8
# -*- coding:utf-8 -*-
import sys
from bs4 import BeautifulSoup
import re
import urllib.request, urllib.error
import xlwt
import sqlite3
from selenium import webdriver
import time




col = ("链接","标题","播放数量","弹幕数量","发布日期","点赞数量","硬币数量","收藏数量","转发数量","评论数量")
findLink = re.compile(r'href="(.*?)"')  # compile创建正则表达式对象，表示规则
findTitle = re.compile(r'href=".*?" title="(.*?)"')
findWatchNum = re.compile(r'<i class="icon-playtime"></i>(.*?)</span>',re.S)
findDanMuNum = re.compile(r'<i class="icon-subtitle"></i>(.*?)</span>',re.S)
findUpdateTime = re.compile(r'<i class="icon-date"></i>(.*?)</span>',re.S)
findLikeNum = re.compile(r'<i class="van-icon-videodetails_like" style="color:;"></i>(.*?)</span>',re.S)
findCoinNum = re.compile(r'<i class="van-icon-videodetails_throw" style="color:;"></i>(.*?)</span>',re.S)
findStarNum = re.compile(r'<i class="van-icon-videodetails_collec" style="color:;"></i>(.*?)</span>',re.S)
findForwardNum = re.compile(r'<i class="van-icon-videodetails_share"></i>(.*?)<div class="share-box">',re.S)
isCommentShut = re.compile(r'评论关闭')
pageTo = 50
pageFrom = 1
commentLikeMinNum = 1
# commentPercentOfPage = 0.02
timeLine1 = [20191208,20200122]
timeLine2 = [20200123,20200207]
timeLine3 = [20200210,20200213]
timeLine4 = [20200310,20200630]
sleepTime = 2

def appendCommentNumAndComment(dataList,i):
    res = []
    for data in dataList:
        try:
            temp = getIndividualVideoComment(data[0])
        except Exception as e:
            print("第"+str(i)+"阶段视频出错，地址是："+str(data[0]))
            continue
        for t in temp:
            data.append(t)
        res.append(data)
    return res

def convertNumStrToInt(s):
    s =s.replace("\n","").replace(" ","")
    s = s.replace("<!---->","")
    if "万" in s:
        s = int(float(s[0:len(s) - 1]) * 10000)
    return s

def getIndividualVideoLink(baseurl):
    dataList = []
    for i in range(pageFrom, pageTo+1):
        url = baseurl + str(i)
        html = askURL(url)

        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all('li', class_="video-item matrix"):
            data = []
            item = str(item)
            link = "https:" + re.findall(findLink, item)[0].replace("amp;","")
            #https://www.bilibili.com/video/BV1kJ411r7cX?from=search&seid=15493096987792884321
            title = re.findall(findTitle,item)[0]
            watchNum = convertNumStrToInt(re.findall(findWatchNum,item)[0])
            danmuNum = convertNumStrToInt(re.findall(findDanMuNum,item)[0])
            updateTime = re.findall(findUpdateTime,item)[0].replace("\n","").replace(" ","").replace("-","")
            # link,title,watchNum,damuNum,updateTime
            data.append(link)
            data.append(title)
            data.append(watchNum)
            data.append(danmuNum)
            data.append(updateTime)
            dataList.append(data)

    res = []
    dataList1 = []
    dataList2 = []
    dataList3 = []
    #dataList4 = []
    for data in dataList:
        updateTime = int(data[4])
        if updateTime <= timeLine1[1] and updateTime >= timeLine1[0]:
            dataList1.append(data)
        elif updateTime <= timeLine2[1] and updateTime >= timeLine2[0]:
            dataList2.append(data)
        elif updateTime <= timeLine3[1] and updateTime >= timeLine3[0]:
            dataList3.append(data)
        # elif updateTime <= timeLine4[1] and updateTime >= timeLine4[0]:
        #     dataList4.append(data)
    res.append(dataList1)
    res.append(dataList2)
    res.append(dataList3)
    # res.append(dataList4)
    print(res)
    return res

# return int likeNum + int coinNum + int starNum + int forwardNum + int commentNum + str[] hotComment(int likeNum + str content)
def getIndividualVideoComment(link):
    res = []
    tags,commentNum,comment,commentLike = askURLForComment(link)
    for item in tags:
        item = str(item)
        likeNum = convertNumStrToInt(re.findall(findLikeNum,item)[0])
        coinNum = convertNumStrToInt(re.findall(findCoinNum,item)[0])
        starNum = convertNumStrToInt(re.findall(findStarNum,item)[0])
        forwardNum = convertNumStrToInt(re.findall(findForwardNum,item)[0])
        res.append(likeNum)
        res.append(coinNum)
        res.append(starNum)
        res.append(forwardNum)

    res.append(commentNum)
    res.append(comment)
    res.append(commentLike)
    return res





# 得到制定一个URL的网页内容
def askURLStatic(url):
    # 个数多可用键值对
    # 伪装成一个浏览器，而非一个py程序
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66",
        # "cookie": "_uuid = C3764279 - 289F - 49F7 - 449A - 830AD34509D058231infoc;buvid3 = B258AEA4 - 12C2 - 4AAF - BA00 - 2CDBDD1ED771155833infoc;sid = ax09asr7;LIVE_BUVID = AUTO7715847705858828;rpdid = | (J |)J)Ykl~R0J'ul)R~~|Y|J; PVID=1; DedeUserID=4238206; DedeUserID__ckMd5=1b0d2a2305629db7; SESSDATA=eacf6bdd%2C1624499131%2Cf5854*c1; bili_jct=f8175f90c2ad05131df5b88fe1e327fe; finger=1571944565; arrange=matrix; CURRENT_FNVAL=80; blackside_state=1",
        # "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        # #"accept-encoding": "gzip, deflate, br",
        # "accept-language": "zh - CN, zh;q = 0.9cache - control: max - age = 0",
        # "referer":"https://www.bilibili.com/",
        # "sec-fetch-dest": "document",
        # "sec-fetch-mode": "navigate",
        # "sec-fetch-site": "same-origin",
        # "sec-fetch-user": "?1upgrade - insecure - requests: 1"
    }
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read()
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html

def askURL(url):
    path = "C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe"  # Get Chromedriver.exe path
    driver = webdriver.Chrome(executable_path=path)  # Drive Chrome
    # The homepage link for one upper whose uid is 10330740
    driver.get(url)
    # Load the url
    time.sleep(5)
    # Check out HTML entire page source codes for one page
    pageSourceThree = driver.page_source
    return pageSourceThree

def askURLForComment(url):
    path = "C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe"  # Get Chromedriver.exe path
    driver = webdriver.Chrome(executable_path=path)  # Drive Chrome
    # The homepage link for one upper whose uid is 10330740
    driver.get(url)
    # Load the url
    time.sleep(sleepTime)
    # Delay 5s
    driver.execute_script('window.scrollBy(0,document.body.scrollHeight)')
    comment = []
    commentLike = []

    time.sleep(1.5)  # 页面滚动到底部
    driver.execute_script('window.scrollBy(0,8000)')
    time.sleep(1.5)

    time.sleep(sleepTime)

    breakFlag = False

    while True:
        try:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            # commentNumTemp = soup.find_all('span',class_="b-head-t results")[0]
            # commentNum = int(re.findall(r'<span class="b-head-t results">(.*?)</span>',str(commentNumTemp))[0])
            tags = soup.find_all('div', class_="ops")
            temps = soup.find_all('div',class_="page-jump")
            whetherBreak = soup.find_all('ul',class_="clearfix")
            if len(re.findall(isCommentShut,str(whetherBreak))) != 0:
                breakFlag = True
                break

            findTotalPageNum = re.compile(r'共<span>(.*?)</span>页')
            pageNum = int(re.findall(findTotalPageNum,str(temps[0]))[0])
            commentNum = pageNum * 20

            commentTemp0 = soup.find_all('p',class_="text")
            commentTemp11 = soup.find_all('div',class_="con")
            findCommentLikeNum = re.compile(r'<span class="like"><i></i><span>(.*?)</span>')
            findComment = re.compile(r'<p class="text">(.*?)</p>',re.S)
            for ct in commentTemp11:
                commentLikeNum = int(re.findall(findCommentLikeNum,str(ct))[0])
                commentLike.append(commentLikeNum)
            for ct in commentTemp0:
                commentTemp = str(re.findall(findComment,str(ct))[0]).replace(r'<br/>',"")
                comment.append(commentTemp)
            break
        except Exception as e:
            time.sleep(sleepTime)


    while not breakFlag:
        flag = False
        try:
            c = driver.find_element_by_css_selector(
                "#comment > div > div.comment > div.bb-comment > div.bottom-page.paging-box-big > a.next")
            # print(c)
            c.click()  # 模拟点击下一页，当没有下一页的时候就会进行下面一个操作
            time.sleep(sleepTime)
            time.sleep(0.5)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            commentTemp0 = soup.find_all('p', class_="text")
            commentTemp11 = soup.find_all('div', class_="con")
            findCommentLikeNum = re.compile(r'<span class="like"><i></i><span>(.*?)</span>')
            findComment = re.compile(r'<p class="text">(.*?)</p>', re.S)
            for ct in commentTemp11:
                try:
                    commentLikeNum = int(re.findall(findCommentLikeNum, str(ct))[0])
                except Exception as e:
                    commentLikeNum = 0
                if commentLikeNum < commentLikeMinNum:
                    flag = True
                commentLike.append(commentLikeNum)
            for ct in commentTemp0:
                commentTemp = str(re.findall(findComment, str(ct))[0]).replace(r'<br/>', "")
                comment.append(commentTemp)
            if flag:
                break
        except Exception as e:
            print(e)
            print("出错了！地址为："+url)
            break
    # Check out HTML entire page source codes for one page
    return tags,commentNum,comment,commentLike


def saveData(dataList, savepath):
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)
    sheets = []
    for i in range(len(dataList)):
        sheet = book.add_sheet('视频'+str(i),cell_overwrite_ok=True)
        sheets.append(sheet)
    col = ("链接","标题","播放数量","弹幕数量","发布日期","点赞数量","硬币数量","收藏数量","转发数量","评论数量")

    for i in range(len(sheets)):
        sheet = sheets[i]
        for j in range(0, len(col)):
            sheet.write(0, j, col[j])
            sheet.write(1,j,dataList[i][j])
        sheet.write(2,0,"评论点赞数")
        sheet.write(2,1,"评论内容")
        for j in range(3,3+len(dataList[i][len(col)])):
            sheet.write(j,0,dataList[i][len(col)+1][j-3])
            sheet.write(j, 1, dataList[i][len(col)][j - 3])

    book.save(savepath)


def saveData2DB(dataList, dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()

    for data in dataList:
        for index in range(len(data)):
            if not is_number(data[index]):
                data[index] = '"' + data[index] + '"'
        sql = '''
            insert into movie250 
            (info_link,pic_link,cname,ename,score,rated,introduction,info)
            values(%s)''' % ",".join(data)
        cursor.execute(sql)
        conn.commit()
    conn.close()


def init_db(dbpath):
    sql = '''
     create table movie250
     (
     id integer primary key autoincrement,
     info_link text,
     pic_link text,
     cname varchar,
     ename varchar,
     score numeric,
     rated numeric,
     introduction text,
     info text 
     )
 '''
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False



if __name__ == "__main__":
    baseurl = "https://search.bilibili.com/all?keyword=%E7%96%AB%E6%83%85&order=click&duration=0&tids_1=0&page="
    savepath = []
    dataList = []
    savepath.append("b站评论全——阶段1.xls")
    savepath.append("b站评论全——阶段2.xls")
    savepath.append("b站评论全——阶段3.xls")
    savepath.append("b站评论全——阶段4.xls")
    dataListTemp = getIndividualVideoLink(baseurl)
    #dataListTemp = [[['https://www.bilibili.com/video/BV117411v78z?from=search&seid=8074312763742338398', '【新闻联播】习近平对新型冠状病毒感染的肺炎疫情作出重要指示', 2147000, '0', '20200120'], ['https://www.bilibili.com/video/BV1G7411i7M1?from=search&seid=464536162209239328', '钟南山：新型冠状病毒会人传人 暂比SARS弱 戴口罩可预防', 1973000, '8039', '20200121']], [['https://www.bilibili.com/video/BV1v7411s7Yd?from=search&seid=2202266572971212174', '小当家最难的真鲷大陆图竟然被我做出来了！', 2892000, 20000, '20200203'], ['https://www.bilibili.com/video/BV1D7411k7tS?from=search&seid=2202266572971212174', '因疫情无法返乡，清华博士宅在家给猫讲函数', 2837000, '3761', '20200126'], ['https://www.bilibili.com/video/BV1r741167qv?from=search&seid=2202266572971212174', '这个摔炮有赌的成分', 2814000, '632', '20200127'], ['https://www.bilibili.com/video/BV167411B7N3?from=search&seid=12029447911971418058', '我吐槽我自己，2020可不能再乱买东西了', 2754000, 42000, '20200131'], ['https://www.bilibili.com/video/BV1S7411q7wp?from=search&seid=1684348759439363718', '【鬼谷闲谈】病毒：生于三界之外 不灭六道之中', 2587000, 11000, '20200130'], ['https://www.bilibili.com/video/BV1j7411H7TL?from=search&seid=1684348759439363718', '能力越大责任越大！我就是这个城市的救星！一只非常普通的鹿', 2540000, 38000, '20200205'], ['https://www.bilibili.com/video/BV187411H782?from=search&seid=1684348759439363718', '连续爆肝45天用方块还原拜年祭？【火锅城】完美细节还原！', 2493000, 13000, '20200206'], ['https://www.bilibili.com/video/BV1m7411r7jf?from=search&seid=1684348759439363718', '凤凰专访钟南山：已对疫情做最坏打算，湖北武汉病患数量无任何隐瞒', 2484000, '889', '20200125'], ['https://www.bilibili.com/video/BV1U7411B7Km?from=search&seid=1684348759439363718', '我和我的猫，到此一游', 2476000, '9170', '20200131'], ['https://www.bilibili.com/video/BV1K7411x7rW?from=search&seid=4158902562957895798', '新型冠状病毒有多狡猾？疫情当头,肺炎之下,病毒与人类的军备竞赛,谁能活到最后？武汉加油!', 2408000, 16000, '20200204'], ['https://www.bilibili.com/video/BV137411H7Bt?from=search&seid=4158902562957895798', '外国女孩在上海经历肺炎，父母却因为西方媒体的假新闻特别担心自己的女儿', 2364000, '5897', '20200205'], ['https://www.bilibili.com/video/BV1X7411p7Vc?from=search&seid=10348676824032670363', '【田逾欢】女生如何根据脸型选发型/选对发型巧妙掩盖脸型缺陷提高颜值', 2308000, 26000, '20200204'], ['https://www.bilibili.com/video/BV1Y7411p7PK?from=search&seid=10348676824032670363', '不同人眼中的肺炎疫情', 2206000, 16000, '20200204'], ['https://www.bilibili.com/video/BV1n7411k7Pk?from=search&seid=8074312763742338398', '还在买天价n95口罩？防毒面具效果更好！价格是kn95口罩的十分之一 或许能够帮到你  武汉加油', 2152000, '2213', '20200126'], ['https://www.bilibili.com/video/BV1j7411z7KQ?from=search&seid=464536162209239328', '简单算算，你宅在家里究竟能为抗击肺炎疫情做出多大贡献？', 2009000, 21000, '20200129'], ['https://www.bilibili.com/video/BV1U7411W787?from=search&seid=464536162209239328', '云监工的胜利！武汉挖掘机天团火到日本，日本网友吐槽，你们居然也有呕泥酱？', 2007000, '5687', '20200203'], ['https://www.bilibili.com/video/BV1E7411Y7iz?from=search&seid=3252349508043765756', '河南这个疫情防护宣传真是太硬核了', 1902000, '4812', '20200124'], ['https://www.bilibili.com/video/BV1X7411x7qx?from=search&seid=3252349508043765756', '十四天不出门，大sao在楼顶炖鸡烧肉，大锅台配小酒，一家人娱乐', 1884000, 12000, '20200202'], ['https://www.bilibili.com/video/BV117411b7gx?from=search&seid=3252349508043765756', '由于疫情严峻 昨天被老婆打后她一直不肯送我去医院', 1835000, '148', '20200207'], ['https://www.bilibili.com/video/BV1c7411B7rD?from=search&seid=13384828349062390327', '【嘟督咆哮解说】你见过腿这么长的女鬼吗？！《港诡实录》', 1756000, 30000, '20200130'], ['https://www.bilibili.com/video/BV1u7411679U?from=search&seid=17636439235460837626', '播报疫情，浙江的方言真是绝！', 1724000, 13000, '20200130'], ['https://www.bilibili.com/video/BV1j7411x7vn?from=search&seid=17636439235460837626', '【泡芙喵】✌ 彩 虹 节 拍 ✌｜ BdF2020 ｜ 生日作✿', 1714000, '6239', '20200201'], ['https://www.bilibili.com/video/BV1Q7411q74A?from=search&seid=17636439235460837626', '当我拔出剑的一刻，世界:没人能够白嫖！', 1701000, 12000, '20200130']], [['https://www.bilibili.com/video/BV1x7411V7wq?from=search&seid=4158902562957895798', '建议改为：网 课 食 神', 2460000, '1728', '20200213'], ['https://www.bilibili.com/video/BV1x741157p9?from=search&seid=4158902562957895798', '用嘶吼来玩的恐怖游戏，啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊！', 2440000, 43000, '20200211'], ['https://www.bilibili.com/video/BV16741157oH?from=search&seid=4158902562957895798', '噩梦终于结束了！30天全脸大换血，抽脂/吸脂+脂肪填充恢复全记录vlog', 2396000, 39000, '20200211'], ['https://www.bilibili.com/video/BV1V7411371D?from=search&seid=464536162209239328', '抗击疫情，在家学做街头美食，八盘配菜做一碗面，两大碗吃不过瘾', 2015000, 21000, '20200213'], ['https://www.bilibili.com/video/BV13741157LS?from=search&seid=17636439235460837626', '疫情宅在家，一起发胖呀！试试爆浆巧克力熔岩蛋糕，让我们在胖的路上起飞吧！', 1722000, 12000, '20200213'], ['https://www.bilibili.com/video/BV1i741137i4?from=search&seid=17636439235460837626', '韩国首尔市市长：现在该是我们报恩的时候了', 1683000, 12000, '20200213']], [['https://www.bilibili.com/video/BV1E54y1D7Yn?from=search&seid=2202266572971212174', '差点破产的武汉老板，送出万份免费盒饭后，如今直播“卖饭”', 2918000, '8208', '20200511'], ['https://www.bilibili.com/video/BV1H7411d7H9?from=search&seid=2202266572971212174', '这个游戏太真实了，让我对超市产生了恐惧！', 2906000, 33000, '20200317'], ['https://www.bilibili.com/video/BV1d741197RP?from=search&seid=2202266572971212174', '中国人又在干嘛？？？', 2902000, '5266', '20200318'], ['https://www.bilibili.com/video/BV1Q7411Z7Kp?from=search&seid=2202266572971212174', '实拍美国疫情，纽约大部分地方关门，新泽西开始宵禁！', 2896000, 23000, '20200317'], ['https://www.bilibili.com/video/BV1Zc41187Wn?from=search&seid=2202266572971212174', '央视和郭杰瑞连线直播完整版来了', 2891000, 22000, '20200401'], ['https://www.bilibili.com/video/BV1m54y1Q7Ex?from=search&seid=2202266572971212174', '泰国猫咪因违反外出禁令被逮捕 网友：看表情就是社会猫', 2870000, '1961', '20200429'], ['https://www.bilibili.com/video/BV1gE411A7jq?from=search&seid=2202266572971212174', '被气疯的意大利市长，学到了河南村长的精髓', 2867000, '5221', '20200320'], ['https://www.bilibili.com/video/BV16a4y1t7pp?from=search&seid=2202266572971212174', '不 要 抽 到 挑 战', 2862000, 50000, '20200328'], ['https://www.bilibili.com/video/BV11741117fj?from=search&seid=2202266572971212174', '这个游戏都快把我吓哭了！硬着头皮玩通关！', 2860000, 78000, '20200325'], ['https://www.bilibili.com/video/BV1iE411c7tD?from=search&seid=2202266572971212174', '骁话一下：塞尔维亚曾是世界第七工业国，为何如今总统含泪求援中国', 2830000, 35000, '20200321'], ['https://www.bilibili.com/video/BV13e411s7Xm?from=search&seid=12029447911971418058', '因疫情封锁，印度“不宜洗澡”的恒河水清澈见底，已达直接饮用标准', 2789000, '3277', '20200414'], ['https://www.bilibili.com/video/BV1bZ4y1j7yi?from=search&seid=12029447911971418058', '中国抗疫图鉴', 2784000, 28000, '20200405'], ['https://www.bilibili.com/video/BV1uE411c7yy?from=search&seid=12029447911971418058', '这个高中不简单！', 2774000, 49000, '20200323'], ['https://www.bilibili.com/video/BV1AE411w7B8?from=search&seid=12029447911971418058', '被疫情提问惹恼 特朗普怒吼记者：我一直是对的！', 2754000, '9294', '20200321'], ['https://www.bilibili.com/video/BV1h741197Lm?from=search&seid=12029447911971418058', '因为这个游戏，我体验了一把卧底的感觉', 2737000, 28000, '20200327'], ['https://www.bilibili.com/video/BV1v7411m7Rz?from=search&seid=12029447911971418058', '美主持人：中国专家批评意大利封锁松散，这“松散的封锁”在美国才刚刚开始', 2726000, '9501', '20200323'], ['https://www.bilibili.com/video/BV1ba4y147aB?from=search&seid=12029447911971418058', '【川普】出卖（出山）', 2696000, 22000, '20200423'], ['https://www.bilibili.com/video/BV1P5411x7i9?from=search&seid=12029447911971418058', '疫情把一个演员变成了厂狗', 2694000, '3421', '20200528'], ['https://www.bilibili.com/video/BV1Mk4y1k7QB?from=search&seid=12029447911971418058', '骁话一下：大英帝国，对冲国运，猛男荷官鲍里斯在线发牌', 2684000, 42000, '20200509'], ['https://www.bilibili.com/video/BV1U7411o7LG?from=search&seid=12029447911971418058', '美国男子冲入美媒直播镜头怒斥：中国很对，是你们在炒作', 2682000, '3270', '20200316'], ['https://www.bilibili.com/video/BV1LE411G7F4?from=search&seid=12029447911971418058', '最近突然火的《少年》太好听了，单曲循环了很多遍！', 2674000, '2359', '20200316'], ['https://www.bilibili.com/video/BV1ok4y1d75w?from=search&seid=12029447911971418058', '【中西合璧】当古筝在法国街头遇上《克罗地亚狂想曲》？', 2665000, '6674', '20200328'], ['https://www.bilibili.com/video/BV1iT4y1G7RG?from=search&seid=1684348759439363718', '美国疫情破80万，为什么还要上街游行求解封？', 2623000, 21000, '20200421'], ['https://www.bilibili.com/video/BV1Vf4y1m74E?from=search&seid=1684348759439363718', '骁话一下：法国拥有世界第一福利，为何面对疫情不堪一击？', 2601000, 60000, '20200502'], ['https://www.bilibili.com/video/BV1AT4y1G7rQ?from=search&seid=1684348759439363718', '【懂点儿啥48】方方武汉日记出版，熟悉的配方有内味了', 2579000, 83000, '20200410'], ['https://www.bilibili.com/video/BV1zE41157G2?from=search&seid=1684348759439363718', '最强篮球队之我的队友都是演员！', 2574000, 36000, '20200313'], ['https://www.bilibili.com/video/BV1Ft4y127wC?from=search&seid=1684348759439363718', '【懂点儿啥49】屡次辱华的丹麦，面对中国的物资时……', 2557000, 61000, '20200414'], ['https://www.bilibili.com/video/BV165411x7v9?from=search&seid=1684348759439363718', '当有陌生人敲门！打开这个视频！快！', 2537000, '4126', '20200427'], ['https://www.bilibili.com/video/BV1z7411R7EP?from=search&seid=1684348759439363718', '入职阿里巴巴的第二天就要变成印度网红了！？', 2497000, 26000, '20200320'], ['https://www.bilibili.com/video/BV1cK411W7yK?from=search&seid=1684348759439363718', '【万物皆可做刀】世界上最锋利的沙之刃', 2493000, 18000, '20200615'], ['https://www.bilibili.com/video/BV1f7411d7KP?from=search&seid=1684348759439363718', '意大利朋友告诉我，一定要把这个视频给中国朋友看！｜新冠肺炎', 2493000, 23000, '20200318'], ['https://www.bilibili.com/video/BV1fC4y1s7nD?from=search&seid=4158902562957895798', '骁话番外：美国主播泼中国脏水，几个菜呀喝成这样？', 2472000, 45000, '20200421'], ['https://www.bilibili.com/video/BV1gE411V7Hs?from=search&seid=4158902562957895798', '2020逆风翻盘！疫情结束后的新机会丨ztalk', 2461000, 117000, '20200315'], ['https://www.bilibili.com/video/BV1hg4y1z7Ua?from=search&seid=4158902562957895798', '欠钱不还,阿根廷疫情中第一个倒下的国家？【大蜡烛】', 2447000, 21000, '20200426'], ['https://www.bilibili.com/video/BV13E411L7op?from=search&seid=4158902562957895798', '面对疫情，日本到底怎么了？谁来负责...', 2446000, 63000, '20200311'], ['https://www.bilibili.com/video/BV1Pz411b71x?from=search&seid=4158902562957895798', '这就是中国公演！众多韩国明星直言不可能之系列（一)', 2435000, '2355', '20200330'], ['https://www.bilibili.com/video/BV1E7411f7HE?from=search&seid=4158902562957895798', '火遍全网！美国记者介绍中国抗疫：和美国天差地别', 2428000, '7788', '20200315'], ['https://www.bilibili.com/video/BV14K4y1t7Sf?from=search&seid=4158902562957895798', '我做了新冠病毒抗体测试，第二天就拿到了结果！', 2414000, 11000, '20200528'], ['https://www.bilibili.com/video/BV1cE41157U4?from=search&seid=4158902562957895798', '最后耿爽这一笑，你品，你细品~', 2385000, '3918', '20200312'], ['https://www.bilibili.com/video/BV1xz4y1d7yr?from=search&seid=4158902562957895798', '因疫情被裁员，西餐厨师路边摆起午夜牛扒摊', 2370000, '3012', '20200528'], ['https://www.bilibili.com/video/BV1S7411Q7ab?from=search&seid=10348676824032670363', '微表情分析【特朗普】是否撒谎！！！', 2308000, 18000, '20200328'], ['https://www.bilibili.com/video/BV11741117gK?from=search&seid=10348676824032670363', '意大利外长：当初赠中国4万只口罩我备受指责 现在中国回赠数百万只', 2292000, '2885', '20200325'], ['https://www.bilibili.com/video/BV1A7411d7Dz?from=search&seid=10348676824032670363', '“即使得新冠也不能阻止我去聚会” 美国小伙的这番话引网友猛批', 2260000, 13000, '20200319'], ['https://www.bilibili.com/video/BV1W741127Sq?from=search&seid=10348676824032670363', '男子日本网上买了蛋包饭生成器？倒入蛋液后结果。。。。', 2241000, 29000, '20200324'], ['https://www.bilibili.com/video/BV1kk4y1R7Ha?from=search&seid=10348676824032670363', '骁话番外：我最懂特朗普 VS 妈最爱纽约州长，怎么抗疫就演成了权斗戏？', 2215000, 26000, '20200416'], ['https://www.bilibili.com/video/BV1TK4y187sV?from=search&seid=10348676824032670363', '用朱一旦的方式打开西方抹黑中国过程！我投你以西柚，你报我以匕首！', 2201000, '7209', '20200506'], ['https://www.bilibili.com/video/BV1DE41137tA?from=search&seid=10348676824032670363', '深更半夜的潜入高中真的让我感到背后发凉！', 2195000, 37000, '20200315'], ['https://www.bilibili.com/video/BV14T4y1u7Af?from=search&seid=10348676824032670363', '一斤苕粉，一斤炸鸡，大sao做大锅炖菜，一人吃一锅，米饭煮少了', 2194000, 23000, '20200518'], ['https://www.bilibili.com/video/BV1n64y1M7cH?from=search&seid=8074312763742338398', '骁遣05：美国确诊破百万，“永不犯错”特朗普又想把锅甩给谁？', 2173000, 26000, '20200428'], ['https://www.bilibili.com/video/BV1q7411o7eP?from=search&seid=8074312763742338398', '塞尔维亚总统宣布进入紧急状态：寄希望于中国技术与物资援助', 2145000, '5130', '20200316'], ['https://www.bilibili.com/video/BV1zK411L74y?from=search&seid=8074312763742338398', '外媒质疑中国举措没人权？英国专家：中国的人权就是让人们活下来！', 2143000, '6865', '20200408'], ['https://www.bilibili.com/video/BV1jC4y1W7Hx?from=search&seid=8074312763742338398', '【中字】外国小哥被疫情逼出迪士尼人格', 2116000, '6288', '20200424'], ['https://www.bilibili.com/video/BV1bE411N7oA?from=search&seid=8074312763742338398', '【独树一帜38】英国防疫上演川剧变脸 到底打了谁的白月光脸？', 2089000, 27000, '20200320'], ['https://www.bilibili.com/video/BV1z54y1Q7E9?from=search&seid=8074312763742338398', '中国人不买澳大利亚的东西就是“经济胁迫”？为啥不买心里没点数，耿爽回怼', 2085000, '2598', '20200428'], ['https://www.bilibili.com/video/BV1Ge4114743?from=search&seid=8074312763742338398', '【美国网友：中国已成为世界的老大】美国州长哽咽含泪感谢中国22批次援助物资', 2068000, '8789', '20200408'], ['https://www.bilibili.com/video/BV1K7411d7jX?from=search&seid=8074312763742338398', '骁话一下：投下一半GDP，中国如何用数字化新基建打抗疫“世界大战”', 2037000, 28000, '20200319'], ['https://www.bilibili.com/video/BV1oK4y147GZ?from=search&seid=8074312763742338398', '一言不爽秒走人！遭记者灵魂追问，特朗普崩溃了', 2034000, '6419', '20200512'], ['https://www.bilibili.com/video/BV1aQ4y1K7wR?from=search&seid=464536162209239328', '武汉解封第一天 黄鼠狼饥饿难耐街头向路人乞食 网友：可爱又心疼', 2005000, '1542', '20200409'], ['https://www.bilibili.com/video/BV1mE411G7PJ?from=search&seid=464536162209239328', '全 世 界 都 说 钉 钉 话', 2001000, 13000, '20200313'], ['https://www.bilibili.com/video/BV1s7411U799?from=search&seid=464536162209239328', '日本导演把中国南京人的防疫日常推上了全球热搜榜', 1992000, '1856', '20200323'], ['https://www.bilibili.com/video/BV15e411x7kH?from=search&seid=464536162209239328', '【懂点儿啥40】澳大利亚多次反华排华，如今疫情来了怎么办？', 1978000, 44000, '20200326'], ['https://www.bilibili.com/video/BV1Mc411h7XQ?from=search&seid=464536162209239328', '假口罩的罪与罚', 1968000, 24000, '20200403'], ['https://www.bilibili.com/video/BV1w7411y7Gf?from=search&seid=464536162209239328', '笑翻！英国小女孩因中餐厅关闭崩溃大哭：要吃妈妈做的饭了', 1966000, '1737', '20200326'], ['https://www.bilibili.com/video/BV16Z4y1j77a?from=search&seid=464536162209239328', '香港记者询问WHO是否会重新考虑台湾的成员资格 助理总干事：拜拜', 1964000, '8320', '20200328'], ['https://www.bilibili.com/video/BV1wg4y1q78h?from=search&seid=464536162209239328', '特朗普：如果中国算发展中国家，那美国也是发展中国家', 1958000, '2691', '20200611'], ['https://www.bilibili.com/video/BV1Mt4y117os?from=search&seid=464536162209239328', '金灿荣：疫情之后，如果他们继续瞎搞，可能祖国统一就提前实现了', 1951000, 16000, '20200507'], ['https://www.bilibili.com/video/BV14E411N7Sz?from=search&seid=464536162209239328', '【钢琴】前方爆燃高能!《撒野》广播剧超还原钢琴改编版 戴上耳机！简介附谱', 1950000, 18000, '20200320'], ['https://www.bilibili.com/video/BV1rf4y1S7G3?from=search&seid=3252349508043765756', '初三化学老师回应带猫上课：上课时碰巧猫进来了', 1938000, '1458', '20200427'], ['https://www.bilibili.com/video/BV1op4y1X7N2?from=search&seid=3252349508043765756', '骁遣一下：教人注射消毒剂？老科学家特朗普又上线了', 1925000, 39000, '20200426'], ['https://www.bilibili.com/video/BV17K411j7bq?from=search&seid=3252349508043765756', '越来越多的外国人开始明白：中国没有因为疫情停摆是这个世界最大的幸事！中国正在拯救世界！', 1911000, '6888', '20200419'], ['https://www.bilibili.com/video/BV1A7411y7Cc?from=search&seid=3252349508043765756', '从日本抗疫分析其民族底层逻辑,无用的人不必活着！【思维实验室】第三十期 菊与刀', 1893000, 24000, '20200327'], ['https://www.bilibili.com/video/BV1R7411d7cV?from=search&seid=3252349508043765756', '关乎逆风笑名誉的马车8决斗！', 1887000, 22000, '20200318'], ['https://www.bilibili.com/video/BV1wT4y1G7Et?from=search&seid=3252349508043765756', '【毕导】新冠疫苗的最完全解析：是科学的战争，也是大国的较量', 1871000, 32000, '20200329'], ['https://www.bilibili.com/video/BV1T64y1u7Dm?from=search&seid=3252349508043765756', '八国语言版《好想爱这个世界啊》献给全世界为疫情战斗的英雄们!【飞鸟乐团】', 1847000, '6800', '20200405'], ['https://www.bilibili.com/video/BV1sp4y197fm?from=search&seid=3252349508043765756', '“黑人抬棺”老哥：疫情结束后我们会涨价哦！', 1836000, '4346', '20200503'], ['https://www.bilibili.com/video/BV1PE411w7xw?from=search&seid=13384828349062390327', '意大利雪上加霜,熔断美国寅吃卯粮,中国抢救世界？', 1834000, 12000, '20200321'], ['https://www.bilibili.com/video/BV1de411W7EF?from=search&seid=13384828349062390327', '墨西哥毒枭给贫民发抗疫物资 总统洛佩斯：政府已无法阻止他们', 1834000, '2847', '20200421'], ['https://www.bilibili.com/video/BV1C7411R7Pa?from=search&seid=13384828349062390327', '台湾称每周将向美国供10万只口罩。。。', 1822000, '7166', '20200319'], ['https://www.bilibili.com/video/BV1yT4y1G7zn?from=search&seid=13384828349062390327', '骁话番外：明知是被特朗普当枪使，为什么底层白人还上街抗议求复工？', 1792000, 30000, '20200420'], ['https://www.bilibili.com/video/BV127411d7RK?from=search&seid=13384828349062390327', '外交部：中国愿派医疗专家组赴塞尔维亚', 1790000, '6216', '20200317'], ['https://www.bilibili.com/video/BV1jE411w7Ud?from=search&seid=13384828349062390327', '听说现在美国人是这样防范新冠疫情的', 1786000, '644', '20200323'], ['https://www.bilibili.com/video/BV1Jg4y1z77P?from=search&seid=13384828349062390327', '各国现存确诊人数 此生无悔入华夏 下一句……', 1783000, 19000, '20200416'], ['https://www.bilibili.com/video/BV1dA411i7C4?from=search&seid=13384828349062390327', '听说疫情让俄罗斯倒退40年', 1774000, '6323', '20200519'], ['https://www.bilibili.com/video/BV1f64y1T7nq?from=search&seid=13384828349062390327', '【C菌】“群体免疫”已经一个月了, 英国现在是什么样?', 1754000, '7239', '20200430'], ['https://www.bilibili.com/video/BV1mT4y1372x?from=search&seid=13384828349062390327', '骁遣07：英国死亡人数欧洲第一，政府抗疫专家却偷偷带情人回家？', 1751000, 20000, '20200506'], ['https://www.bilibili.com/video/BV13a4y1t7CR?from=search&seid=13384828349062390327', '各国疫情现状', 1735000, '3204', '20200326'], ['https://www.bilibili.com/video/BV1of4y117av?from=search&seid=17636439235460837626', '封国的第五十二天 印度的内部矛盾又开始了', 1728000, '4760', '20200516'], ['https://www.bilibili.com/video/BV1a54y1D7td?from=search&seid=17636439235460837626', '奥巴马再批特朗普政府：连假装负责都做不到', 1728000, '3519', '20200517'], ['https://www.bilibili.com/video/BV1ME411F7nA?from=search&seid=17636439235460837626', '英国首相鲍里斯·约翰逊发表演讲：大家做好失去亲人的准备吧...', 1713000, 25000, '20200316'], ['https://www.bilibili.com/video/BV1ZK4y1r7Vm?from=search&seid=17636439235460837626', '【懂点儿啥46】美国吹哨人的下场，我看了手脚冰冷，浑身发抖', 1711000, 48000, '20200406'], ['https://www.bilibili.com/video/BV1Vk4y1z7gk?from=search&seid=17636439235460837626', '武器+弹药，来了', 1709000, '4449', '20200601'], ['https://www.bilibili.com/video/BV1TE411j7No?from=search&seid=17636439235460837626', '意大利大使在美媒喊话：批欧盟无一国响应求援，只有中国帮我们', 1705000, '2350', '20200312'], ['https://www.bilibili.com/video/BV1gg4y1q7sY?from=search&seid=17636439235460837626', '孩子，你要庆幸自己的肤色', 1686000, '280', '20200605'], ['https://www.bilibili.com/video/BV1dE411V7UA?from=search&seid=17636439235460837626', '直播现场变魔术？英国财政大臣红色文件夹瞬间变绿', 1685000, '1202', '20200312']]]
    # "链接","标题","播放数量","弹幕数量","发布日期","点赞数量","硬币数量","收藏数量","转发数量","评论数量","评论数组"，"对应的评论like数"
    #for i in range(0,len(dataListTemp)):
    for i in range(0, len(dataListTemp)):
        data = appendCommentNumAndComment(dataListTemp[i],i)
        # dataList.append(data)
        saveData(data,savepath[i])


