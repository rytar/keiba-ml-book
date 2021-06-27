import requests
import time
import threading
import datetime
from tqdm import tqdm

class Scraper:

    def __init__(self, sleep_time=1):
        self.__sleep_time = sleep_time

    
    def __get_html(self, url, key):
        def func():
            try:
                res = requests.get(url)
                res.raise_for_status()
                self.htmls[key] = res.content
            except Exception as e:
                print(e)

        return func
        

    def run(self, urls, keys=None):
        l = len(urls)
        self.htmls = dict()

        if len(keys) != l:
            print('[Error] The length of keys must be the same as the length of urls.')
            return self.htmls

        dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))) + datetime.timedelta(seconds=l * self.__sleep_time)
        print('[Info] Start scraping ' + str(l) + ' urls.  This will finish until ' + str(dt))

        if keys == None:
            keys = range(l)

        base_time = time.time()
        next_time = 0
        bar = tqdm(total=l)
        bar.set_description('progress')
        for url, key in zip(urls, keys):
            t = threading.Thread(target=self.__get_html(url, key))
            t.start()
            bar.update(1)
            next_time = ((base_time - time.time()) % self.__sleep_time) or self.__sleep_time
            time.sleep(next_time)

        return self.htmls
