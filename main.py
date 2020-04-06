import os
import traceback

def test_s3_upload():
    from slugify import slugify
    from utils import load_excel_file, upload_to_s3, save_to_random_file, download_and_save
    url = "http://test.com"
    datafilename = slugify(url, replacements=[['|', 'or'], ['%', 'percent']]).replace("https-", "").replace("http-","")
    #print(datafilename)
    datajson = {"project":"parsing example"}
    randomfile = save_to_random_file(datajson, datafilename, as_json=True)
    #print(randomfile)
    upload_to_s3("projectstore", randomfile)

def generate_done_list():
    import simplejson as json
    done_map = {}
    with open('files/global_data.txt','r') as f:
        lines = f.readlines()
        for line in lines:
                data = line.strip()
                j = json.loads(data)
                if "url" in j:
                    done_map[j["url"]] = j["url"]
    print('No of done urls = ', len(done_map.keys()))


def main():
    #test_s3_upload()
    from crawler_parser import CrawlerParser
    #cp = CrawlerParser()
    #cp.run()
    generate_done_list()
    pass

if __name__ == '__main__':
        main()
