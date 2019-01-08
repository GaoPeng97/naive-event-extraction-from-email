#coding=utf-8
import nltk
import numpy
import os

class HMM(object):
	"""docstring for HMM"""
	def __init__(self,corpus_path):
		self.corpus_path = corpus_path
		#状态转移矩阵：0：非实体词；123：location; 456:time; 789:PERSON; 10 11 12:organization
		self.trans_prob = {'O': {},'B_LOCATION': {},'M_LOCATION': {},'E_LOCATION': {},'B_TIME': {},
							'M_TIME': {},'E_TIME': {},'B_PERSON': {},'M_PERSON': {},'E_PERSON': {},'W_PERSON': {},
							'B_ORGANIZATION': {},'M_ORGANIZATION': {},'E_ORGANIZATION': {}}
		#发射矩阵
		self.emiss_prob = {'O': {},'B_LOCATION': {},'M_LOCATION': {},'E_LOCATION': {},'B_TIME': {},
							'M_TIME': {},'E_TIME': {},'B_PERSON': {},'M_PERSON': {},'E_PERSON': {},'W_PERSON': {},
							'B_ORGANIZATION': {},'M_ORGANIZATION': {},'E_ORGANIZATION': {}}

		self.states = ('O', 'B_LOCATION', 'M_LOCATION', 'E_LOCATION', 'B_TIME', 'M_TIME', 'E_TIME',
						 'B_PERSON', 'M_PERSON', 'E_PERSON', 'W_PERSON','B_ORGANIZATION', 'M_ORGANIZATION', 'E_ORGANIZATION')
		self.init_prob()


	def get_word_tag(self):
		'''
		读取语料库中的词和标注
		'''
		rf = open(self.corpus_path, 'rb')
		lines = rf.readlines()
		word_tag_list = []
		for line in lines:
			line = line.decode('utf-8')
			line = line.replace('\n','').replace('\r','')
			word_tag = line.split('\t')
			if len(word_tag) == 2:
				word_tag_list.append((word_tag[0],word_tag[1]))
		rf.close()
		'''
		wf = open('word_tag.txt','w+')
		for word_tag in word_tag_list:
			wf.write(str(word_tag[0]))
			wf.write(str(word_tag[1]))
			wf.write('\n')
		wf.close()
		'''
		return word_tag_list


	def get_tag_tag(self,word_tag_list):
		'''
		读取tag的状态转移
		'''
		tag_tag_list = []
		for i in range(len(word_tag_list)-1):
			forward_tag = word_tag_list[i][1]
			backward_tag = word_tag_list[i+1][1]
			tag_tag_list.append((forward_tag,backward_tag))
		'''
		wf = open('tag_tag.txt','w+')
		for tag_tag in tag_tag_list:
			wf.write(str(tag_tag[0]))
			wf.write(str(tag_tag[1]))
			wf.write('\n')
		wf.close()
		'''
		return tag_tag_list


	def get_words(self,word_tag_list):
		"""
		读取语料库中的全部字
		"""
		wf = open('word.txt','w+')
		words = []
		for w, t in word_tag_list:
			words.append(w)
		only_words = set(words)
		for word in only_words:
			wf.write(word + ' ')
		wf.close()


	def load_words(self):
		'''
		加载字典
		'''
		rf = open('word.txt', 'r+')
		lines = rf.readlines()
		words = []
		for line in lines:
			#line = line.decode("utf-8")
			words = line.split(" ")
		return words


	def init_prob(self):
		'''
		初始化转移概率和发射概率
		'''
		word_tag_list = self.get_word_tag()
		tag_tag_list = self.get_tag_tag(word_tag_list)
		self.get_words(word_tag_list)
		words = self.load_words()
		for state0 in self.states:
			for state1 in self.states:
				self.trans_prob[state0][state1] = 0
			for word in words:
				self.emiss_prob[state0][word] = 0
		self.get_start_prob(word_tag_list)
		self.get_transition_probability(tag_tag_list)
		self.get_emission_probability(word_tag_list)


	def get_start_prob(self,word_tag_list):
		"""
		开始概率：标注的初始概率
		:param word_tag_list:
		:return:
		"""
		wf = open('start_prob.txt','w+')
		fdist = nltk.FreqDist(t for w, t in word_tag_list)
		for key, value in fdist.items():
			wf.write(key +' '+ str(value) +' ' + str(fdist.freq(key)))
			wf.write('\n')
		wf.close()


	def load_start_profortransemi(self, path='start_prob.txt'):
		"""
		用于计算转移概率 发射概率的格式封装，便于计算
		:param path:
		:return:
		"""
		start_prob = {}
		rf = open(path, 'r+')
		lines = rf.readlines()
		for line in lines:
			line = line.replace("\n", '')
			#line = line.decode("utf-8")
			tag_pro = line.split(" ")
			start_prob[tag_pro[0]] = [eval(tag_pro[1]), eval(tag_pro[2])]
		return start_prob


	def get_emission_probability(self, word_tag_list):
		"""
		获取发射概率，字对应的标注的概率
		:param words:
		:param word_tag_list:
		
		:return:
		"""
		start_pro = self.load_start_profortransemi()
		wf = open('emiss_prob.txt', 'w+')
		fdist = nltk.FreqDist(word_tag_list)
		for key, value in fdist.items():
			#print key[1], key[0], value, fdist.freq(key) / start_pro[key[1]][0]
			wf.write(key[1] + ' ' + key[0] + ' ' + str(value) + ' ' + str(fdist.freq(key) / start_pro[key[1]][0]))
			wf.write('\n')
		wf.close()


	def get_transition_probability(self, tag_tag_list):
		"""
		获取转移概率 前标注转移下一个标注的概率
		:param tag_tag_list:
		:return:
		"""
		wf = open('trans_prob.txt','w+')
		start_pro = self.load_start_profortransemi()
		fdist = nltk.FreqDist(tag_tag_list)
		for key, value in fdist.items():
			condition_pro2 = value*1.00 / start_pro[key[0]][0]
			#print '频率/频率的条件概率', key[0], key[1], value, condition_pro2
			wf.write(key[0]+' '+key[1]+' '+str(value)+' '+str(condition_pro2))
			wf.write('\n')
		wf.close()


	def load_transition_pro(self, path='trans_prob.txt'):
		"""
		hmm 维特比计算的时候，转移概率的封装
		:param path:
		:return:
		"""
		rf = open(path, 'r+')
		lines = rf.readlines()
		for line in lines:
			line = line.replace("\n", '')
			#line = line.decode("utf-8")
			tag_totag_pro = line.split(" ")
			self.trans_prob[tag_totag_pro[0]][tag_totag_pro[1]] = eval(tag_totag_pro[3])
		return self.trans_prob


	def load_emission_pro(self, path='emiss_prob.txt'):
		"""
		hmm 维特比计算的时候，发射概率的格式封装
		:param path:
		:return:
		"""
		rf = open(path, 'r')
		lines = rf.readlines()
		for line in lines:
			line = line.replace("\n", '')
			#line = line.decode("utf-8")
			tag_toword_pro = line.split(" ")
			# print tag_toword_pro
			self.emiss_prob[tag_toword_pro[0]][tag_toword_pro[1]] = eval(tag_toword_pro[3])
		return self.emiss_prob


	def load_start_pro(self, path='start_prob.txt'):
		"""
		hmm 维特比计算的时候，初始概率的格式封装
		:param path:
		:return:
		"""
		start_pro = {}
		rf = open(path, 'r')
		lines = rf.readlines()
		for line in lines:
			line = line.replace("\n", '')
			#line = line.decode("utf-8")
			tag_pro = line.split(" ")
			start_pro[tag_pro[0]] = eval(tag_pro[2])
		return start_pro


	def get_observation(self,sentence):
		"""
		unicode格式的观察状态格式
		:param sentence:
		:return:
		"""
		word_list = []
		for i in sentence:
			word_list.append(i)
		return tuple(word_list)