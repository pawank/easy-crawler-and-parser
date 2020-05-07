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
    with open('files/done_urls.txt', 'a') as f:
        f.write("\n".join(list(done_map.keys())))


def main(argv):
    #test_s3_upload()
    from utils import get_dynamodb_table, save_in_dynamodb
    #table = get_dynamodb_table()
    #print('Table = ', table)
    #save_in_dynamodb('data_files', {"url": "https://www.myntra.com/339469", "brand": "Tweens", "name": "Pink T-shirt Bra", "price": "Rs. 270", "tax": "inclusive of all taxes", "product_details": "Pink, T-shirt bra, has extra padding and seamless cups, non-  wired, elasticated and adjustable, multiway shoulder straps, three rows of double hook-and-eye closure at the back for an adjustable fit\n\nOwing to intimate nature of this product it is eligible for self-ship return only   (no pick-up facility)", "meta_desc": ["100% Original Products", "Free Delivery on order above Rs. 1199", "Cash on delivery might be available", "Easy 30 days returns", "This item is only returnable and not exchangeable"]  , "images": ["https://assets.myntassets.com/h_1136,q_90,w_852/v1/images/style/properties/Tweens-Women-Bra_6ce7fdf23adabbbd0edbdd6dea28e5c5_images.jpg"], "uploaded_images": [{"original": "https://assets.myntassets.com/h_11  36,q_90,w_852/v1/images/style/properties/Tweens-Women-Bra_6ce7fdf23adabbbd0edbdd6dea28e5c5_images.jpg", "uploaded": "cache/339469/https-assets-myntassets-com-h-1136-q-90-w-852-v1-images-style-properties-tweens-women-bra-6  ce7fdf23adabbbd0edbdd6dea28e5c5-images.jpg", "size": "101.2 KB"}], "at": "2020-04-05 13:07:12.341104"})
    generate_done_list()
    if True:
        from crawler_parser import CrawlerParser
        i = int(argv[1])
        j = int(argv[2])
        cp = CrawlerParser(i, j, save_to_s3=True)
        cp.run()
    pass

if __name__ == '__main__':
        main(sys.argv)
