import xlrd
import pickle

resBilibili = {}
resWeibo = {}
def mergeTwoLists(a, b):
	for item in b:
		a.append(item)
	return a

def getBilibiliDataByDay(path):
    workbook = xlrd.open_workbook(path)

    sheets = workbook.sheets()
    for sheet in sheets:
        time = str(sheet.cell_value(1,4))
        comment = []
        rowNum = sheet.nrows
        for i in range(3,rowNum):
            commentTemp = []
            commentTemp.append(int(sheet.cell_value(i,0)))
            commentTemp.append(sheet.cell_value(i,1))
            comment.append(commentTemp)
        if time in resBilibili.keys():
            resBilibili[time] = mergeTwoLists(comment,resBilibili[time])
        else:
            resBilibili[time] = comment

def getWeiboDataByDay(path):
    workbook = xlrd.open_workbook(path)

    sheets = workbook.sheets()
    for sheet in sheets:
        time = str(sheet.cell_value(1,1))
        timeTemp = time[:len(time)-5].split("-")
        if len(timeTemp[1])<2:
            timeTemp[1] = "0"+timeTemp[1]
        if len(timeTemp[2])<2:
            timeTemp[2] = "0"+timeTemp[2]
        time = timeTemp[0]+timeTemp[1]+timeTemp[2]
        comment = []
        rowNum = sheet.nrows
        for i in range(3,rowNum):
            comment.append(sheet.cell_value(i,1))
        if time in resWeibo.keys():
            resWeibo[time] = mergeTwoLists(comment,resWeibo[time])
        else:
            resWeibo[time] = comment

if __name__=="__main__":
    getBilibiliDataByDay(r"bilibiliData\b站评论——阶段1.xlsx")
    getBilibiliDataByDay(r"bilibiliData\b站评论——阶段2.xlsx")
    getBilibiliDataByDay(r"bilibiliData\b站评论——阶段3.xlsx")
    getBilibiliDataByDay(r"b站评论——阶段4.xlsx")
    getWeiboDataByDay(r"weiboData\weibo-第一阶段.xlsx")
    getWeiboDataByDay(r"weiboData\weibo-第二阶段.xlsx")
    getWeiboDataByDay(r"weiboData\weibo-第三阶段.xlsx")
    getWeiboDataByDay(r"weiboData\weibo-第四阶段.xlsx")
    resBilibili = sorted(resBilibili.items(),key=lambda item:item[0])
    resWeibo = sorted(resWeibo.items(),key=lambda item:item[0])

    output = open(r"../../tempPKL/cutIntoDayArrayBilibili.pkl", 'wb')
    temp = pickle.dumps(resBilibili)
    output.write(temp)
    output.close()

    output = open(r"../../tempPKL/cutIntoDayArrayWeibo.pkl", 'wb')
    temp = pickle.dumps(resWeibo)
    output.write(temp)
    output.close()

    for r in resBilibili:
        print(r[0])

    print(len(resWeibo))
