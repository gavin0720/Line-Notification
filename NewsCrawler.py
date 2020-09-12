import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os


class NewsCrawler(object):

	def __init__(self):
		super(NewsCrawler, self).__init__()


	def read_previous(this, website):
		filename = os.path.join('data', website + '.json')
		if os.path.isfile(filename):
			with open(filename, 'r', encoding='utf-8') as f:
				titles = json.load(f)
			os.remove(filename)
		else:
			titles = {}
		return titles


	def write_new_title(this, website, titles):
		filename = os.path.join('data', website + '.json')
		with open(filename, 'w', encoding='utf-8') as f:
			json.dump(titles, f, ensure_ascii=False)


	def chinaNews(this):

		root_url = 'https://www.chinatimes.com'
		url = 'https://www.chinatimes.com/realtimenews/?page={page}&chdtv'
		pre_titles = this.read_previous('chinaNews')
		new_titles = {}

		# go through every pages
		for page in range(1,11):

			html = requests.get(url.format(page=str(page))).text
			html = BeautifulSoup(html, "lxml")

			blocks = html.select('.vertical-list.list-style-none')[0]
			items = blocks.select('li')
			for item in items:
				title = item.select('.title')[0].select('a')[0].text
				link = root_url + item.select('.title')[0].select('a')[0]['href']

				# compare with previous data
				if title not in pre_titles:
					new_titles[title] = link
					print(title)
				else:
					this.write_new_title('chinaNews', new_titles)
					return new_titles

		this.write_new_title('chinaNews', new_titles)
		return new_titles


	def formosa(this):

		root_url = 'https://www.ftvnews.com.tw'
		url = 'https://www.ftvnews.com.tw/tag/快新聞/{page}'
		pre_titles = this.read_previous('formosa')
		new_titles = {}

		# go through every pages
		page = 1
		while True:
			if page > 20:
				break

			html = requests.get(url.format(page=str(page))).text
			html = BeautifulSoup(html, 'lxml')

			items = html.select('.col-lg-4.col-sm-6')
			for item in items:
				title = item.select('.title')[0].text.replace('快新聞／', '')
				link = root_url + item.select('a')[0]['href']
				if title not in pre_titles:
					new_titles[title] = link
					print(title)
				else:
					this.write_new_title('formosa', new_titles)
					return new_titles

			pagiNum = html.select('.pagiNum')[0].text
			pagiNum = pagiNum.split('/')[1]
			pagiNum = int(pagiNum)
			if page == pagiNum:
				break
			else:
				page += 1

		this.write_new_title('formosa', new_titles)
		return new_titles


	def threeStand(this):

		root_url = 'https://www.setn.com'
		url = 'https://www.setn.com/ViewAll.aspx?PageGroupID=5&p={page}'
		pre_titles = this.read_previous('threeStand')
		new_titles = {}

		page = 1
		while True:
			if page > 10:
				break

			html = requests.get(url.format(page=str(page))).text
			html = BeautifulSoup(html, 'lxml')

			items = html.select('.col-sm-12.newsItems')
			if len(items) == 0:
				break

			for item in items:
				title = item.select('.gt')[0].text.replace('\u3000', '')
				link = root_url + item.select('a')[1]['href']
				if title not in pre_titles:
					new_titles[title] = link
					print(title)
				else:
					this.write_new_title('threeStand', new_titles)
					return new_titles
			page += 1

		this.write_new_title('threeStand', new_titles)
		return new_titles


	def unionNews(this):

		root_url = 'https://udn.com'
		url_more = 'https://udn.com/api/more?page={page}&id=&channelId=1&cate_id=0&type=breaknews&totalRecNo={rec}'
		url_page = 'https://udn.com/news/breaknews/1'
		pre_titles = this.read_previous('unionNews')
		new_titles = {}

		# get totalRecNo from html
		html = requests.get(url_page).text
		html = BeautifulSoup(html, 'lxml')
		button = html.select('#indicator')[0]
		query_info = button['data-query'].replace('\'', '"')
		query_info = json.loads(query_info)
		rec = query_info['totalRecNo']
		# print(rec)

		page = 1
		while True:
			try:
				req = requests.get(url_more.format(page=str(page),rec=rec)).json()
			except:
				pass
			datas = req['lists']
			for data in datas:
				title = data['title']
				link = root_url + data['titleLink']
				if title not in pre_titles:
					new_titles[title] = link
					print(title)
				else:
					this.write_new_title('unionNews', new_titles)
					return new_titles

			if req['end']:
				break
			page += 1

		this.write_new_title('unionNews', new_titles)
		return new_titles


	def freeNews(this):

		url = 'https://news.ltn.com.tw/ajax/breakingnews/all/{page}'
		pre_titles = this.read_previous('freeNews')
		new_titles = {}

		page = 2
		while True:

			datas = requests.get(url.format(page=str(page))).json()['data']
			if len(datas) == 0:
				break

			for data in datas:
				title = datas[data]['title']
				link = datas[data]['url']

				if title not in pre_titles:
					new_titles[title] = link
					print(title)
				else:
					this.write_new_title('freeNews', new_titles)
					return new_titles
			page += 1

		this.write_new_title('freeNews', new_titles)
		return new_titles


	def appleNews(this):

		root_url = 'https://tw.appledaily.com'
		url = 'https://tw.appledaily.com/pf/api/v3/content/fetch/query-feed?query=%7B%22feedOffset%22%3A0%2C%22feedQuery%22%3A%22type%253Astory%2520AND%2520taxonomy.primary_section._id%253A%252F%255C%252Frealtime.*%252F%22%2C%22feedSize%22%3A%22100%22%2C%22sort%22%3A%22display_date%3Adesc%22%7D&filter=%7B_id%2Ccontent_elements%7B_id%2Ccanonical_url%2Ccreated_date%2Cdisplay_date%2Cheadlines%7Bbasic%7D%2Clast_updated_date%2Cpromo_items%7Bbasic%7B_id%2Ccaption%2Ccreated_date%2Cheight%2Clast_updated_date%2Cpromo_image%7Burl%7D%2Ctype%2Curl%2Cversion%2Cwidth%7D%2Ccanonical_website%2Ccredits%2Cdisplay_date%2Cfirst_publish_date%2Clocation%2Cpublish_date%2Crelated_content%2Csubtype%7D%2Crevision%2Csource%7Badditional_properties%2Cname%2Csource_id%2Csource_type%2Csystem%7D%2Ctaxonomy%7Bprimary_section%7B_id%2Cpath%7D%2Ctags%7Btext%7D%7D%2Ctype%2Cversion%2Cwebsite%2Cwebsite_url%7D%2Ccount%2Ctype%2Cversion%7D&d=136&_website=tw-appledaily'
		pre_titles = this.read_previous('appleNews')
		new_titles = {}

		elements = requests.get(url).json()['content_elements']
		for ele in elements:
			title = ele['headlines']['basic'].replace('\u3000','')
			link = root_url + ele['website_url']
			
			if title not in pre_titles:
				new_titles[title] = link
				print(title)
			else:
				this.write_new_title('appleNews', new_titles)
				return new_titles

		this.write_new_title('appleNews', new_titles)
		return new_titles


	def execute(this):
		this.chinaNews()
		this.formosa()
		this.threeStand()
		this.unionNews()
		this.freeNews()
		this.appleNews()


# nc = NewsCrawler()
# nc.execute()
# title = nc.chinaNews()
# title = nc.formosa()
# title = nc.threeStand()
# title = nc.unionNews()
# title = nc.freeNews()
# title = nc.appleNews()



