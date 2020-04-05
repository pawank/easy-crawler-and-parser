from __future__ import print_function
import pickle
import sys, os
sys.path.append('/path/to/selenium')
import os.path
import requests
from bs4 import BeautifulSoup
import traceback
import re
import simplejson as json
from utils import load_excel_file, upload_to_s3, save_to_random_file, download_and_save
import time
import random
from selenium import webdriver
#from slugify import slugify

CHROME = 'chromium'
CHROME_DRIVER = 'chromedriver'

class CrawlerParser(object):
    bucket_name = "projectstore"
    urls = []
    start_index = 0
    end_index = 9999999999
    driver = None

    def __init__(self, start_index=0, end_index = 9999999999):
        super().__init__()
        self.start_index = start_index
        self.end_index = end_index
        self._get_web_driver(False)
        if not self.driver:
            print('Init failed. Exited. ')
        else:
            print('Init done with start index = ', self.start_index, ' and end index = ', self.end_index)

    def _get_web_driver(self, headless):
        user_agent = '''
            Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36
        '''
        try:
            chrome_options = webdriver.ChromeOptions()
            if headless:
                chrome_options.add_argument('headless')
            chrome_options.add_argument('user-agent={0}'.format(user_agent))
            driver = webdriver.Chrome(CHROME_DRIVER, chrome_options=chrome_options)
            print('Selenium driver loaded with start index = ', self.start_index, ' and end index = ', self.end_index)
            self.driver = driver 
        except Exception as ex:
            error = str(traceback.format_exc())
            print('ERROR: Driver loading error = ', error)
    
    def exit_browser(self):
        self.driver.quit()

    # Return a list of target url to be crawled and processed
    def load_urls(self, excel_filename):
        self.urls = []
        with open(excel_filename, 'r') as f:
            data = f.readlines()
            #print(data, len(data))
            for line in data:
                tokens = line.split(",")
                url = "".join(tokens[2:]).strip()
                self.urls.append(url)
        #print(self.urls)
        return self.urls

    def _crawl_using_selenium(self, url):
        html = None
        try:
            driver = self.driver
            driver.get(url)

            # scroll down and setting time delay - to get the images loaded on each scroll.  
            driver.execute_script("window.scrollTo(0,400)")
            timeDelay = random.randrange(2, 3)
            time.sleep(timeDelay)
            driver.execute_script("window.scrollTo(0,600)")
            timeDelay = random.randrange(2, 3)
            time.sleep(timeDelay)
            driver.execute_script("window.scrollTo(0,900)")
            timeDelay = random.randrange(2, 3)
            time.sleep(timeDelay)
            driver.execute_script("window.scrollTo(0,1100)")
            timeDelay = random.randrange(2, 3)
            time.sleep(timeDelay)
            driver.execute_script("window.scrollTo(0,1300)")
            timeDelay = random.randrange(2, 3)
            time.sleep(timeDelay)
            driver.execute_script("window.scrollTo(0,1500)")
            timeDelay = random.randrange(2, 3)
            time.sleep(timeDelay)
            driver.execute_script("window.scrollTo(0,1700)")
            timeDelay = random.randrange(2, 3)
            time.sleep(timeDelay)
            driver.execute_script("window.scrollTo(0,1900)")
            timeDelay = random.randrange(2, 3)
            time.sleep(timeDelay)

            #get html page of url 
            content = driver.page_source.encode('utf-8').strip()
            soup = BeautifulSoup(content, 'lxml')
            html = soup.prettify()


        except Exception as ex:
            error = str(traceback.format_exc())
            print('ERROR: Helper crawl error = ', error, ' for url, ', url)
        return html

    def make_data_json(self, fields_map):
        datajson = {}
        return datajson

    # Parse the input HTML and extract relevant information from it as per the user case and return True for success and False for error
    def parse(self, url, html):
        images = []
        # A dictionary table of fields with values extracted from the html

        fields_map = {

        }


        try:
            driver.get(url)

            # Getting brand name
            brands = driver.find_elements_by_class_name("pdp-title")
            fields_map['brand_name'] = brands[0].text

            # Getting product name
            product_name = driver.find_elements_by_class_name("pdp-name")
            fields_map['product_name'] = product_name[0].text

            ## getting prices
            price = driver.find_elements_by_class_name("pdp-price")
            fields_map['product_name'] = price[0].text

            # getting taxes
            taxes = driver.find_elements_by_class_name("pdp-vatInfo")
            fields_map['tax']= taxes[0].text

            # getting product details
            product_details = driver.find_elements_by_class_name("pdp-product-description-content")
            fields_map['product_details'] = product_details[0].text
            
            #getting images, and adding to images[]

            soup = BeautifulSoup(html, 'lxml')
            
            image_links = soup.find_all('div', {"class": "image-grid-image"})
            for link in image_links:
                l1 = link['style']
                final_url = l1[23:-3]
                print(final_url)
                images.append(final_url)

            for image in images:
                print('Uploading image: ', image, ' to S3')
                #upload_to_s3(self.bucket_name, image)
                print('Uploaded image: ', image, ' to S3')
            datajson = self.make_data_json(fields_map)
            datafilename = slugify(url, replacements=[['|', 'or'], ['%', 'percent']])
            randomfile = save_to_random_file(datajson, datafilename)
            print('Uploading fields data file: ', randomfile, ' to S3')
            #upload_to_s3(self.bucket_name, randomfile)
            print('Uploaded fields data file: ', randomfile, ' to S3')
        except Exception as ex:
            error = str(traceback.format_exc())
            print('ERROR: URL parse error = ', error, ' for url, ', url)
        return True

    # Crawl a given url and return filename of the HTML content saved
    def crawl(self, url):
        html = None
        try:
            html = self._crawl_using_selenium(url)
        except Exception as ex:
            error = str(traceback.format_exc())
            print('ERROR: URL crawl error = ', error, ' for url, ', url)
        return html

    def run(self):
        html = None
        try:
            excel_filename = "styles.csv"
            self.load_urls(excel_filename)
        except Exception as ex:
            error = str(traceback.format_exc())
            print('ERROR: Run error = ', error)
        return html