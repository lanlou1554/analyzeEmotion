# from datetime import datetime
import json
import re
import time
import xlwt as xlwt
from lxml import etree
# import xlrd
# import openpyxl

# from xlutils.copy import copy as xl_copy

from util.news_parser import NewsParser, ua1
from util.str_util import str_list_process, str_process, remove_sign


# def find_urls(news_parser, num):
#     result = []
#     for i in range(num):
#         all_urls = news_parser.get_dynamic_elements('//div[@class="box-result clearfix"]//a')
#         result.extend([cur_url.get_attribute("href") for cur_url in all_urls])
#         news_parser.get_dynamic_element('//table[@style="margin:0 auto;"]//a[@title="下一页"]').click()
#     return result


def find_urls(news_parser, base_url, max_num):
    res = []
    # html = news_parser.get_static(base_url)
    raw = news_parser.get_static_raw(base_url)
    html = etree.HTML(raw)
    cur_html = html
    while max_num >= 1:
        cur_urls = cur_html.xpath("//a[@action-type='fl_unfold']/@href")
        res.extend(["https:" + cur_url for cur_url in cur_urls])
        next = html.xpath("//a[@class='next']/@href")
        if len(next) == 0:
            break
        cur_html = news_parser.get_static("https://s.weibo.com" + next[0])
        max_num -= 1
        time.sleep(5)
    return res


@str_process
def get_topic(news_parser, url):
    static_raw = news_parser.get_static_raw(url)
    static = etree.HTML(static_raw)
    return static.xpath('//head//title/text()')[0]


@str_process
def get_time(news_parser, url):
    static_raw = news_parser.get_static_raw(url)
    static = etree.HTML(static_raw)
    cur_list = static.xpath('//script/text()')
    mid = []
    for script in cur_list:
        if "feed_list_item_date" in script:
            mid = re.findall('.*(<a.*?feed_list_item_date.*?/a>).*', script[3000:7000])
            break
    next_html = etree.HTML(mid[0])
    res_time = next_html.xpath("//a/text()")
    return res_time[0].strip()


@str_list_process
def get_comments(news_parser, url):
    static = news_parser.get_static(url)
    mid_list = static.xpath("//script/text()")
    mid = []
    for cur_mid in mid_list:
        if "act=" in cur_mid:
            mid = re.findall(r'.*act=(\d+).*', cur_mid)
            break
    mid = eval(mid[0])
    html = news_parser.get_static_raw(
        "https://weibo.com/aj/v6/comment/big?ajwvr=6&id={}&from=singleWeiBo&__rnd=1608146907945".format(mid),
        encoding='Unicode')
    json_ins = json.loads(html)
    comments_html = etree.HTML(json_ins['data']['html'])
    comments = comments_html.xpath("//div[@class='list_li S_line1 clearfix']//div[@class='WB_text']/text()")
    return comments


def get_one(news_parser: NewsParser, url: str, res: list):
    try:
        topic = get_topic(news_parser, url)
        # time.sleep(2)
        cur_time = get_time(news_parser, url)
        # time.sleep(2)
        comments = get_comments(news_parser, url)
        # time.sleep(2)
        res.extend([topic, cur_time, url, comments])
    except Exception as e:
        print(e.args)
        pass


