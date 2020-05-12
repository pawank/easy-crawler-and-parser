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
                    if j['name'] != '' and j['images'] != []:
                        done_map[j["url"]] = j["url"]
    print('No of done urls = ', len(done_map.keys()))
    with open('files/done_urls.txt', 'w') as f:
        f.write("\n".join(list(done_map.keys())))

def generate_error_urls():
    import simplejson as json
    records = []
    with open('files/global_data.txt','r') as f:
        lines = f.readlines()
        for line in lines:
                data = line.strip()
                j = json.loads(data)
                if "url" in j:
                    if j['name'] == '' or j['images'] == []:
                        records.append(j['url'].strip())
    records = list(set(records))
    print('No of error urls = ', len(records))
    with open('files/error_urls.txt', 'w') as f:
        f.write("\n".join(records))

def generate_good_saved_urls():
    import simplejson as json
    records = []
    urls = []
    with open('files/global_data.txt','r') as f:
        lines = f.readlines()
        for line in lines:
                data = line.strip()
                j = json.loads(data)
                if "url" in j:
                    if j['name'] != '' and j['images'] != []:
                        records.append(data)
                        urls.append(j['url'])
    records = list(set(records))
    with open('files/ok_urls_with_data.txt', 'w') as f:
        f.write("\n".join(records))
    urls = list(set(urls))
    with open('files/ok_urls.txt', 'w') as f:
        f.write("\n".join(urls))
    print('No of ok urls = ', len(records))

def generate_chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def generate_styles_stats():
    from crawler_parser import CrawlerParser
    excel_filename = "styles.csv"
    cp = CrawlerParser(0, 400000000, save_to_s3=True, is_override=True)
    urls = cp.load_urls(excel_filename)
    sub_lists = generate_chunks(urls, 5000)
    return sub_lists

def start_run(urls):
    from crawler_parser import CrawlerParser
    cp = CrawlerParser(0, 400000000, save_to_s3=True, is_override=True)
    cp.start_run(urls)

def run_in_threads(urls_lists):
    import threading
    import multiprocessing
    import shutil
    counter = 0
    try:
        os.system("cat files/error_urls.txt >> files/all_error_urls.txt")
        os.system("rm files/error_urls.txt")
        threads = len(urls_lists)
        if threads > 10:
            threads = 10
        print("No of threads = ", threads)
        jobs = []
        for i in range(0, threads):
            urls = urls_lists[i]
            #thread = threading.Thread(target=start_run(urls))
            #print('URLS:', urls)
            thread = multiprocessing.Process(target=start_run, args=(urls,)) 
            jobs.append(thread)

        # Start the threads (i.e. calculate the random number lists)
        for j in jobs:
            j.start()
        print('All jobs started now..')
        # Ensure all of the threads have finished
        for j in jobs:
            j.join()
    except Exception as ex:
        error = str(traceback.format_exc())
        print('ERROR: Run error = ', error)
    return counter

def main(argv):
    #test_s3_upload()
    from utils import get_dynamodb_table, save_in_dynamodb, get_files_listed_in_s3, download_from_s3, allocate_new_ip
    #table = get_dynamodb_table()
    #print('Table = ', table)
    #save_in_dynamodb('data_files', {"url": "https://www.myntra.com/339469", "brand": "Tweens", "name": "Pink T-shirt Bra", "price": "Rs. 270", "tax": "inclusive of all taxes", "product_details": "Pink, T-shirt bra, has extra padding and seamless cups, non-  wired, elasticated and adjustable, multiway shoulder straps, three rows of double hook-and-eye closure at the back for an adjustable fit\n\nOwing to intimate nature of this product it is eligible for self-ship return only   (no pick-up facility)", "meta_desc": ["100% Original Products", "Free Delivery on order above Rs. 1199", "Cash on delivery might be available", "Easy 30 days returns", "This item is only returnable and not exchangeable"]  , "images": ["https://assets.myntassets.com/h_1136,q_90,w_852/v1/images/style/properties/Tweens-Women-Bra_6ce7fdf23adabbbd0edbdd6dea28e5c5_images.jpg"], "uploaded_images": [{"original": "https://assets.myntassets.com/h_11  36,q_90,w_852/v1/images/style/properties/Tweens-Women-Bra_6ce7fdf23adabbbd0edbdd6dea28e5c5_images.jpg", "uploaded": "cache/339469/https-assets-myntassets-com-h-1136-q-90-w-852-v1-images-style-properties-tweens-women-bra-6  ce7fdf23adabbbd0edbdd6dea28e5c5-images.jpg", "size": "101.2 KB"}], "at": "2020-04-05 13:07:12.341104"})
    if len(argv) < 3:
        #get_files_listed_in_s3("projectstore")
        #download_from_s3("projectstore")
        #generate_done_list()

        #generate_error_urls()
        #generate_good_saved_urls()
        #generate_styles_stats()

        #from utils import update_counter_value
        #update_counter_value()

        allocate_new_ip()
    else:
        generate_error_urls()
        generate_good_saved_urls()
        generate_styles_stats()
        os.system("cat files/ok_urls.txt >> done_urls.txt")
        '''
        from crawler_parser import CrawlerParser
        i = int(argv[1])
        j = int(argv[2])
        is_override = False
        if len(argv) >= 4:
            is_override = True
        cp = CrawlerParser(i, j, save_to_s3=True, is_override=True)
        '''
        lists = list(generate_styles_stats())
        '''
        lists = [["https://www.myntra.com/1132629"],["https://www.myntra.com/1132717"],
  ["https://www.myntra.com/1135579"],
  ["https://www.myntra.com/1141650"],
  ["https://www.myntra.com/1147206"]]
        '''
        run_in_threads(lists)
        #print(len(lists))
    pass

if __name__ == '__main__':
        main(sys.argv)
