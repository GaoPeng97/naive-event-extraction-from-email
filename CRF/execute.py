# -*- coding: utf-8 -*-
import sys
from corpus import Corpus
from model import CrfModel
from calendar_api import insert_event
import preprocess_email
import time
def pre_process():
    """
    抽取语料特征
    """
    corpus = Corpus()
    corpus.pre_process()

def train():
    """
    训练模型
    """
    model = CrfModel()
    model.train()

def recognize(temp_path, label_path):
    """
    命名实体识别
    """
    model = CrfModel()
    for i in range(0, 100, 1):
        file_path = temp_path+'/' + str(i).zfill(2)+'.txt'
        f = open(file_path, 'r', encoding='GBK')
        lines = f.readlines()
        f.close()
        label_file_path = label_path +'/' + str(i).zfill(2)+'_label.txt'
        f = open(label_file_path, 'r', encoding='GBK')
        label_lines = f.readlines()
        f.close()
        sentence = preprocess_email.process(lines)
        result = model.predict(sentence)

        write_path =  'result/email_result.txt'
        if(i == 0):
            f = open(write_path, 'w', encoding='UTF-8')
        else:
            f = open(write_path, 'a', encoding='UTF-8')
        f.writelines(str(i)+'\n')
        f.writelines(lines)
        f.writelines('\n')
        f.writelines('label\n')
        f.writelines(label_lines)
        f.writelines('\n')
        f.writelines('result\n')
        f.writelines(str(result)+'\n')
        f.writelines('\n')
        f.close()

    return

def insert_calendar():
    localtime = time.localtime()
    entity={}
    entity['EVENT'] = 'test'
    entity['PER']='mike'
    entity['T'] = str(localtime.tm_year)+'-'+str(localtime.tm_mon)+'-'+ str(localtime.tm_mday)+'T09:00:00-07:00'
    entity['LOC'] = 'Building 3'
    insert_event(entity)


if __name__ == '__main__':
    arg = sys.argv[1]
    if (arg == 'train'):
        train()
    elif (arg == 'process'):
        pre_process()
    elif (arg == 'recognize'):
        file_path = sys.argv[2]
        label_path = sys.argv[3]
        if(file_path == '' or label_path == ''):
            print('input file path and label path \n')
            sys.exit()
        else:
             recognize(file_path, label_path)
    elif (arg == 'test_calendar'):
        insert_calendar()

    else:
        print('Args must in ["process", "train", "recongize","test_calendar"].')
    sys.exit()