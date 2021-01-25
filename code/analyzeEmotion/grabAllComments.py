import xlrd
import pickle

def grabAndSaveComment(savePath,grabPath):
    workbook = xlrd.open_workbook(grabPath)

    sheets = workbook.sheets()
    res = []
    for sheet in sheets:
        rowNum = sheet.nrows
        for i in range(3,rowNum):
            res.append(sheet.cell_value(i,1))

    output = open(savePath, 'wb')
    temp = pickle.dumps(res)
    output.write(temp)
    output.close()

def grabAndSaveCommentWithLikeNum(savePath,grabPath):
    workbook = xlrd.open_workbook(grabPath)

    sheets = workbook.sheets()
    res = []
    for sheet in sheets:
        rowNum = sheet.nrows
        for i in range(3,rowNum):
            tempRes = []
            tempRes.append(int(sheet.cell_value(i,0)))
            tempRes.append(sheet.cell_value(i,1))
            res.append(tempRes)
    print(res[0])

    output = open(savePath, 'wb')
    temp = pickle.dumps(res)
    output.write(temp)
    output.close()

# grabAndSaveComment("stageComment\pkl\stage1WB.pkl",r"weiboData\weibo-第一阶段.xlsx")
# grabAndSaveComment("stageComment\pkl\stage2WB.pkl",r"weiboData\weibo-第二阶段.xlsx")
# grabAndSaveComment("stageComment\pkl\stage3WB.pkl",r"weiboData\weibo-第三阶段.xlsx")
# grabAndSaveComment("stageComment\pkl\stage4WB.pkl",r"weiboData\weibo-第四阶段.xlsx")
# grabAndSaveComment("stageComment\pkl\stage1BL.pkl",r"bilibiliData\b站评论——阶段1.xlsx")
# grabAndSaveComment("stageComment\pkl\stage2BL.pkl",r"bilibiliData\b站评论——阶段2.xlsx")
# grabAndSaveComment("stageComment\pkl\stage3BL.pkl",r"bilibiliData\b站评论——阶段3.xlsx")
# grabAndSaveComment("stageComment\pkl\stage4BL.pkl",r"b站评论——阶段4.xlsx")
grabAndSaveCommentWithLikeNum("stageComment\pkl\stage1BLWLN.pkl",r"bilibiliData\b站评论——阶段1.xlsx")
grabAndSaveCommentWithLikeNum("stageComment\pkl\stage2BLWLN.pkl",r"bilibiliData\b站评论——阶段2.xlsx")
grabAndSaveCommentWithLikeNum("stageComment\pkl\stage3BLWLN.pkl",r"bilibiliData\b站评论——阶段3.xlsx")
grabAndSaveCommentWithLikeNum("stageComment\pkl\stage4BLWLN.pkl",r"b站评论——阶段4.xlsx")