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

            # scroll down
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

            # setting time delay and time to load.
            timeDelay = random.randrange(20, 25)
            time.sleep(timeDelay)

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

        soup = BeautifulSoup(html, 'lxml')

        #extracting data :

        # get brand name
        brands = soup.find_all('h1', {"class": "pdp-title"})
        for brand in brands:
            print(brand.get_text())
            fields_map['brand_name'] = brand.get_text()

        # get product name
        products = soup.find_all('h1', {"class": "pdp-name pdp-bb1"})
        for product in products:
            print(product.get_text())
            fields_map['product_name'] = product.get_text()

        prices = soup.find_all('span', {"class": "pdp-price"})
        for price in prices:
            print(price.get_text())
            fields_map['product_name'] = price.get_text()

        taxes = soup.find_all('span', {"class": "pdp-vatInfo"})
        for tax in taxes:
            print(tax.get_text())
            fields_map['tax'] = tax.get_text()

        # productDetails = soup.find_all('p', { "class" : "pdp-product-description-content"})
        # for productDetail in productDetails:
        #   print(productDetail.get_text())
        #   myntraLinkData.append(productDetail.get_text())

        product_details = driver.find_elements_by_class_name("pdp-product-description-content")
        print(product_details[0].text)
        fields_map['product_details'] = product_details[0].text


        image_links = soup.find_all('div', {"class": "image-grid-image"})
        for link in image_links:
            l1 = link['style']
            final_url = l1[23:-3]
            print(final_url)
            images.append(final_url)

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
