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

class CrawlerParser(object):
    bucket_name = "projectstore"
    urls = []
    url_split_factor = 4

    def __init__(self):
        super().__init__()

    #Return a list of target url to be crawled and processed
    def load_urls(self, excel_filename):
        self.urls = []
        return self.urls

    def _crawl_using_selenium(self, url):
        html = None
        try:
            pass
        except Exception as ex:
            error = str(traceback.format_exc())
            print('ERROR: Helper crawl error = ', error, ' for url, ', url)
        return html
           
    def make_data_json(self, fields_map):
        datajson = {}
        return datajson

    #Parse the input HTML and extract relevant information from it as per the user case and return True for success and False for error
    def parse(self, url, html):
        images = []
        #A dictionary table of fields with values extracted from the html
        fields_map = {}
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

    #Crawl a given url and return filename of the HTML content saved
    def crawl(self, url):
        html = None
        try:
            html = self._crawl_using_selenium(url)
        except Exception as ex:
            error = str(traceback.format_exc())
            print('ERROR: URL crawl error = ', error, ' for url, ', url)
        return html

    