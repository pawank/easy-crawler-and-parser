from __future__ import print_function
import pickle
import os
import os.path
import requests
from bs4 import BeautifulSoup
import traceback
import re
import simplejson as json
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}


class dict2object(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)


class objdict(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)


def load_excel_file(filename):
    return []

def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)


def link_to_filename(link, ext):
    #FIXME:
    aws_url = ""
    from slugify import slugify
    if link:
        link = link.replace(aws_url,"").replace("." + ext, "")
        return slugify(link) + "." + ext
    return None



def getUUID(size=8, is_lower_case=False):
    import uuid
    tmpuuid = (str(uuid.uuid4())[:size]).upper()
    if is_lower_case:
        return tmpuuid.lower()
    return tmpuuid


def save_to_random_file(data, prefix, as_json):
            output = data
            filename = None
            try:
                if not prefix:
                    prefix = ""
                    filename = "/tmp/" + prefix + str(getUUID(32)) + ".json"
                else:
                    if not as_json:
                        filename = prefix
                    else:
                        prefix = str(prefix) + ".json"
                        filename = prefix
                with open(filename, 'w', encoding='utf8') as f:
                    if as_json:
                        f.write(json.dumps(data))
                    else:
                        f.write(data)
                print('Wrote to file = ', filename)
            except Exception as exx:
                tmperr = str(traceback.format_exc())
                print("Data save error in file: ", filename, " and ex = ", tmperr, " with prefix = ", prefix)
            return filename


#ext with which file is to be saved locally e.g. .pdf .jpg
def download_and_save(prefix, url, ext, is_override=None, add_type=None):
    ext = '.jpg'
    if url:
        ext = url.split(".")[-1]
    justfilename = link_to_filename(url, ext)
    filename = prefix + justfilename
    sz = 0
    headers = {
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
    try:
        if not is_override:
            if os.path.exists(filename):
                sz = file_size(filename)
                return (justfilename, sz)
        response = requests.get(url, headers=headers, verify=False, timeout=600)
        with open(filename, 'wb') as f:
            f.write(response.content)
        print('download_and_save: Image from, %s and saved filename, %s' % (url, filename))
        sz = file_size(filename)
    except Exception as ex:
        print(traceback.format_exc(), ' for url, ', url)
        filename = ''
        justfilename = ''
    return (justfilename, sz)


def upload_to_s3(bucket_name, filename, as_json=None):
    #https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html
    import boto3
    try:
        if os.path.exists(filename):
            s3 = boto3.resource('s3')
            '''
            for bucket in s3.buckets.all():
                print(bucket.name)
            '''
            data = None
            if as_json:
                data = open(filename, 'r')
            else:
                data = open(filename, 'rb')
            #print(data)
            key = filename.split("/")[-1]
            s3.Bucket(bucket_name).put_object(Key=key, Body=data)
            print('Uploaded to s3 file = ', filename, ' with key = ', key)
            return True
        else:
            print('Sorry, Filename not found: ', filename)
    except Exception as ex:
        error = str(traceback.format_exc())
        print('ERROR: Upload to s3 error = ', error, ' for url, ', filename)
    return False
