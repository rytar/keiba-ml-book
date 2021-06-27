import itertools
from src.Scraper import Scraper

def analyze(html):
    pass

def main():
    start_year = 2011
    end_year = 2020
    years = [ str(year) for year in range(start_year, end_year + 1) ]
    codes = [ str(i + 1).zfill(2) for i in range(10) ]
    race_counts = [ str(i + 1).zfill(2) for i in range(6) ]
    days = [ str(i + 1).zfill(2) for i in range(8) ]
    race_nums = [ str(i + 1).zfill(2) for i in range(12) ]
    race_ids = list(itertools.product(years, codes, race_counts, days, race_nums))
    race_ids = [ ''.join(race_id) for race_id in race_ids ]
    urls = [ 'https://race.netkeiba.com/race/result.html?race_id={}'.format(race_id) for race_id in race_ids ]

    scraper = Scraper()
    htmls = scraper.run(urls, keys=race_ids)
    print(htmls)

if __name__ == '__main__':
    main()