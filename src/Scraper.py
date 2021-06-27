import requests
import time
import threading
import datetime
from tqdm import tqdm

class Scraper:

    def __init__(self, sleep_time=1):
        self.__sleep_time = sleep_time

    
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
                print('\n[Error] Connection Error: key ' + str(key))
                print(e)

        return func
        

    def run(self, urls, keys=None):
        l = len(urls)

        if keys == None:
            self.htmls = list()
        else:
            self.htmls = dict()

        if keys != None and len(keys) != l:
            print('[Error] The length of keys must be the same as the length of urls.')
            return self.htmls

        dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))) + datetime.timedelta(seconds=l * self.__sleep_time)
        print('[Info] Start scraping ' + str(l) + ' urls.  This will finish until ' + str(dt))
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
