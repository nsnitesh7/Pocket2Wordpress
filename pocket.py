import requests
import json
import webbrowser
import urlparse
import time
import urllib2
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
from selenium.webdriver.common.by import By
from wordpress import CreateNewPost

def doAuthentication():
	driver = webdriver.Firefox()
	driver.get("https://getpocket.com/login")
	try:
		WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME,'feed_id')))
	except TimeoutException:
		print "Loading took too much time!"
		driver.close()
		return 'null'
	elem = driver.find_element_by_name("feed_id")
	elem.send_keys("username of pocket")
	try:
		WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME,'password')))
	except TimeoutException:
		print "Loading took too much time!"
		driver.close()
		return 'null'
	elem = driver.find_element_by_name("password")
	elem.send_keys("password of pocket")
	elem.send_keys(Keys.RETURN)
	
	try:
		WebDriverWait(driver, 30).until(EC.title_contains('Pocket'))
	except TimeoutException:
		print "Loading took too much time!"
		driver.close()
		return 'null'
		
	return driver

def getPocketPage(item_id, driver):

	driver.get("http://getpocket.com/a/read/"+item_id)
	
	try:
		WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME,'text_body')))
	except TimeoutException:
		print "Loading took too much time!"
		return 'null'

	html = driver.execute_script("return document.getElementsByClassName('text_body')[0].innerHTML")
	return html

if __name__ == "__main__":

	redirect_uri = 'http://localhost:8000'
	consumer_key = "consumer_key to use pocket API"

	payload = {'consumer_key':consumer_key , 'redirect_uri':redirect_uri}
	url = 'https://getpocket.com/v3/oauth/request'
	response = requests.post(url, payload)
	#print response.text

	request_token = response.text.split('=')[1]

	print consumer_key
	print request_token

	url = ('https://getpocket.com/auth/authorize?request_token=%s&redirect_uri=%s' % (request_token, redirect_uri))
	print 'please open this url on your browser'
	print url
	webbrowser.open_new_tab(url)
	raw_input()

	url = 'https://getpocket.com/v3/oauth/authorize'
	headers = {'Content-type': 'application/json'}
	payload = {'consumer_key': consumer_key, 'code': str(request_token)}
	response = requests.post(url, json.dumps(payload), headers=headers)
	print response.text
	response_dict = urlparse.parse_qs(response.text)
	access_token = response_dict['access_token']

	f = open('lastTimeStamp.txt', 'r+')

	lastPost = str(f.read().strip())
	
	i=1
	
	while 1:
		print i

		url = 'https://getpocket.com/v3/get'
		payload = {'consumer_key': consumer_key, 'access_token': access_token[0], 'sort': 'oldest', 'since': lastPost, 'detailType': 'complete'}
		response = requests.post(url, json.dumps(payload), headers=headers)

		json_response=response.json()

		if len(json_response['list'])!=0:
			driver='null'
			while driver=='null':
				driver=doAuthentication()
				
			for key,val in json_response['list'].iteritems():
				content='null'
				while content == 'null':
					content = getPocketPage(val['item_id'], driver)
	
				CreateNewPost(val['given_title'],content)
			driver.close()
			lastPost = str(json_response['since'])
			f.seek(0)
			f.write(lastPost)
			f.truncate()
	
		time.sleep(10)
		i=i+1
