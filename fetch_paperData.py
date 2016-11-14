# -*- coding: utf-8 -*- 


"""
説明

論文タイトル, PMID, 年, 月, キーワード（ ";" 区切り）, アブストラクト
をそれぞれ取得して csv形式で出力。

eSearch API を利用
http://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.ESearch

取得枚数の指定（retmax）は最大10万件まで可能。
それ以上の取得や、途中で切断された場合には、retstartに再開する値をセットする。


【参考】
Hacking on the Pubmed API
http://www.fredtrotter.com/2014/11/14/hacking-on-the-pubmed-api/


"""

#!/usr/bin/env python

from tqdm import tqdm
from time import sleep
import xml.etree.ElementTree as ET
import json, requests, csv, codecs



def fetch_PMID(term, retmax, retstart):
	""" JSONから対象termを含む論文のPMIDを取得する """

	url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed"\
	"&term={term}&retmode=json&retmax={retmax}&retstart={retstart}".format(term=term, retmax=retmax, retstart=retstart)
	jsonString = requests.get(url).text
	data = json.loads(jsonString)
	PMID_list = data['esearchresult']['idlist']

	return PMID_list


def fetch_data(PMID):
	""" 指定PMIDの論文情報をXMLから抽出する  """

	# リストを初期化
	data_list = []

	url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed"\
	"&retmode=xml&rettype=abstract&id={PMID}".format(PMID=PMID)
	string = requests.get(url).text
	root = ET.fromstring(string)

	# 論文のタイトルを追加
	title = root.find('.//ArticleTitle').text
	data_list.append(title)

	#PMIDを追加
	data_list.append(PMID)

	# 論文の年月を追加
	Year = root.find('.//DateCreated/Year').text
	Month = root.find('.//DateCreated/Month').text
	data_list.append(Year)
	data_list.append(Month)

	# 論文のキーワードを追加
	keyword_list = []
	if root.find('.//Keyword') is not None: 
		for keywords in root.iter('Keyword'):
			keyword_list.append(keywords.text)
	else:
		keyword_list.append("NaN") # keywordsがない場合は"NaN"をリストに代入する

	data_list.append('; '.join(keyword_list)) # keywordsリストを ";" 区切りにしてリストへ追加


	# 論文のアブストラクトを追加
	abstract_list = []
	if root.find('.//AbstractText') is not None: 
		for abst in root.iter('AbstractText'):
				abstract_list.append(abst.text)
	else:
		abstract_list.append("NaN") # abstractがない場合は"NaN"をリストに代入する


	data_list.append(''.join(abstract_list))

	return data_list



if __name__ == '__main__':

	term = "JAMIA[TA]"
	retmax = 50
	retstart = 0

	filename= 'JAMIA_data_test.csv'

	PMID_list = fetch_PMID(term, retmax, retstart)

	# 進捗を表示する
	pbar = tqdm(total=retmax-retstart) 


	# ヘッダーを書き込む
	with open(filename, 'w') as f: 
		writer = csv.writer(f, lineterminator='\n')
		writer.writerow(["Title", "PMID", "Year", "Month", "Keywords", "Abstract"])


	for i,j in enumerate(PMID_list):
		data_list = fetch_data(j)
		
		with open(filename, 'w') as f:
			writer = csv.writer(f, lineterminator='\n')
			writer.writerow(data_list)

		pbar.update(1)
		sleep(0.1)

	
	fin = codecs.open(filename, "r")
	fout_utf = codecs.open("test2.csv", "a", "utf-8")
	for row in fin:
		fout_utf.write(row)
	fin.close()
	fout_utf.close()
	

	pbar.close()

	print("Finish!")

