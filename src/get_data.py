import itertools
import lxml
import json
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
from src.Scraper import Scraper

def analyze_race_data(html, race_id):
    soup = BeautifulSoup(html, 'lxml')

    rank_list = list()
    frame_list = list()
    number_list = list()
    name_list = list()
    sex_and_age_list = list()
    impost_list = list()
    jockey_list = list()
    time_list = list()
    time_diff_list = list()
    popularity_list = list()
    odds_list = list()
    time_3f_list = list()
    pass_order_list = list()
    stable_list = list()
    weight_list = list()

    race_table = soup.find('table', class_=re.compile('RaceTable01 RaceCommon_Table ResultRefund Table_Show_All'))
    
    if race_table == None:
        return {}, {}

    race_body = race_table.find('tbody')
    race_row = race_body.find_all('tr')

    for row in race_row:
        cols = row.find_all('td')

        rank_list.append(cols[0].get_text(strip=True))
        frame_list.append(cols[1].get_text(strip=True))
        number_list.append(cols[2].get_text(strip=True))
        name_list.append(cols[3].get_text(strip=True))
        sex_and_age_list.append(cols[4].get_text(strip=True))
        impost_list.append(cols[5].get_text(strip=True))
        jockey_list.append(cols[6].get_text(strip=True))
        time_list.append(cols[7].get_text(strip=True))
        time_diff_list.append(cols[8].get_text(strip=True))
        popularity_list.append(cols[9].get_text(strip=True))
        odds_list.append(cols[10].get_text(strip=True))
        time_3f_list.append(cols[11].get_text(strip=True))
        pass_order_list.append(cols[12].get_text(strip=True))
        stable_list.append(cols[13].get_text(strip=True))
        weight_list.append(cols[14].get_text(strip=True))

    spans = soup.find_all('span')
    distance_cource = re.search(r'.[0-9]+m', str(spans))
    cource = distance_cource.group()[0]

    distance = re.sub('\\D', '', distance_cource.group()[1:5])

    tw_soup = soup.find_all('div', class_='RaceData01')
    turn = re.search(r'\(.*\)', str(tw_soup)).group()[1]

    if len(str(tw_soup).split('天候:')) > 1:
        weather = str(tw_soup).split('天候:')[1].split('<')[0]
    else:
        weather = "晴"

    condition = soup.find_all('span', class_='Item03')
    if len(condition) == 0:
        condition = soup.find_all('span', class_='Item04')

    if len(condition) != 0:
        condition = condition[0].get_text(strip=True).replace('/ 馬場:', '')
    else:
        condition = "良"

    race_name = soup.find('div', class_='RaceName').get_text(strip=True)

    race_info = soup.find('div', class_='RaceData02')
    race_info_spans = race_info.find_all('span')
    place = race_info_spans[0].get_text(strip=True) + race_info_spans[1].get_text(strip=True) + race_info_spans[2].get_text(strip=True)

    horse_urls = dict()

    for name in name_list:
        horse_url = race_body.find('a', title=name).get('href').replace('horse/', 'horse/result/')
        horse_urls[name] = horse_url
    
    result = {
        'rank': rank_list,
        'frame': frame_list,
        'number': number_list,
        'name': name_list,
        'sex_and_age': sex_and_age_list,
        'impost': impost_list,
        'jockey': jockey_list,
        'time': time_list,
        'time_diff': time_diff_list,
        'popularity': popularity_list,
        'odds': odds_list,
        'time_3f': time_3f_list,
        'pass_order': pass_order_list,
        'stable': stable_list,
        'weight': weight_list,
        'cource': cource,
        'distance': distance,
        'turn': turn,
        'weather': weather,
        'condition': condition,
        'race_name': race_name,
        'place': place,
        'year': race_id[:4],
    }

    return result, horse_urls


