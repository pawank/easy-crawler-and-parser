from __future__ import print_function
import pickle
import os
import os.path
import requests
from bs4 import BeautifulSoup
import traceback
import re
import simplejson as json
from utils import load_excel_file, upload_to_s3, save_to_random_file, download_and_save
from slugify import slugify
import time
import random


class CrawlerParser(object):
    bucket_name = "projectstore"
    urls = []
    url_split_factor = 4

    def __init__(self):
        super().__init__()

    # Return a list of target url to be crawled and processed
    def load_urls(self, excel_filename):
        self.urls = []
        return self.urls

    def _crawl_using_selenium(self, url):
        html = None
        try:
            driver = webdriver.Chrome()
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
        driver.quit()
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

        driver = webdriver.Chrome()
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

        return (fields_map)

        try:
            for image in images:
                upload_to_s3(self.bucket_name, image)
            datajson = self.make_data_json(fields_map)
            datafilename = slugify(url, replacements=[['|', 'or'], ['%', 'percent']])
            randomfile = save_to_random_file(datajson, datafilename)
            upload_to_s3(self.bucket_name, randomfile)
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
