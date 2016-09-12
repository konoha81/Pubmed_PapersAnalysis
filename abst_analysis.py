# -*- coding: utf-8 -*- 

"""

参考

PythonでBag of WordsとSVMを使ったタイトルのカテゴリ分類
http://stmind.hatenablog.com/entry/2013/11/04/164608

"""

#!/usr/bin/env python

import gensim, csv, re
import gensim.parsing


def make_dictionary(preprocessed, dct_txt):
	""" 取得したアブストから辞書を作成し、低頻度および高頻度の単語を除いて保存する  """
	
	dct = gensim.corpora.Dictionary(preprocessed)
	unfiltered = dct.token2id.keys()
	dct.filter_extremes(no_below=5, no_above=0.6)
	filtered = dct.token2id.keys()
	filtered_out = set(unfiltered) - set(filtered)

	print("\nThe following super common/rare words are filtered out...")
	#print(list(filtered_out),'\n')
	print('The filtered result: ',len(unfiltered), '-', len(filtered_out), '=', len(filtered), 'words.')

	print("Save Dictionary...")

	dct.save_as_text(dct_txt)
	print("		saved to {}".format(dct_txt))



if __name__ == '__main__':

	# 読みとるcsvファイルの名前
	filename = "JAMIA_data6.csv"
	# 解析対象の年
	year = "2014"
	
	f = open(filename, 'r', encoding='utf-8')
	doc =  csv.reader(f)

	# 指定した年のアブストを取得する
	documents = []
	documents.extend([i[5] for i in doc if i[2] == year and i[5] != 'NaN' ])
	
	# トークン化 & ストップワードの除去 & ステミング
	preprocessed = []
	for i,j in enumerate(documents):
		preprocessed.append(gensim.parsing.preprocess_string(documents[i]))

	# 保存する辞書の名前
	dct_txt = ("id2word_" + year + ".txt")
	make_dictionary(preprocessed, dct_txt)

	# 作成済みの辞書を読み込む
	dct = gensim.corpora.Dictionary.load_from_text(dct_txt)

	#print(dct.token2id.keys())

	# 特徴ベクトルの集合を作る
	corpus = [dct.doc2bow(text) for text in preprocessed]

	# TF-IDF
	tfidf = gensim.models.TfidfModel(corpus)
	corpus_tfidf = tfidf[corpus]

	#for doc in corpus_tfidf:
	#	print(doc)


	#with open(filename, 'w') as f: 

	# LSIによるトピックモデルの生成
	num_topics = 10
	lsi = gensim.models.lsimodel.LsiModel(corpus=corpus_tfidf, num_topics=num_topics, id2word=dct)
	corpus_lsi = lsi[corpus_tfidf]

	lsi_index = gensim.similarities.MatrixSimilarity(lsi[corpus_tfidf])

	#for doc in corpus_lsi:
	#		print(doc)

	print(lsi.print_topics())



