from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
# Create your views here.

def index(request):
	result_url = main()
	# result_url = ['www.google.com','www.facebook.com']
	return render(request, 'index.html',{'result_url':result_url} )
	#Refresh steps for everything to work correctly
	
import os
import sqlite3
import shutil
import re
import requests
from bs4 import BeautifulSoup
from RAKE import rake
import operator


def clustering(words):
	import numpy as np
	import sklearn.cluster
	import distance
	#print "clustering"
	#print words
	#words = "YOUR WORDS HERE".split(" ") #Replace this line
	words = np.asarray(words) #So that indexing with a list will work
	lev_similarity = -1*np.array([[distance.levenshtein(w1,w2) for w1 in words] for w2 in words])

	affprop = sklearn.cluster.AffinityPropagation(affinity="precomputed", damping=0.5)
	affprop.fit(lev_similarity)
	classes = []
	for cluster_id in np.unique(affprop.labels_):
	    exemplar = words[affprop.cluster_centers_indices_[cluster_id]]
	    cluster = np.unique(words[np.nonzero(affprop.labels_==cluster_id)])
	    cluster_str = ", ".join(cluster)
	    #print(" - *%s:* %s" % (exemplar, cluster_str))
	    classes.append(exemplar)
	return classes

def get_text2(url):
	from stripogram import html2text
	r = requests.get(url)
	text = html2text(r.content).encode('utf-8')
	#print text
	return text

def get_text(url):
	r = requests.get(url)
	soup = BeautifulSoup(r.content,"lxml")
	data = soup.find_all('p')
	text = ''
	for content in data:
		text+=content.text
	data = soup.find_all('div')
	for content in data:
		text+=content.text
	return text

def get_keywords(url):
	text = get_text2(url)
	# print text
	rake_object = rake.Rake("RAKE/SmartStoplist.txt", 5, 3, 4)
	keywords = rake_object.run(text)
	return keywords


def main():
	import sys
	reload(sys)
	sys.setdefaultencoding("utf-8")
	# Opening the history file
	home_dir = os.path.expanduser('~')
	data_path = ''
	if sys.platform == "linux" or sys.platform == "linux2": 
		data_path = home_dir+"/.config/chromium/Default"
	elif sys.platform == "win32":
		data_path = home_dir+"\AppData\Local\Google\Chrome\User Data\Default"

	files = os.listdir(data_path)
	history_db = os.path.join(data_path, 'History')
	shutil.copy(history_db, home_dir);
	c = sqlite3.connect(os.path.join(home_dir, 'History'))

	#Extracting the data from the file
	cursor = c.cursor()
	#select_statement = "SELECT urls.url, (urls.visit_count*urls.last_visit_time) as score FROM urls, visits WHERE urls.id = visits.url;"
	#select_statement = "SELECT lower_term FROM keyword_search_terms;"
	#select_statement = "SELECT * FROM meta;"
	#select_statement = "SELECT visit_duration FROM visits;"
	#select_statement = "SELECT urls.visit_count, urls.last_visit_time, visits.visit_duration from urls,visits WHERE urls.id = visits.url;"
	'''select_statement = "SELECT url FROM urls ORDER BY urls.last_visit_time DESC , urls.visit_count DESC;"
	cursor.execute(select_statement)
	results = cursor.fetchall()
	
	keywords = ['amazon', 'facebook', 'linkedin', 'instagram']
	#print results
	counter = 0
	for links in results:
		if counter > 0:
			break
		print links
		try:
			counter = counter+1
			keywords.extend(get_keywords(links[0]))
		except:
			counter = counter-1
			continue;

	#print "printing keywords"
	#print keywords
	words = []
	for item in keywords:
		words.append(item[0])

	#Refresh steps for everything to work correctly
	#print words
	classes = clustering(words)'''
	#print "Processing 2nd clustering"
	classes = []
	select_statement = "SELECT lower_term FROM keyword_search_terms LIMIT 100;"
	cursor.execute(select_statement)
	results = cursor.fetchall()
	c.close();
	words = []
	for item in results:
		words.append(item[0])
	classes.extend(clustering(words))
	result_url = []
	from google import search
	for text in classes:
		for url in search(text, tld='com', lang='es', stop=10):
			result_url.append(url)
			break
	print ("Done")    	
	os.remove(os.path.join(home_dir, 'History'))

	return result_url






