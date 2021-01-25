import xlrd
import xlwt
def changeFormat(path):

    workbook = xlrd.open_workbook(path)

    sheets = workbook.sheets()
    res = []
    for sheet in sheets:
        rowNum = sheet.nrows
        for i in range(3,rowNum):
            res.append(sheet.cell_value(i,1))
    return res

def saveAsTXT(data,savePath):
    f = open(savePath,'a',encoding='utf-8')
    for d in data:
        print(d)
        f.write(d)
    f.close()

data = changeFormat("b站疫情期间评论——阶段4.xlsx")
saveAsTXT(data,"keywordAna.txt")