# -*- coding: utf-8 -*-
"""
模型的初始化：
模型的训练：
模型的预测：
模型的保存：
模型的读取：
"""


import sklearn_crfsuite
from sklearn_crfsuite import metrics
import sklearn.externals.joblib as joblib
from corpus import Corpus

import sys
sys.path.append('..')
import tfidf

class CrfModel:

    def __init__(self):
        self.corpus = Corpus
        self.corpus.initialize()

        #模型参数预设
        self.CRF_algorithm = 'lbfgs'
        self.c1 = 0.1
        self.c2 = 0.1
        self.max_iterations = 100

        #模型存储路径
        self.model_path = 'data/{}.pkl'

    def train(self):
        self.model = sklearn_crfsuite.CRF(algorithm= self.CRF_algorithm, c1=self.c1, c2=self.c2,
                                          max_iterations=self.max_iterations, all_possible_transitions=True)
        features, tags = self.corpus.generator()
        x_train, y_train = features[500:], tags[500:]
        x_test, y_test = features[:500], tags[:500]
        self.model.fit(x_train, y_train)
        labels = list(self.model.classes_)
        print(labels)
        labels.remove('O')
        y_predict = self.model.predict(x_test)
        metrics.flat_f1_score(y_test, y_predict, average='weighted', labels=labels)
        sorted_labels = sorted(labels, key=lambda name: (name[1:], name[0]))
        print(metrics.flat_classification_report(y_test, y_predict, labels=sorted_labels, digits=3))
        self.save_model()

    def predict(self, sentence):
        """
        预测
        """
        self.load_model()
        u_sent = Corpus.q_to_b(sentence)
        word_lists = [[u'<BOS>']+[c for c in u_sent]+[u'<EOS>']]
        word_grams = [self.corpus.segment_by_window(word_list) for word_list in word_lists]
        features = self.corpus.extract_feature(word_grams)
        y_predict = self.model.predict(features)

        all_entity=''
        test_entity = {
            'LOC': '',
            'T':'',
            'ORG':'',
            'PER':'',
            'EVENT':''
        }
        for index in range(len(y_predict[0])):
            flag = 1
            temp_word = y_predict[0][index]
            if('LOC' in temp_word):
                if('B' in temp_word):
                    test_entity['LOC'] += ' '
                test_entity['LOC'] += u_sent[index]

            elif('T' in temp_word):
                if('B' in temp_word):
                    test_entity['T'] += ' '
                test_entity['T'] += u_sent[index]

            elif ('PER' in temp_word):
                if('B' in temp_word):
                    test_entity['PER'] += ' '
                if( u_sent[index] not in test_entity['PER']):
                    test_entity['PER'] += u_sent[index]

            elif ('ORG' in temp_word):
                if('B' in temp_word):
                    test_entity['ORG'] += ' '
                test_entity['ORG'] += u_sent[index]

            elif ('EVENT' in temp_word):
                if('B' in temp_word):
                    test_entity['EVENT'] += ' '
                test_entity['EVENT'] += u_sent[index]
            else:
                flag = 0

            if(flag == 1):
                all_entity += u_sent[index]
        #######################################################################################
        #tfidf  extract keyword
        if (test_entity['LOC'] == ""):
            event_key = tfidf.extract_tags(sentence, topK=1, withWeight=True, allowPOS=('ns'))
            for item in event_key:
                if(item[1] > 5):
                   test_entity['LOC'] += item[0]
                   all_entity += item[0]
                break

        keywords = tfidf.extract_tags(sentence, topK=20, withWeight=True, allowPOS = ('n','vn','v'))    #'n','vn','v'
        for item in keywords:
            if(item[0] not in all_entity):
                test_entity['EVENT'] += item[0]
                break

        ########################################################################################
        return test_entity

    def load_model(self, name='model'):
        """
        加载模型
        """
        model_path = self.model_path.format(name)
        self.model = joblib.load(model_path)

    def save_model(self, name='model'):
        """
        保存模型
        """
        model_path = self.model_path.format(name)
        joblib.dump(self.model, model_path)