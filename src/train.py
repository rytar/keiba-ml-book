import pandas as pd
import numpy as np
import warnings
import json
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense, Activation

def make_data(df, horse_data, to_future=False):
    frame_list = [ (int(frame) - 1) / 7 for frame in df['frame'].values ]
    number_list = [ (int(number) - 1) / 17 for number in df['number'].values ]
    # num_list = [ (len(number_list) - 1) / 17 ] * len(number_list)
    prob_list = [ 0.8 / odds if not np.isnan(odds) else 0 for odds in df['odds'].values.astype(np.float32) ]
    sex_and_age_list = df['sex_and_age'].values
    sex_list1 = []
    sex_list2 = []
    sex_list3 = []
    age_list = []
    max_age = 15
    min_age = 2
    for sex_and_age in sex_and_age_list:
        sex = sex_and_age[0]
        if sex == '騙' or sex == 'セ':
            sex_list1.append(1)
            sex_list2.append(0)
            sex_list3.append(0)
        elif sex == '牡':
            sex_list1.append(0)
            sex_list2.append(1)
            sex_list3.append(0)
        elif sex == '牝':
            sex_list1.append(0)
            sex_list2.append(0)
            sex_list3.append(1)
        else:
            print('sex: ' + sex)

        age = int(sex_and_age[1:])
        age_list.append((age - min_age) / (max_age - min_age))

    max_impost = 62
    min_impost = 48
    impost_list = [ (float(impost) - min_impost) / (max_impost - min_impost) for impost in df['impost'].values ]

    max_distance = 3600
    min_distance = 600
    distance_list = [ (int(distance) - min_distance) / (max_distance - min_distance) for distance in df['distance'].values ]

    # weight_list = []
    # weight_change_list = []
    # max_weight = 640
    # min_weight = 330
    # max_wc = 30
    # min_wc = -30
    # for weight in df['weight'].values:
    #     if type(weight) is float:
    #         w = 0.0
    #         wc = 0.0
    #     elif not '(' in weight:
    #         w = float(weight)
    #         wc = 0.0
    #     else:
    #         weight = weight.replace(')', '')
    #         w = float(weight.split('(')[0])
    #         wc = weight.split('(')[1]
    #         if wc == '前計不':
    #             wc = 0.0
    #         else:
    #             wc = float(wc)
    #     weight_list.append((w - min_weight) / (max_weight - min_weight))
    #     weight_change_list.append((wc - min_wc) / (max_wc - min_wc))

    # cource_list1 = []
    # cource_list2 = []
    # cource_list3 = []
    # for cource in df['cource'].values:
    #     if cource == '芝':
    #         cource_list1.append(1)
    #         cource_list2.append(0)
    #         cource_list3.append(0)
    #     elif cource == 'ダ':
    #         cource_list1.append(0)
    #         cource_list2.append(1)
    #         cource_list3.append(0)
    #     elif cource == '障':
    #         cource_list1.append(0)
    #         cource_list2.append(0)
    #         cource_list3.append(1)
    #     else:
    #         print('cource: ' + cource)

    # turn_list1 = []
    # turn_list2 = []
    # turn_list3 = []
    # turn_list4 = []
    # for turn in df['turn'].values:
    #     if turn == '左':
    #         turn_list1.append(1)
    #         turn_list2.append(0)
    #         turn_list3.append(0)
    #         turn_list4.append(0)
    #     elif turn == '右':
    #         turn_list1.append(0)
    #         turn_list2.append(1)
    #         turn_list3.append(0)
    #         turn_list4.append(0)
    #     elif turn == '直':
    #         turn_list1.append(0)
    #         turn_list2.append(0)
    #         turn_list3.append(1)
    #         turn_list4.append(0)
    #     else:
    #         turn_list1.append(0)
    #         turn_list2.append(0)
    #         turn_list3.append(0)
    #         turn_list4.append(1)

    # condition_list1 = []
    # condition_list2 = []
    # condition_list3 = []
    # condition_list4 = []
    # for condition in df['condition'].values:
    #     if condition == '良':
    #         condition_list1.append(1)
    #         condition_list2.append(0)
    #         condition_list3.append(0)
    #         condition_list4.append(0)
    #     elif condition == '稍':
    #         condition_list1.append(0)
    #         condition_list2.append(1)
    #         condition_list3.append(0)
    #         condition_list4.append(0)
    #     elif condition == '重':
    #         condition_list1.append(0)
    #         condition_list2.append(0)
    #         condition_list3.append(1)
    #         condition_list4.append(0)
    #     elif condition == '不':
    #         condition_list1.append(0)
    #         condition_list2.append(0)
    #         condition_list3.append(0)
    #         condition_list4.append(1)
    #     else:
    #         print('condition: ' + condition)

    past_1st_list = []
    past_2nd_list = []
    past_3rd_list = []
    past_velocity_list = []
    past_3f_time_list = []
    max_3f_time = 45
    min_3f_time = 31

    for horse_name, place, year in zip(df['name'].values, df['place'].values, df['year'].values):
        place = place.replace('回', '').replace('日目', '')

        horse_df = pd.DataFrame(horse_data[horse_name])
        horse_df = horse_df.dropna(how='any')

        past_1st_count = 0
        past_2nd_count = 0
        past_3rd_count = 0
        past_velocity_sum = 0
        past_3f_time_sum = 0
        count = 0
        cond = to_future
        for i, row in horse_df[['date', 'place', 'rank', 'distance', 'time', 'time_3f']].iterrows():
            if not cond:
                cond = int(row['date'].split('/')[0]) == year and place == row['place']
                continue

            if row['rank'] == '中' or row['rank'] == '取' or row['rank'] == '除' or row['rank'] == '失' or row['time_3f'] == '':
                continue

            if str(row['rank']) == '1':
                past_1st_count += 1
            elif str(row['rank']) == '2':
                past_2nd_count += 1
            elif str(row['rank']) == '3':
                past_3rd_count += 1

            time = row['time']
            if type(time) is float or time == '':
                print(horse_df)
            if len(time.split(':')) == 2:
                time = 60 * int(time.split(':')[0]) + float(time.split(':')[1])
            else:
                time = float(time)

            past_velocity_sum += time / int(row['distance'][1:])

            past_3f_time_sum += (float(row['time_3f']) - min_3f_time) / (max_3f_time - min_3f_time)

            count += 1

        past_1st_list.append(past_1st_count / count if count != 0 else 0)
        past_2nd_list.append(past_2nd_count / count if count != 0 else 0)
        past_3rd_list.append(past_3rd_count / count if count != 0 else 0)
        past_velocity_list.append(past_velocity_sum / count if count != 0 else 0)
        past_3f_time_list.append(past_3f_time_sum / count if count != 0 else 0)

    
    new_df = pd.DataFrame({
        'frame': frame_list,
        'number': number_list,
        # 'num': num_list,
        'prob': prob_list,
        'sex1': sex_list1,
        'sex2': sex_list2,
        'sex3': sex_list3,
        'age': age_list,
        'impost': impost_list,
        'distance': distance_list,
        # 'weight': weight_list,
        # 'weight_change': weight_change_list,
        # 'cource1': cource_list1,
        # 'cource2': cource_list2,
        # 'cource3': cource_list3,
        # 'turn1': turn_list1,
        # 'turn2': turn_list2,
        # 'turn3': turn_list3,
        # 'turn4': turn_list4,
        # 'condition1': condition_list1,
        # 'condition2': condition_list2,
        # 'condition3': condition_list3,
        # 'condition4': condition_list4,
        'past_1st_rate': past_1st_list,
        'past_2nd_rate': past_2nd_list,
        'past_3rd_rate': past_3rd_list,
        'past_velocity_list': past_velocity_list,
        'past_3f_time_list': past_3f_time_list,
        # 'all_past_1st_rate': np.mean(past_1st_list),
        # 'all_past_2nd_rate': np.mean(past_2nd_list),
        # 'all_past_3rd_rate': np.mean(past_3rd_list),
        # 'all_past_velocity_list': np.mean(past_velocity_list),
        # 'all_past_3f_time_list': np.mean(past_3f_time_list),
        # 'min_past_1st_rate': np.min(past_1st_list),
        # 'past_1st_rate_25%': np.percentile(past_1st_list, 25),
        'past_1st_rate_50%': np.percentile(past_1st_list, 50),
        # 'past_1st_rate_75%': np.percentile(past_1st_list, 75),
        # 'max_past_1st_rate': np.max(past_1st_list),
        'past_1st_rate_rank': np.flip(np.argsort(np.argsort(past_1st_list))) / (len(past_1st_list) - 1),
        # 'min_past_1st_rate': np.min(past_1st_list),
        # 'past_2nd_rate_25%': np.percentile(past_2nd_list, 25),
        'past_2nd_rate_50%': np.percentile(past_2nd_list, 50),
        # 'past_2nd_rate_75%': np.percentile(past_2nd_list, 75),
        'max_past_2nd_rate': np.max(past_2nd_list),
        # 'past_2nd_rate_rank': np.flip(np.argsort(np.argsort(past_2nd_list))) / (len(past_2nd_list) - 1),
        # 'min_past_3rd_rate': np.min(past_3rd_list),
        # 'past_3rd_rate_25%': np.percentile(past_3rd_list, 25),
        'past_3rd_rate_50%': np.percentile(past_3rd_list, 50),
        # 'past_3rd_rate_75%': np.percentile(past_3rd_list, 75),
        # 'max_past_3rd_rate': np.max(past_3rd_list),
        'past_3rd_rate_rank': np.flip(np.argsort(np.argsort(past_3rd_list))) / (len(past_3rd_list) - 1),
        # 'min_past_velocity_rate': np.min(past_velocity_list),
        # 'past_velocity_rate_25%': np.percentile(past_velocity_list, 25),
        'past_velocity_rate_50%': np.percentile(past_velocity_list, 50),
        # 'past_velocity_rate_75%': np.percentile(past_velocity_list, 75),
        # 'max_past_velocity_rate': np.max(past_velocity_list),
        'past_velocity_rate_rank': np.flip(np.argsort(np.argsort(past_velocity_list))) / (len(past_velocity_list) - 1),
        # 'min_past_1st_rate': np.min(past_3f_time_list),
        # 'past_3f_time_rate_25%': np.percentile(past_3f_time_list, 25),
        'past_3f_time_rate_50%': np.percentile(past_3f_time_list, 50),
        # 'past_3f_time_rate_75%': np.percentile(past_3f_time_list, 75),
        # 'max_past_3f_time_rate': np.max(past_3f_time_list),
        'past_3f_time_rate_rank': np.flip(np.argsort(np.argsort(past_3f_time_list))) / (len(past_3f_time_list) - 1),
    })

    return new_df