def analyze_horse_data(html):
    horse_soup = BeautifulSoup(html, 'lxml')

    h_date_list = list()
    h_place_list = list()
    h_weather_list = list()
    h_R_list = list()
    h_race_name_list = list()
    h_horse_num_list = list()
    h_frame_list = list()
    h_number_list = list()
    h_odds_list = list()
    h_popularity_list = list()
    h_rank_list = list()
    h_jockey_list = list()
    h_impost_list = list()
    h_distance_list = list()
    h_condition_list = list()
    h_time_list = list()
    h_time_diff_list = list()
    h_pass_order_list = list()
    h_pace_list = list()
    h_time_3f_list = list()
    h_weight_list = list()
    h_1st_or_2nd_horse_list = list()
    h_prize_list = list()

    horse_race_table = horse_soup.find('table', class_=re.compile('db_h_race_results nk_tb_common'))
    horse_race_body = horse_race_table.find('tbody')
    horse_race_row = horse_race_body.find_all('tr')

    for row in horse_race_row:
        cols = row.find_all('td')

        h_date_list.append(cols[0].get_text(strip=True))
        h_place_list.append(cols[1].get_text(strip=True))
        h_weather_list.append(cols[2].get_text(strip=True))
        h_R_list.append(cols[3].get_text(strip=True))
        h_race_name_list.append(cols[4].get_text(strip=True))
        h_horse_num_list.append(cols[6].get_text(strip=True))
        h_frame_list.append(cols[7].get_text(strip=True))
        h_number_list.append(cols[8].get_text(strip=True))
        h_odds_list.append(cols[9].get_text(strip=True))
        h_popularity_list.append(cols[10].get_text(strip=True))
        h_rank_list.append(cols[11].get_text(strip=True))
        h_jockey_list.append(cols[12].get_text(strip=True))
        h_impost_list.append(cols[13].get_text(strip=True))
        h_distance_list.append(cols[14].get_text(strip=True))
        h_condition_list.append(cols[15].get_text(strip=True))
        h_time_list.append(cols[17].get_text(strip=True))
        h_time_diff_list.append(cols[18].get_text(strip=True))
        h_pass_order_list.append(cols[20].get_text(strip=True))
        h_pace_list.append(cols[21].get_text(strip=True))
        h_time_3f_list.append(cols[22].get_text(strip=True))
        h_weight_list.append(cols[23].get_text(strip=True))
        h_1st_or_2nd_horse_list.append(cols[26].get_text(strip=True))
        h_prize_list.append(cols[27].get_text(strip=True))


    result = {
        'date': h_date_list,
        'place': h_place_list,
        'weather': h_weather_list,
        'R': h_R_list,
        'race_name': h_race_name_list,
        'horse_num': h_horse_num_list,
        'frame': h_frame_list,
        'number': h_number_list,
        'odds': h_odds_list,
        'popularity': h_popularity_list,
        'rank': h_rank_list,
        'jockey': h_jockey_list,
        'impost': h_impost_list,
        'distance': h_distance_list,
        'condition': h_condition_list,
        'time': h_time_list,
        'time_diff': h_time_diff_list,
        'pass_order': h_pass_order_list,
        'pace': h_pace_list,
        'time_3f': h_time_3f_list,
        'weight': h_weight_list,
        '1st_or_2nd_horse': h_1st_or_2nd_horse_list,
        'prize': h_prize_list,
    }

    return result


def save_dict_as_json(d, filepath):
    with open(filepath, 'w') as f:
        json.dump(d, f, indent=4)


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

    race_data = dict()
    horse_urls = dict()

    print('analyze html about race')

    for race_id in tqdm(htmls):
        race_data[race_id], _horse_urls = analyze_race_data(htmls[race_id], race_id)
        horse_urls.update(_horse_urls)

    save_dict_as_json(race_data, './data/race_data.json')
    
    htmls = scraper.run(horse_urls.values(), keys=list(horse_urls.keys()))

    horse_data = dict()

    print('analyze html about horse')

    for horse_name in tqdm(htmls):
        horse_data[horse_name] = analyze_horse_data(htmls[horse_name])

    save_dict_as_json(horse_data, './data/horse_data.json')
        

if __name__ == '__main__':
    main()