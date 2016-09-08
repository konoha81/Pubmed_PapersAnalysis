#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from tqdm import tqdm
from time import sleep
import xml.etree.ElementTree as ET
import json, requests, csv


"""
説明！！！

論文タイトル, PMID, 年, 月, キーワード（ ";" 区切り）
をそれぞれ取得して csv形式で出力。

eSearch API を利用
http://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.ESearch


【参考】
Hacking on the Pubmed API
http://www.fredtrotter.com/2014/11/14/hacking-on-the-pubmed-api/


"""


def fetch_PMID():
	""" JSONから対象termを含む論文のPMIDを取得する """

	term = "JAMIA[TA]"
	retmax = "1000"

	url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed"\
	"&term={term}&retmode=json&retmax={retmax}".format(term=term, retmax=retmax)
	jsonString = requests.get(url).text
	data = json.loads(jsonString)
	PMID_list = data['esearchresult']['idlist']

	return PMID_list, retmax


def fetch_data(PMID):
	""" 指定PMIDの情報をXMLから抽出してリストに入れる  """

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

	return data_list



if __name__ == '__main__':


	#print("")
	#query = input()


	PMID_list, retmax = fetch_PMID()

	pbar = tqdm(total=int(retmax)) # 進捗を表示する

	with open('JAMIA_data.csv', 'a') as f: # ヘッダーを書き込む
		writer = csv.writer(f, lineterminator='\n')
		writer.writerow(["Title", "PMID", "Year", "Month", "Keywords"])

	for i,j in enumerate(PMID_list):
		data_list = fetch_data(j)
				
		with open('JAMIA_data.csv', 'a') as f:
			writer = csv.writer(f, lineterminator='\n')
			writer.writerow(data_list)

		pbar.update(1)
		sleep(0.1)
	pbar.close()
	print("Finish!")