def get_all():
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    news_manager = NewsParser("https://weibo.com/login.php", ua1)
    news_manager.login({'name': '591354379@qq.com',
                        'passwd': 'Xq010307',
                        'login_name_xpath': "//input[@id='loginname']",
                        'passwd_xpath': "//input[@type='password']",
                        'submit_xpath': "//a[@suda-data='key=tblog_weibologin3&value=click_sign']"
                        })
    # news_manager.get_dynamic_element("//a[@node-type='searchSubmit']").click()
    # news_manager.get_dynamic_element("//input[@node-type='text']").send_keys("新冠疫情")
    # news_manager.get_dynamic_element("//button[@class='s-btn-b']").click()
    # news_manager.get_dynamic_element("//a[@node-type='advsearch']").click()

    # 第一阶段
    urls_feiyan = find_urls(news_manager,
                            "https://s.weibo.com/weibo?q=%E8%82%BA%E7%82%8E&xsort=hot&suball=1&timescope=custom:2019-12-08-0:2020-01-22-23&Refer=g"
                            , 19)
    urls_yi = find_urls(news_manager,
                        "https://s.weibo.com/weibo?q=%E7%96%AB&xsort=hot&suball=1&timescope=custom:2019-12-08-0:2020-01-22-23&Refer=SWeibo_box"
                        , 13)
    urls_xinguan = find_urls(news_manager,
                             "https://s.weibo.com/weibo?q=%E6%96%B0%E5%86%A0&xsort=hot&suball=1&timescope=custom:2019-12-08-0:2020-01-22-23&Refer=g"
                             , 2)
    urls_wuhan = find_urls(news_manager,
                           "https://s.weibo.com/weibo?q=%E6%AD%A6%E6%B1%89&xsort=hot&suball=1&timescope=custom:2019-12-08-0:2020-01-22-23&Refer=SWeibo_box"
                           , 18)
    urls_bingli = find_urls(news_manager,
                            "https://s.weibo.com/weibo?q=%E7%97%85%E4%BE%8B&xsort=hot&suball=1&timescope=custom:2019-12-08-0:2020-01-22-23&Refer=SWeibo_box"
                            , 18)
    urls_zhengzhuang = find_urls(news_manager,
                                 "https://s.weibo.com/weibo?q=%E7%97%87%E7%8A%B6&xsort=hot&suball=1&timescope=custom:2019-12-08-0:2020-01-22-23&Refer=SWeibo_box"
                                 , 19)
    urls_quezhen = find_urls(news_manager,
                             "https://s.weibo.com/weibo?q=%E7%A1%AE%E8%AF%8A&xsort=hot&suball=1&timescope=custom:2019-12-08-0:2020-01-22-23&Refer=SWeibo_box"
                             , 18)

    # 第二阶段
    # urls_feiyan = find_urls(news_manager,
    #                     "https://s.weibo.com/weibo?q=%E8%82%BA%E7%82%8E&xsort=hot&suball=1&timescope=custom:2020-01-23-0:2020-02-07-23&Refer=g"
    #                     , 19)
    # urls_yi = find_urls(news_manager,
    #                     "https://s.weibo.com/weibo?q=%E7%96%AB&xsort=hot&suball=1&timescope=custom:2020-01-23-0:2020-02-07-23&Refer=SWeibo_box"
    #                     , 19)
    # urls_xinguan = find_urls(news_manager,
    #                          "https://s.weibo.com/weibo?q=%E6%96%B0%E5%86%A0&xsort=hot&suball=1&timescope=custom:2020-01-23-0:2020-02-07-23&Refer=SWeibo_box"
    #                          , 19)
    # urls_wuhan = find_urls(news_manager,
    #                        "https://s.weibo.com/weibo?q=%E6%AD%A6%E6%B1%89&xsort=hot&suball=1&timescope=custom:2020-01-23-0:2020-02-07-23&Refer=SWeibo_box"
    #                        , 19)
    # urls_bingli = find_urls(news_manager,
    #                         "https://s.weibo.com/weibo?q=%E7%97%85%E4%BE%8B&xsort=hot&suball=1&timescope=custom:2020-01-23-0:2020-02-07-23&Refer=SWeibo_box"
    #                         , 18)
    # urls_zhengzhuang = find_urls(news_manager,
    #                              "https://s.weibo.com/weibo?q=%E7%97%87%E7%8A%B6&xsort=hot&suball=1&timescope=custom:2020-01-23-0:2020-02-07-23&Refer=SWeibo_box"
    #                              , 19)
    # urls_quezhen = find_urls(news_manager,
    #                          "https://s.weibo.com/weibo?q=%E7%A1%AE%E8%AF%8A&xsort=hot&suball=1&timescope=custom:2020-01-23-0:2020-02-07-23&Refer=SWeibo_box"
    #                          , 19)

    # 第三阶段
    # urls_feiyan = find_urls(news_manager,
    #                         "https://s.weibo.com/weibo/%25E8%2582%25BA%25E7%2582%258E?q=%E8%82%BA%E7%82%8E&xsort=hot&suball=1&timescope=custom:2020-02-10-0:2020-02-13-23&Refer=g"
    #                         , 19)
    # urls_yi = find_urls(news_manager,
    #                     "https://s.weibo.com/weibo?q=%E7%96%AB&xsort=hot&suball=1&timescope=custom:2020-02-10-0:2020-02-13-23&Refer=SWeibo_box"
    #                     , 19)
    # urls_xinguan = find_urls(news_manager,
    #                          "https://s.weibo.com/weibo?q=%E6%96%B0%E5%86%A0&xsort=hot&suball=1&timescope=custom:2020-02-10-0:2020-02-13-23&Refer=SWeibo_box"
    #                          , 15)
    # urls_wuhan = find_urls(news_manager,
    #                        "https://s.weibo.com/weibo?q=%E6%AD%A6%E6%B1%89&xsort=hot&suball=1&timescope=custom:2020-02-10-0:2020-02-13-23&Refer=SWeibo_box"
    #                        , 19)
    # urls_bingli = find_urls(news_manager,
    #                         "https://s.weibo.com/weibo?q=%E7%97%85%E4%BE%8B&xsort=hot&suball=1&timescope=custom:2020-02-10-0:2020-02-13-23&Refer=SWeibo_box"
    #                         , 19)
    # urls_zhengzhuang = find_urls(news_manager,
    #                              "https://s.weibo.com/weibo?q=%E7%97%87%E7%8A%B6&xsort=hot&suball=1&timescope=custom:2020-02-10-0:2020-02-13-23&Refer=SWeibo_box"
    #                              , 19)
    # urls_quezhen = find_urls(news_manager,
    #                          "https://s.weibo.com/weibo?q=%E7%A1%AE%E8%AF%8A&xsort=hot&suball=1&timescope=custom:2020-02-10-0:2020-02-13-23&Refer=SWeibo_box"
    #                          , 19)

    # 第四阶段
    # urls_feiyan = find_urls(news_manager,
    #                         "https://s.weibo.com/weibo?q=%E8%82%BA%E7%82%8E&xsort=hot&suball=1&timescope=custom:2020-03-10:2020-06-30&Refer=SWeibo_box"
    #                         , 19)
    # urls_yi = find_urls(news_manager,
    #                     "https://s.weibo.com/weibo?q=%E7%96%AB&xsort=hot&suball=1&timescope=custom:2020-03-10:2020-06-30&Refer=SWeibo_box"
    #                     , 19)
    # urls_xinguan = find_urls(news_manager,
    #                          "https://s.weibo.com/weibo?q=%E6%96%B0%E5%86%A0&xsort=hot&suball=1&timescope=custom:2020-03-10:2020-06-30&Refer=SWeibo_box"
    #                          , 18)
    # urls_wuhan = find_urls(news_manager,
    #                        "https://s.weibo.com/weibo?q=%E6%AD%A6%E6%B1%89&xsort=hot&suball=1&timescope=custom:2020-03-10:2020-06-30&Refer=SWeibo_box"
    #                        , 17)
    # urls_bingli = find_urls(news_manager,
    #                         "https://s.weibo.com/weibo?q=%E7%97%85%E4%BE%8B&xsort=hot&suball=1&timescope=custom:2020-03-10:2020-06-30&Refer=g"
    #                         , 19)
    # urls_zhengzhuang = find_urls(news_manager,
    #                              "https://s.weibo.com/weibo/%25E7%2597%2587%25E7%258A%25B6?q=%E7%97%87%E7%8A%B6&xsort=hot&suball=1&timescope=custom:2020-03-10:2020-06-30&Refer=g"
    #                         , 19)
    # urls_quezhen = find_urls(news_manager,
    #                          "https://s.weibo.com/weibo?q=%E7%A1%AE%E8%AF%8A&xsort=hot&suball=1&timescope=custom:2020-03-10:2020-06-30&Refer=SWeibo_box"
    #                          , 19)

    urls = list(set(urls_feiyan + urls_yi + urls_xinguan + urls_wuhan + urls_bingli + urls_zhengzhuang + urls_quezhen))

    print(len(urls))
    last_res = []
    # return NewsParser.run(get_one, urls)
    for url in urls:
        # print(url)
        res = []
        get_one(news_manager, url, res)
        last_res.append(res)
    news_manager.close()
    return last_res


