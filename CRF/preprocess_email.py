#coding: utf-8

"""
处理邮件中的事件信息以及代词等
"""

import time
import jieba.posseg as pseg

def process(lines):
    # file_path = 'data/test.txt'
    # f = open(file_path, 'r', encoding='UTF-8')
    # lines = f.readlines()
    # f.close()
    if(len(lines)<3):
        raise Exception(" the email is NULL ")

    receiver = ''
    words = pseg.cut(lines[0])
    for word, flag in words:
        if(flag == 'nr'):
            receiver += word
    sender = lines[len(lines)-1].strip()
    content = ''
    for i in range(1, len(lines)-1):
        content += lines[i]

    content = content.replace('我们', receiver + '和' + sender)
    content = content.replace('我', sender)
    content = content.replace('你', receiver)
    content = content.replace('您', receiver)

    if('我' not in content and '你' not in content and '您' not in content and '我们' not in content):
        content = receiver + content.strip()
    localtime = time.localtime()
    if('明天' in content):
        date = str((localtime.tm_mon))+ '月' + str(localtime.tm_mday) + '日'
        content = content.replace('明天', date)
    if('今天' in content):
        date = str((localtime.tm_mon)) + '月' + str(localtime.tm_mday-1) + '日'
        content = content.replace('今天', date)

    return content
def main():
    process()
if __name__ == '__main__':
    main()