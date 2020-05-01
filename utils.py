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

def write_to_global_file(data):
            filename = "global_data.txt"
            try:
                with open(filename, 'a+', encoding='utf8') as f:
                        f.write(data + "\n")
                print('Wrote to file = ', filename)
            except Exception as exx:
                tmperr = str(traceback.format_exc())
                print("Data save error in global data file: ", filename, " and ex = ", tmperr)
            return filename

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
                        jsonvalue = json.dumps(data)
                        write_to_global_file(jsonvalue)
                        f.write(jsonvalue)
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
    return (filename, sz)


def upload_to_s3(bucket_name, filename, as_json=None):
    #https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html
    import boto3
    try:
        if os.path.exists(filename):
            session = boto3.Session(profile_name='nitish')
            #s3 = boto3.resource('s3')
            #s3 = session.client('s3')
            s3 = session.resource('s3')
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
            #key = filename.split("/")[-1]
            key = filename
            s3.Bucket(bucket_name).put_object(Key=key, Body=data)
            print('Uploaded to s3 file = ', filename, ' with key = ', key)
            return True
        else:
            print('Sorry, Filename not found: ', filename)
    except Exception as ex:
        error = str(traceback.format_exc())
        print('ERROR: Upload to s3 error = ', error, ' for url, ', filename)
    return False

def get_dynamodb_table(table_name="data_files"):
    #https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html
    import boto3
    try:
        session = boto3.Session(profile_name='nitish', region_name='us-east-1')
        # Get the service resource.
        #dynamodb = boto3.resource('dynamodb')
        dynamodb = session.client('dynamodb')
        table_found = False
        try:
            response = dynamodb.describe_table(TableName=table_name)
            table_found = True
        except dynamodb.exceptions.ResourceNotFoundException:
            # do something here as you require
            error = str(traceback.format_exc())
            print('TABLE not found = ', error)
            pass
        if table_found:
            return dynamodb
        else:
            # Create the DynamoDB table.
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 'url',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'pid',
                        'KeyType': 'RANGE'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'url',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'pid',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1
                }
            )
            # Wait until the table exists.
            dynamodb.get_waiter('table_exists').wait(TableName=table_name)
            table_found = True
            # Print out some data about the table.
            print(table.item_count)
            return dynamodb
    except Exception as ex:
        error = str(traceback.format_exc())
        print('ERROR: Saving to dynamodb error = ', error, ' for table, ', table_name)
    return None

def save_in_dynamodb(table_name, data_table):
    import boto3
    try:
        pid = None
        if 'pid' in data_table:
            pass
        else:
            tokens = data_table['url'].split('/')
            tokens.reverse()
            pid = tokens[0]
        data = json.dumps(data_table)
        table = {
            'url':{'S': data_table['url']},
            'pid':{'S': pid},
            'data': {'S': data}
        }
        session = boto3.Session(profile_name='nitish', region_name='ap-south-1')
        client = session.client('dynamodb')
        client = get_dynamodb_table(table_name)
        client.put_item(
            TableName=table_name,
            Item=table
        )
        return True
    except Exception as ex:
        error = str(traceback.format_exc())
        print('ERROR: Saving to dynamodb error = ', error, ' for table, ', table_name)
    return None