if __name__ == '__main__':
    final_res = get_all()
    row = ("topic", "time", "url", "comment")
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)
    # rb = xlrd.open_workbook(r'weibo-第四阶段.xlsx')
    # book = xl_copy(rb)
    # book = openpyxl.load_workbook(r'weibo-第四阶段.xlsx')
    i = 0
    for cur in final_res:
        # sheet = book.create_sheet("微博%d" % i)
        sheet = book.add_sheet("微博%d" % i)
        i += 1
        sheet.write(0, 0, row[0])
        sheet.write(1, 0, row[1])
        sheet.write(2, 0, row[2])
        sheet.write(3, 0, row[3])
        sheet.write(0, 1, cur[0])
        sheet.write(1, 1, cur[1])
        sheet.write(2, 1, cur[2])
        comment_num = 0
        for comment in cur[3]:
            if comment is not "：" and comment is not "等人" and comment is not ":":
                sheet.write(3 + comment_num, 1, comment)
                comment_num += 1
    # book.save("weibo-第四阶段.xls")
    # book.save("weibo-第三阶段.xls")
    # book.save("weibo-第二阶段.xls")
    book.save("weibo-第一阶段.xls")

    # for cur in final_res:
    #     print(cur[0], cur[1], cur[2])
    #     for comment in cur[3]:
    #         # print(comment.replace("：",""))
    #         print(comment)
