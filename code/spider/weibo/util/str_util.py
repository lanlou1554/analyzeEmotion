from functools import wraps


def remove_sign(tar, sign):
    res = ''
    for cur_char in tar:
        if cur_char != sign:
            res += cur_char
    return res


def single_str_process(string):
    res = ''
    for char in string:
        char = ''.join(char.split())
        res += char
    if len(res) > 0 and res[0] == '：':
        res = res[1:]
    return res


def str_process(func):
    """包装需要处理字符串的函数"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        html_str = func(*args, **kwargs)
        return single_str_process(html_str)

    return wrapper


def str_list_process(func):
    """包装需要处理字符串列表的函数"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        str_list = func(*args, **kwargs)
        res = []
        for cur_str in str_list:
            res.append(single_str_process(cur_str))
        return [x for x in res if x != '']

    return wrapper