import requests
import time
import threading
from tqdm import tqdm

class Scraper:

    def __init__(self, sleep_time=1):
        self.__sleep_time = sleep_time

    
    def __get_html(self, url):
        def func():
            try:
                res = requests.get(url)
                res.raise_for_status()
                self.htmls.append(res.content)
            except Exception as e:
                print(e)

        return func
        

    def run(self, urls):
        print('[Info] Start scraping ' + str(len(urls)) + ' urls.')
        
        self.htmls = list()

        base_time = time.time()
        next_time = 0
        for url in tqdm(urls):
            t = threading.Thread(target=self.__get_html(url))
            t.start()
            next_time = ((base_time - time.time()) % self.__sleep_time) or self.__sleep_time
            time.sleep(next_time)

        return self.htmls
