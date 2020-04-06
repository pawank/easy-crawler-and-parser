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

CHROME = 'chromium'
CHROME_DRIVER = 'chromedriver'

class CrawlerParser(object):
    bucket_name = "projectstore"
    url_counter = 0
    urls = []
    start_index = 0
    end_index = 9999999999
    driver = None
    base_folder = "cache/"
    is_delete_cache = True
    save_to_s3 = None

    def __init__(self, start_index=0, end_index = 9999999999, save_to_s3=False):
        super().__init__()
        self.start_index = start_index
        self.end_index = end_index
        self.save_to_s3 = save_to_s3
        self._get_web_driver(True)
        if not self.driver:
            print('Init failed and exited with start index = ', self.start_index, ' and end index = ', self.end_index)
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

    def restart_driver(self):
        self.driver.quit()
        timeDelay = random.randrange(2, 3)
        self._get_web_driver(True)

    # Return a list of target url to be crawled and processed
    def load_urls(self, excel_filename):
        self.urls = []
        done_map = {}
        with open("done_urls.txt", 'r') as f:
            data = f.readlines()
            for line in data:
                url = line.strip()
                if url and len(url) > 1:
                    done_map[url] = done_map
        i = 0
        j = 0
        with open(excel_filename, 'r') as f:
            data = f.readlines()
            #print(data, len(data))
            for line in data:
                tokens = line.split(",")
                url = "".join(tokens[2:]).strip()
                if url and len(url) > 1:
                    if url in done_map:
                        pass
                    else:
                        self.urls.append(url)
                i += 1
        #print(self.urls)
        print('Total no of urls to be parsed = ', len(self.urls), ' out of ', i)
        return self.urls

    def page_id(self, url):
        if url:
            tokens = url.split("/")
            tokens.reverse()
            return tokens[0]
        return None

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
            filename = self.base_folder + self.page_id(url) + "/" + self.page_id(url) + ".html"
            randomfile = save_to_random_file(html, filename, as_json=False)
            if self.save_to_s3:
                upload_to_s3(self.bucket_name, randomfile)
            if self.is_delete_cache:
                os.remove(randomfile)
        except Exception as ex:
            error = str(traceback.format_exc())
            print('ERROR: Helper crawl error = ', error, ' for url, ', url)
        return html

    def make_data_json(self, fields_map):
        from datetime import datetime
        datajson = fields_map
        datajson['at'] = str(datetime.now())
        return datajson

    def save_page_screenshot(self, url, driver):
        from slugify import slugify
        try:
            datafilename = slugify(url, replacements=[['|', 'or'], ['%', 'percent']])
            S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
            driver.set_window_size(S('Width'),S('Height')) # May need manual adjustment                                                                                                                
            screenshot_filename = self.base_folder + self.page_id(url) + "/screenshot_" + datafilename + ".png"
            driver.find_element_by_tag_name('body').screenshot(screenshot_filename)
            #driver.get_screenshot_as_file(screenshot_filename)
            print('Saved screenshot at = ', screenshot_filename, ' for url = ', url)
            if self.save_to_s3:
                upload_to_s3(self.bucket_name, screenshot_filename)
            if self.is_delete_cache:
                os.remove(screenshot_filename)
            return screenshot_filename
        except Exception as ex:
            error = str(traceback.format_exc())
            print('ERROR: Screenshot save error = ', error, ' for url, ', url)
        return None

    def get_text_value(self, data, is_all=None):
        if data and len(data) > 0:
            if is_all:
                return list(map(lambda x: x.text, data))
            return data[0].text
        if is_all:
            return []
        return ""

    # Parse the input HTML and extract relevant information from it as per the user case and return True for success and False for error
    def parse(self, url, html):
        from slugify import slugify
        images = []
        # A dictionary table of fields with values extracted from the html
        fields_map = {}
        final_filename = None
        try:
            fields_map['url'] = url
            datafilename = self.base_folder + self.page_id(url) + "/" + slugify(url, replacements=[['|', 'or'], ['%', 'percent']])
            driver = self.driver
            driver.get(url)

            self.save_page_screenshot(url, driver)

            # Getting brand name
            brands = driver.find_elements_by_class_name("pdp-title")
            fields_map['brand'] = self.get_text_value(brands)

            # Getting product name
            product_name = driver.find_elements_by_class_name("pdp-name")
            fields_map['name'] = self.get_text_value(product_name)

            ## getting prices
            price = driver.find_elements_by_class_name("pdp-price")
            fields_map['price'] = self.get_text_value(price)

            # getting taxes
            taxes = driver.find_elements_by_class_name("pdp-vatInfo")
            fields_map['tax']= self.get_text_value(taxes)

            # getting product details
            product_details = driver.find_elements_by_class_name("pdp-product-description-content")
            fields_map['product_details'] = self.get_text_value(product_details)

            metadescs = driver.find_elements_by_class_name("meta-desc")
            fields_map['meta_desc'] = self.get_text_value(metadescs, True)
            

            print('Fields map so far = ', fields_map, 'for url = ', url) 
            #getting images, and adding to images[]

            soup = BeautifulSoup(html, 'lxml')
            
            image_links = soup.find_all('div', {"class": "image-grid-image"})
            for link in image_links:
                l1 = link['style']
                final_url = l1[23:-3]
                print('Image found so far = ', final_url, 'for url = ', url) 
                images.append(final_url)

            fields_map['images'] = images


            image_prefix = self.base_folder + self.page_id(url) + "/"
            s3_images = []
            for image in images:
                print('Uploading image: ', image, ' to S3')
                if self.save_to_s3:
                    image_file, image_size = download_and_save(image_prefix, image, None, is_override=True, add_type=None)
                    if image_file:
                        s3_images.append({"original":image, "uploaded":image_file, "size":image_size})
                        upload_to_s3(self.bucket_name, image_file)
                        if self.is_delete_cache:
                            os.remove(image_file)
                print('Uploaded image: ', image, ' to S3')
            fields_map['uploaded_images'] = s3_images
            datajson = self.make_data_json(fields_map)
            randomfile = save_to_random_file(datajson, datafilename, as_json=True)
            print('Uploading fields data file: ', randomfile, ' to S3')
            if self.save_to_s3:
                upload_to_s3(self.bucket_name, randomfile)
            print('Uploaded fields data file: ', randomfile, ' to S3')
            if self.is_delete_cache:
                os.remove(randomfile)
            final_filename = randomfile
        except Exception as ex:
            error = str(traceback.format_exc())
            print('ERROR: URL parse error = ', error, ' for url, ', url)
        return final_filename

    # Crawl a given url and return filename of the HTML content saved
    def crawl(self, url):
        html = None
        try:
            from datetime import datetime
            dt = datetime.now()
            print('Starting crawl for url = ', url, ' at time = ', dt)
            html = self._crawl_using_selenium(url)
            dt = datetime.now()
            print('Ended crawl for url = ', url, ' at time = ', dt)
        except Exception as ex:
            error = str(traceback.format_exc())
            print('ERROR: URL crawl error = ', error, ' for url, ', url)
        return html

    def run(self):
        import shutil
        counter = 0
        try:
            excel_filename = "styles.csv"
            self.load_urls(excel_filename)
            for url in self.urls[self.start_index:self.end_index]:
                self.url_counter += 1
                if self.url_counter % 10 == 0:
                    self.restart_driver()
                path = self.base_folder + self.page_id(url)
                if path.find("cache") >= 0:
                    if not os.path.exists(path):
                        os.makedirs(path)
                    else:
                        shutil.rmtree(path) 
                        os.makedirs(path)
                print("%s = %s" % (url, "started")) 
                html = self.crawl(url)
                final_filename = self.parse(url, html)
                print('Final filename found = ', final_filename, ' for url = ', url)
                print("%s = %s" % (url, "ended")) 
                with open("done_urls.txt", 'a+') as f:
                    f.write(url + "\n")
                counter += 1
        except Exception as ex:
            error = str(traceback.format_exc())
            print('ERROR: Run error = ', error)
        return counter