def make_dataset(race_data, horse_data):
    warnings.simplefilter(action='ignore', category=FutureWarning)

    X = None
    Y = None
    first_data = False
    for race_id in tqdm(race_data, desc='make dataset'):
        df = pd.DataFrame(race_data[race_id])
        df = make_data(df, horse_data)

        rank_list = df['rank'].values
        n = len(rank_list)
        if np.any(rank_list == '中止') or np.any(rank_list == '取消') or np.any(rank_list == '除外') or np.any(rank_list == '失格'):
            continue

        rank_1st_list = []
        rank_2nd_list = []
        rank_3rd_list = []
        rank_other_list = []
        ranks = np.zeros((n, n))
        for i, rank in enumerate(rank_list):
            ranks[i][rank - 1] = 1

            if int(rank) == 1:
                rank_1st_list.append(1)
                rank_2nd_list.append(0)
                rank_3rd_list.append(0)
                rank_other_list.append(0)
            elif int(rank) == 2:
                rank_1st_list.append(0)
                rank_2nd_list.append(1)
                rank_3rd_list.append(0)
                rank_other_list.append(0)
            elif int(rank) == 3:
                rank_1st_list.append(0)
                rank_2nd_list.append(0)
                rank_3rd_list.append(1)
                rank_other_list.append(0)
            else:
                rank_1st_list.append(0)
                rank_2nd_list.append(0)
                rank_3rd_list.append(0)
                rank_other_list.append(1)

        output_data = pd.DataFrame({
            '1st': rank_1st_list,
            '2nd': rank_2nd_list,
            '3rd': rank_3rd_list,
            'other': rank_other_list,
        })

        if not first_data:
            X = df.values
            Y = output_data.values
        else:
            X = np.concatenate([X, df.values])
            Y = np.concatenate([Y, output_data.values])

    return X, Y


def main():
    race_data_path = './data/race_data.json'
    horse_data_path = './data/horse_data.json'

    race_data = dict()
    with open(race_data_path, 'r') as f:
        race_data = json.load(f)

    horse_data = dict()
    with open(horse_data_path, 'r') as f:
        horse_data = json.load(f)

    X, Y = make_dataset(race_data, horse_data)
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, shuffle=True, train_size=0.9)
    X_train, X_validation, Y_train, Y_validation = train_test_split(X_train, Y_train, train_size=8/9)

    model = Sequential()

    model.add(Dense(32, input_shape=(24,)))
    model.add(Activation('relu'))
    model.add(Dense(4))
    model.add(Activation('softmax'))

    model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])

    model.summary()

    epochs = 100
    batch_size = 100
    hist = model.fit(X_train, Y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_validation, Y_validation))

    loss_and_metrics = model.evaluate(X_test, Y_test)
    print(loss_and_metrics)

    model.save('./model/simple')


if __name__ == '__main__':
    main()