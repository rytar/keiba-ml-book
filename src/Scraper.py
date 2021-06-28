import requests
import time
import threading
import datetime
import logging
from tqdm import tqdm

class Scraper:

    def __init__(self, sleep_time=1):
        self.__sleep_time = sleep_time
        
        self.__logger = logging.getLogger(__name__)
        
        fh = logging.FileHandler('./scraper.log', mode='w')
        
        fmt = logging.Formatter('%(asctime)s: %(message)s', '%Y-%m-%dT%H:%M:%S')
        fh.setFormatter(fmt)
        
        self.__logger.addHandler(fh)
        self.__logger.setLevel(logging.DEBUG)

    
    def __get_html(self, url, key=None):
        def func():
            try:
                res = requests.get(url, timeout=30.0)
                res.raise_for_status()
                if key == None:
                    self.htmls.append(res.content)
                else:
                    self.htmls[key] = res.content
            except Exception as e:
                message = '[Error] Connection Error: key ' + str(key)
                self.__logger.error(message)
                print('\n' + message)
                print(e)

        return func
        

    def run(self, urls, keys=None):
        l = len(urls)

        if keys == None:
            self.htmls = list()
        else:
            self.htmls = dict()

        if keys != None and len(keys) != l:
            message = '[Error] The length of keys must be the same as the length of urls.'
            self.__logger.error(message)
            print(message)
            return self.htmls

        dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))) + datetime.timedelta(seconds=l * self.__sleep_time)
        
        message = '[Info] Start scraping ' + str(l) + ' urls.  This will finish until ' + str(dt)
        self.__logger.info(message)
        print(message)
        print('')

        size = 30
        bar = tqdm(total=l, desc='progress', ncols=100)
        for s in range(int(l / size)):
            threads = list()

            for i, url in enumerate(urls[s * size : min((s + 1) * size, l)]):
                if keys == None:
                    t = threading.Thread(target=self.__get_html(url))
                else:
                    t = threading.Thread(target=self.__get_html(url, key=keys[i]))
                t.start()
                threads.append(t)
                bar.update(1)
                time.sleep(self.__sleep_time)

            for t in threads:
                t.join()

        print('')

        return self.htmls
