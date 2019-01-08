# -*- coding: utf-8 -*-
"""
语料库的读取：
语料库的预处理：
特征选取：
生成训练数据：
"""
import re


class Corpus:
    _maps = {
        u't':u'T',
        u'nr':u'PER',
        u'ns':u'LOC',
        u'nt':u'ORG',

    }
    #u'ev': u'EVENT'
    train_corpus_path = 'data/rmrb199801.txt'
    process_corpus_path = 'data/rmrb.txt'

##预处理语料库 ---只针对人民日报词性语料库
    @classmethod
    def pre_process(cls):
        lines = cls.read_corpus_from_file(cls.train_corpus_path)
        new_lines = []
        for line in lines:
            words = cls.q_to_b(line.strip()).split(u' ')  # 全角转半角
            pro_words = cls.time_preprocess(words)
            pro_words = cls.nr_preprocess(pro_words)
            pro_words = cls.k_preprocess(pro_words)
            ##todo event
            #pro_words = cls.event_preprocess(pro_words)
            new_lines.append('  '.join(pro_words[1:]))
            cls.write_corpus_to_file(data='\n'.join(new_lines), file_path=cls.process_corpus_path)

    @classmethod
    def initialize(cls):
        processed_corpus_path = cls.process_corpus_path
        lines = cls.read_corpus_from_file(processed_corpus_path)
        words_list = [line.strip().split(' ') for line in lines if line.strip()]
        del lines
        cls.init_sequence(words_list)


    @classmethod
    def init_sequence(cls,words_list):
        words_list = cls.space_preprocess(words_list)
        words_seq = [[word.split(u'/')[0] for word in words] for words in words_list]
        pos_seq = [[word.split(u'/')[1] for word in words] for words in words_list]
        tag_seq = [[cls.pos_to_tag(p) for p in pos] for pos in pos_seq]
        cls.pos_seq = [[[pos_seq[index][i] for _ in range(len(words_seq[index][i]))]
                        for i in range(len(pos_seq[index]))] for index in range(len(pos_seq))]
        cls.tag_seq = [[[cls.tag_perform(tag_seq[index][i], w) for w in range(len(words_seq[index][i]))]
                        for i in range(len(tag_seq[index]))] for index in range(len(tag_seq))]
        cls.pos_seq = [[u'un'] + [cls.pos_perform(p) for pos in pos_seq for p in pos] + [u'un'] for pos_seq in
                       cls.pos_seq]
        cls.tag_seq = [[t for tag in tag_seq for t in tag] for tag_seq in cls.tag_seq]

        cls.word_seq = [[u'<BOS>'] + [w for word in word_seq for w in word] + [u'<EOS>'] for word_seq in words_seq]

    @classmethod
    def segment_by_window(cls, words_list=None, window=3):
        """
        窗口切分
        """
        words = []
        begin, end = 0, window
        for _ in range(1, len(words_list)):
            if end > len(words_list): break
            words.append(words_list[begin:end])
            begin = begin + 1
            end = end + 1
        return words


    @classmethod
    def extract_feature(cls, word_grams):
        """
        特征选取
        """
        features, feature_list = [], []
        for index in range(len(word_grams)):
            for i in range(len(word_grams[index])):
                word_gram = word_grams[index][i]
                #todo 模版设计
                feature = {u'w-1': word_gram[0],
                           u'w': word_gram[1],
                           u'w+1': word_gram[2],
                           u'w-1:w': word_gram[0] + word_gram[1],
                           u'w:w+1': word_gram[1] + word_gram[2],
                           u'bias': 1.0}
                feature_list.append(feature)
            features.append(feature_list)
            feature_list = []
        return features

    @classmethod
    def generator(cls):
        """
        训练数据
        """
        word_grams = [cls.segment_by_window(word_list) for word_list in cls.word_seq]
        features = cls.extract_feature(word_grams)
        #todo change here
        return features, cls.tag_seq


    @classmethod
    def pos_perform(cls, pos):
        """
        去除词性携带的标签先验知识
        """
        if pos in cls._maps.keys() and pos != u't':
            return u'n'
        else:
            return pos

    @classmethod
    def tag_perform(cls, tag, index):
        """
        标签种类
        """
        if(index == 0 and tag != u'O'):
            return u'B_{}'.format(tag)
        elif(tag != u'O'):
            return u'I_{}'.format(tag)
        else:
            return tag


    @classmethod
    def pos_to_tag(cls,p):
        t = cls._maps.get(p,None)
        return t if t else u'O'


