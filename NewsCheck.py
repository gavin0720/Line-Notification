import os
import json
import pandas as pd
import jieba
from Swinger import Swinger
import matplotlib.pyplot as plt


class NewsCheck(object):

	crawler_file = 'data'
	keywords = []
	titles = []
	title_and_links = {}

	def __init__(self):
		self.keywords = self.read_keywords()
		self.titles, self.title_and_links = self.read_titles()
		super(NewsCheck, self).__init__()


	def check(this):
		print(this.title_and_links)
		print(this.titles)


	def read_titles(this):
		title_total = []
		title_and_links = {}
		files = os.listdir(this.crawler_file)
		for file in files:
			if file == '.DS_Store' or file == 'record.json' or file == 'user.json':
				continue
			path = os.path.join(this.crawler_file, file)

			with open(path, 'r', encoding='utf-8') as f:
				titles = json.load(f)
				title_and_links = {**title_and_links, **titles}
				title_total += titles.keys()
		return title_total, title_and_links


	def read_keywords(this):
		filename = 'keywords.xlsx'
		df = pd.read_excel(filename)
		keywords = list(df['詞庫'])
		# print(keywords)
		return keywords


	def emotion_plot(this, new_record):
		img_path = 'image/emotion.jpg'
		record_path = os.path.join('data', 'record.json')

		with open(record_path, 'r', encoding='utf-8') as f:
			records = json.load(f)
		if len(records) == 0:
			records.append(new_record)
		else:
			if new_record != records[-1]:
				records.append(new_record)

		x_data = [i*30 for i in range(len(records))]
		y_pos, y_neg = [], []
		for rec in records:
			y_pos.append(rec[0])
			y_neg.append(rec[1])
		plt.plot(x_data, y_pos,'s-', color = 'g', label="Positive")
		plt.plot(x_data, y_neg,'s-', color = 'r', label="Negative")
		plt.xlabel("Minutes Before", fontsize=15)
		plt.ylabel("Numbers of News", fontsize=15)
		plt.legend(loc = "best", fontsize=12)
		# plt.show()

		plt.savefig(img_path)
		with open(record_path, 'w', encoding='utf-8') as f:
			json.dump(records, f, ensure_ascii=False)


	def check_keyword(this):
		titles = []
		links = []
		
		for title in this.titles:
			# get cut result
			seg_list = jieba.cut(title, cut_all=False)
			seg_list = list(seg_list)
			# clean_seg = [seg for seg in seg_list if seg not in del_words and len(seg)>1]
			# print("分詞結果: ", seg_list)

			for seg in seg_list:
				if seg in this.keywords:
					titles.append(title)
					links.append(this.title_and_links[title])
					# print(title)
					break
		return titles, links


	def check_emotion(this):
		pos_count, neg_count = 0, 0
		s = Swinger()
		s.load('LogisticRegression')

		for title in this.titles:
			emotion = s.swing(title)
			if str(emotion) == 'pos':
				pos_count += 1
			elif str(emotion) == 'neg':
				neg_count += 1
			# print(title)
			# print(emotion)
		print(pos_count, neg_count)
		# this.emotion_plot([pos_count, neg_count])
		return {'pos': pos_count, 'neg': neg_count}


	def new_word(this, new):
		filename = 'keywords.xlsx'
		df = pd.read_excel(filename)
		keywords = list(df['詞庫'])

		if new in keywords:
			return 'Duplicate'
		else:
			keywords.append(new)
			new_keyword = {'詞庫': keywords}
			new_keyword = pd.DataFrame(new_keyword)
			new_keyword.to_excel(filename, index=False)
			return 'OK'



# nc = NewsCheck()
# nc.check_emotion()
# nc.check_keyword()
# nc.emotion_plot([50, 10])

