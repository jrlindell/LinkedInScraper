import pandas as pd
import string
import numpy as np
import requests
import random
from time import sleep
import json
from parsel import Selector
import time
from selenium import webdriver
import re
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import csv
import argparse, os, time
from selenium.common.exceptions import NoSuchElementException

parser = argparse.ArgumentParser()
# Open Chrome Browser using Chromedriver
driver = webdriver.Chrome("/Users/jumananadir/opt/anaconda3/lib/python3.7/site-packages/chromedriver_binary/chromedriver")
driver.get("https://www.google.com/")
# Enter Boolean Search in the search bar
press_enter = driver.find_element_by_name("q")
press_enter.send_keys('site:linkedin.com/in ("project manager" AND construction AND "va hospital" AND civil) AND (bechtel OR aecom OR mcdermott OR "sto building" OR skanska OR "pcl construction" OR gilbane OR kiewit)')
press_enter.send_keys(Keys.ENTER)
sleep(2)
full_list_of_URLS=[]
full_list_of_CANDIDATES=[]
full_list_of_HEADLINE=[]
full_list_of_PROFILE_SUMMARY=[]
full_list_of_FOLLOWERS=[]
full_list_of_NAMES=[]
full_list_of_PROFILE_YOE=[]
full_list_of_LOCATION=[]
full_list_of_COMPANY=[]

count=0
while count<20:
    page = bs(driver.page_source, features="html.parser")
    content =driver.find_elements_by_tag_name('a')
    candidates = []
    candidate_names=[]
    for contact in content:
        candidates.append(contact.get_attribute('href'))
        candidate_names.append(contact.text)
    full_list_of_CANDIDATES = full_list_of_CANDIDATES+candidate_names
    full_list_of_URLS = full_list_of_URLS+candidates
    full_list_of_URLS= list(filter(None, full_list_of_URLS))

    try:
        driver.find_element_by_xpath('//a[contains(.,"Next")]').click()
        count+=1
    except NoSuchElementException:
        break
    try:
        driver.find_elements_by_class_name("next_page disabled")
    except NoSuchElementException:
        break

result = [i for i in full_list_of_URLS if i.startswith('https://www.linkedin.com/in/')]
print(result)
# Removing duplicate profiles
woduplicates = list(set(result))
print(woduplicates)
#Login to linkedin
driver.get('https://www.linkedin.com/login')
email = driver.find_element_by_xpath("/html/body/div/main/div[2]/div[1]/form/div[1]/input")
email.send_keys('jumana@dataprime.ai')
password = driver.find_element_by_xpath("/html/body/div/main/div[2]/div[1]/form/div[2]/input")

with open('/Users/jumananadir/Desktop/scraper/stack.txt', 'r') as myfile:
    Password = myfile.read().replace('\n', '')

password.send_keys(Password)
password.submit()

print ("success! Logged in to linkedin, Bot starting")

# going to each profiles one by one to scrape the data
for link in woduplicates:
    driver.get(link)
    sleep(2)
    sell = Selector(text=driver.page_source)
    name= sell.xpath('//*[starts-with(@class, "inline t-24 t-black t-normal break-words")]/text()').extract()
    summary = sell.xpath('//*[contains(@class, "lt-line")]/text()').extract()
    #YOE = sell.xpath('//*[@class="visually-hidden" and contains(text(),"Total Duration")]/text()').extract()
    headline= sell.xpath('//*[starts-with(@class, "mt1 t-18 t-black t-normal break-words")]/text()').extract()

    if summary is not None:
        print('profile summary:', summary)
        full_list_of_PROFILE_SUMMARY.append(summary)
    else:
        full_list_of_PROFILE_SUMMARY.append('None')


    if headline is not None:
        print(headline)
        full_list_of_HEADLINE.append(headline)
    else:
        full_list_of_HEADLINE.append('None')


    if name is not None:
        print(name)
        full_list_of_NAMES.append(name)
    else:
        full_list_of_NAMES.append('None')


    fol= sell.xpath('//*[starts-with(@class, "t-16 t-black t-normal")]/text()').extract()
    if fol is not None:
        print("connections=",fol)
        full_list_of_FOLLOWERS.append(fol)
    else:
        full_list_of_FOLLOWERS.append('None')


    location= sell.xpath('//*[starts-with(@class, "t-16 t-black t-normal inline-block")]/text()').extract()
    if location is not None:
        print(location)
        full_list_of_LOCATION.append(location)
    else:
        full_list_of_LOCATION.append('None')

    company = sell.xpath('//*[starts-with(@class, "text-align-left ml2 t-14 t-black t-bold full-width lt-line-clamp lt-line-clamp--multi-line ember-view")]/text()').extract_first()
    if company is not None:
        print(company)
        full_list_of_COMPANY.append(company)
    else:
        full_list_of_COMPANY.append('None')



driver.quit()

full_list_of_CANDIDATES=[item for item in full_list_of_CANDIDATES if item!='']

profiles_df=pd.DataFrame(list(zip(woduplicates,full_list_of_NAMES,full_list_of_FOLLOWERS,full_list_of_HEADLINE,full_list_of_COMPANY, full_list_of_PROFILE_SUMMARY, full_list_of_LOCATION)), columns =['URLs','Name','# Connections', 'Headline', 'Current Company','Summary', "Location"])
print(profiles_df.head())
profiles_df.to_csv(r'CMcopy.csv', index=True)