##处理大粒度分词
    @classmethod
    def k_preprocess(cls, words):
        """
        处理大粒度分词
        """
        pro_words = []
        flag = 0
        temp = u''
        for word in words:
            if (u'[' in word and flag == 0):
                word = word.replace(u'[', u'')
                word = re.sub(u'/[a-zA-Z]*', u'', string=word)
                flag = 1
                temp += word
            elif (flag == 1 and u']' not in word):
                word = re.sub(u'/[a-zA-Z]*', u'', string=word)
                temp += word
            elif (u']' in word):
                word = re.sub(u'/[a-zA-Z]*]', u'/', string=word)
                temp += word
                flag = 0
                pro_words.append(temp)
                temp = u''
            else:
                pro_words.append(word)
        return pro_words

##处理空格
    @classmethod
    def space_preprocess(cls, words_list):
        """
        处理大粒度分词
        """
        pro_words_list = []
        for words in words_list:
            pro_words = []
            for word in words:
                if (word == u''):
                    continue
                else:
                    pro_words.append(word)
            pro_words_list.append(pro_words)
        return pro_words_list

##处理姓名
    @classmethod
    def nr_preprocess(cls, words):
        """
            处理姓名
        """
        pro_words = []
        temp = u''
        for word in words:
            if (u'/nr' not in word and temp != u''):
                if (word == ''):
                    continue
                else:
                    pro_words.append(temp + u'/nr')
                    temp = u''
                    pro_words.append('')
                    pro_words.append(word)
            elif (u'/nr' not in word and temp == u''):
                pro_words.append(word)
            elif (u'/nr' in word):
                word = word.replace(u'/nr', u'')
                temp = temp + word
        if (temp != u''):
            pro_words.append(temp + u'/nr')
        return pro_words


## 处理时间
    @classmethod
    def time_preprocess(cls, words):
        pro_words = []
        temp = u''
        for word in words:
            if (u'/t' not in word and temp != u''):
                if (word == ''):
                    continue
                else:
                    pro_words.append(temp + u'/t')
                    temp = u''
                    pro_words.append('')
                    pro_words.append(word)
            elif (u'/t' not in word and temp == u''):
                pro_words.append(word)
            elif (u'/t' in word):
                word = word.replace(u'/t', u'')
                temp = temp + word
        if (temp != u''):
            pro_words.append(temp + u'/t')
        return pro_words

###todo 处理事件
    @classmethod
    def event_preprocess(cls, words):
        pro_words = []
        temp = u''
        index = 0
        while (index < len(words)-2):
            word = words[index]
            next_word = words[index+2]
            if(u'/v' in word and u'/n' in next_word):
                word = word.replace(u'/v',u'')
                next_word = next_word.replace(u'/n',u'/ev')
                temp = word+next_word
                pro_words.append(temp)
                index = index + 3
            else:
                pro_words.append(word)
                index = index + 1
        return pro_words

##全角转半角
    @classmethod
    def q_to_b(cls, q_str):
        """全角转半角"""
        b_str = ""
        for uchar in q_str:
            inside_code = ord(uchar)
            if inside_code == 12288:  # 全角空格直接转换
                inside_code = 32
            elif 65374 >= inside_code >= 65281:  # 全角字符（除空格）根据关系转化
                inside_code -= 65248
            b_str += chr(inside_code)
        return b_str


###半角转全角
    @classmethod
    def b_to_q(cls, b_str):
        """半角转全角"""
        q_str = ""
        for uchar in b_str:
            inside_code = ord(uchar)
            if inside_code == 32:  # 半角空格直接转化
                inside_code = 12288
            elif 126 >= inside_code >= 32:  # 半角字符（除空格）根据关系转化
                inside_code += 65248
            q_str += chr(inside_code)
        return q_str

###读取语料
    @classmethod
    def read_corpus_from_file(cls, file_path):
        """
        读取语料
        """

        f = open(file_path, 'r',encoding='UTF-8')
        lines = f.readlines()
        f.close()
        return lines

###写语料
    @classmethod
    def write_corpus_to_file(cls, data, file_path):
        """
        写语料
        """
        f = open(file_path, 'w',encoding='UTF-8')
        f.write(data)
        f.close()





if __name__ == '__main__':
    test_corpus = Corpus
    test_corpus.pre_process()
    print('finish')