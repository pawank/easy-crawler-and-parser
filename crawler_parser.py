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
from utils import load_excel_file, upload_to_s3, save_to_random_file, download_and_save, update_counter_value
import time
import random
import requests
from selenium import webdriver
from simple_mail_client import send_mail

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
    is_override = None
    bad_url_count = 0

    def __init__(self, start_index=0, end_index = 9999999999, save_to_s3=False, is_override=None, show_stats=None):
        super().__init__()
        self.start_index = start_index
        self.end_index = end_index
        self.save_to_s3 = save_to_s3
        self.is_override = is_override
        if not show_stats:
            #self._get_web_driver(True)
            pass
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
        if self.driver:
            self.driver.quit()

    def restart_driver(self):
        if self.driver:
            self.driver.quit()
        timeDelay = random.randrange(2, 3)
        #self._get_web_driver(True)

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
        print("total done urls = ", len(done_map.keys()))
        donexs = set(list(done_map.keys()))
        totals = 0
        i = 0
        j = 0
        with open(excel_filename, 'r') as f:
            data = f.readlines()
            print("Total urls in styles = ", len(data))
            totals = len(data)
            #print(data, len(data))
            for line in data:
                tokens = line.split(",")
                url = None
                if len(tokens) >= 3:
                    url = "".join(tokens[2:]).strip()
                if len(tokens) <= 2:
                    url = line.strip()
                if url and len(url) > 1:
                    if self.is_override:
                        self.urls.append(url)
                    else:
                        if url in done_map:
                            pass
                        else:
                            self.urls.append(url)
                else:
                    print("\n\nINVALID URL = ", url)
                i += 1
        #print(self.urls)
        self.urls = set(self.urls)
        self.urls = list(self.urls - donexs)
        print('Total no of urls to be parsed = ', len(self.urls), ' out of ', totals)
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

    def _crawl_using_requests(self, url):
        html = None
        try:
            id = self.page_id(url)
            r = requests.get(url)
            html = r.text
            #timeDelay = random.randrange(2, 3)
            #time.sleep(timeDelay)
            '''
            with open("/tmp/" + id, "wb") as f:
                f.write(html)
            
            with open("/tmp/" + id, "rb") as f:
                html = f.read()
            ''' 
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
    def parse(self, url, html, counter=0):
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
            if not fields_map['name']:
                counter += 1
                if counter > 1:
                    pass
                else:
                    print('Retrying again URL = ', url, ' with counter = ', counter)
                    timeDelay = random.randrange(3, 5)
                    time.sleep(timeDelay)
                    return self.parse(url, html, counter)

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
            '''
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
            '''
            fields_map['uploaded_images'] = s3_images
            datajson = self.make_data_json(fields_map)
            randomfile = save_to_random_file(datajson, datafilename, as_json=True)
            print('Uploading fields data file: ', randomfile, ' to S3')
            if self.save_to_s3:
                upload_to_s3(self.bucket_name, randomfile)
            print('Uploaded fields data file: ', randomfile, ' to S3')
            if self.is_delete_cache:
                #os.remove(randomfile)
                pass
            final_filename = randomfile
            if fields_map['name'] == '' or fields_map['images'] == []:
                self.bad_url_count += 1
                update_counter_value()
                with open('error_urls.txt', 'a') as eff:
                    eff.write(fields_map['url'] + "\n")
                if self.bad_url_count % 10 == 0:
                    self.bad_url_count = 0
                    #sending email as alert
                    #send_mail("admin@rapidor.co", "pawan.kumar@gmail.com", "NO DATA FOUND", str(fields_map['url']))
                    pass
            #update_counter_value()
        except Exception as ex:
            error = str(traceback.format_exc())
            print('ERROR: URL parse error = ', error, ' for url, ', url)
        return final_filename
    
    def make_final_json_from_pdp_data(self, json_data):
        json_data = json_data["pdpData"] if "pdpData" in json_data else None
        if json_data:
            id = json_data["id"]
            brand = json_data["brand"] if "brand" in json_data else None
            name = json_data["name"]
            brand_name = brand["name"] if brand else ""
            mrp = json_data["mrp"] if "mrp" in json_data else ""
            productDetails = json_data["productDetails"] if "productDetails" in json_data else []
            prod = ""
            care = ""
            if productDetails:
                for p in productDetails:
                    if p["title"] == "Product Details":
                        description = p["description"] if "description" in p else ""
                        if description:
                            prod = description
                    if p["title"] == "MATERIAL & CARE":
                        description = p["description"] if "description" in p else ""
                        if description:
                            care = description
            meta_desc = []
            serviceability = json_data["serviceability"] if "serviceability" in json_data else None
            if serviceability:
                meta_desc = serviceability["descriptors"] if "descriptors" in serviceability else []
            albums = json_data["media"]["albums"]
            imgs = []
            for album in albums:
                images = album["images"] if "images" in album else []
                #print("IMAGES: ", images)
                for img in images:
                    if 'imageURL' in img:
                        imgs.append(img['imageURL'])
            from datetime import datetime
            at = str(datetime.now())
            j = {
            "url": "https://www.myntra.com/" + str(id),
            "brand": brand_name,
            "name": name.replace(brand_name, "") if brand_name else "",
            "price": "Rs. " + str(mrp) if mrp else "",
            "tax": "inclusive of all taxes",
            "product_details": prod,
            "material_and_care": care,
            "meta_desc": meta_desc,
            "images": imgs,
            "uploaded_images": [],
            "at": at,
            "original":json_data
            }
            return j
        return None
    
    def parse_using_requests(self, url, html, counter=0):
        from slugify import slugify
        images = []
        # A dictionary table of fields with values extracted from the html
        fields_map = {}
        final_filename = None
        try:
            maybejson = html.split("window.__myx = ")[1]
            maybejson = maybejson.split('''</script><script>window''')[0]
            #print(maybejson.strip())
            json_data = json.loads(maybejson.strip())

            fields_map['url'] = url
            datafilename = self.base_folder + self.page_id(url) + "/" + slugify(url, replacements=[['|', 'or'], ['%', 'percent']])
            json_data = self.make_final_json_from_pdp_data(json_data)
            product_name = None
            if json_data:
                product_name = json_data["name"]
            if not product_name:
                counter += 1
                if counter > 1:
                    pass
                else:
                    print('Retrying again URL = ', url, ' with counter = ', counter)
                    timeDelay = random.randrange(3, 5)
                    time.sleep(timeDelay)
                    return self.parse_using_requests(url, html, counter)

            fields_map = json_data

            image_prefix = self.base_folder + self.page_id(url) + "/"
            images = json_data["images"]
            s3_images = []
            '''
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
            '''
            fields_map['uploaded_images'] = s3_images
            datajson = self.make_data_json(fields_map)
            randomfile = save_to_random_file(datajson, datafilename, as_json=True)
            print('Uploading fields data file: ', randomfile, ' to S3')
            if self.save_to_s3:
                upload_to_s3(self.bucket_name, randomfile)
            print('Uploaded fields data file: ', randomfile, ' to S3')
            if self.is_delete_cache:
                #os.remove(randomfile)
                pass
            final_filename = randomfile
            if fields_map['name'] == '' or fields_map['images'] == []:
                self.bad_url_count += 1
                update_counter_value()
                with open('error_urls.txt', 'a') as eff:
                    eff.write(fields_map['url'] + "\n")
                if self.bad_url_count % 10 == 0:
                    self.bad_url_count = 0
                    #sending email as alert
                    #send_mail("admin@rapidor.co", "pawan.kumar@gmail.com", "NO DATA FOUND", str(fields_map['url']))
                    pass
            #update_counter_value()
        except Exception as ex:
            error = str(traceback.format_exc())
            print('ERROR: URL parse error = ', error, ' for url, ', url)
            with open('error_urls.txt', 'a') as eff:
                eff.write(url + "\n")
        return final_filename


    # Crawl a given url and return filename of the HTML content saved
    def crawl(self, url):
        html = None
        try:
            from datetime import datetime
            dt = datetime.now()
            print('Starting crawl for url = ', url, ' at time = ', dt)
            html = self._crawl_using_requests(url)
            #html = self._crawl_using_selenium(url)
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
                final_filename = self.parse_using_requests(url, html)
                print('Final filename found = ', final_filename, ' for url = ', url)
                print("%s = %s" % (url, "ended")) 
                with open("done_urls.txt", 'a+') as f:
                    f.write(url + "\n")
                counter += 1
                #timeDelay = random.randrange(5, 10)
                #time.sleep(timeDelay)
        except Exception as ex:
            error = str(traceback.format_exc())
            print('ERROR: Run error = ', error)
        return counter

    def start_run(self, urls):
        import threading
        import shutil
        counter = 0
        try:
            import datetime
            self.urls = urls
            #print(self.urls)
            print("Starting with urls count ", len(urls), " at = ", datetime.datetime.now())
            for url in self.urls:
                self.url_counter += 1
                if self.url_counter % 30 == 0:
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
                final_filename = self.parse_using_requests(url, html)
                print('Final filename found = ', final_filename, ' for url = ', url)
                print("%s = %s" % (url, "ended")) 
                with open("done_urls.txt", 'a+') as f:
                    f.write(url + "\n")
                counter += 1
                #timeDelay = random.randrange(5, 10)
                #time.sleep(timeDelay)
            self.exit_browser()
        except Exception as ex:
            error = str(traceback.format_exc())
            print('ERROR: Run error = ', error)
        return counter
