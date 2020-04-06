import os
import sys
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
    with open('files/done_urls.txt', 'w') as f:
        f.write("\n".join(list(done_map.keys())))


def main(argv):
    #test_s3_upload()
    generate_done_list()
    if False:
        from crawler_parser import CrawlerParser
        i = int(argv[1])
        j = int(argv[2])
        cp = CrawlerParser(i, j, save_to_s3=True)
        cp.run()
    pass

if __name__ == '__main__':
        main(sys.argv)
