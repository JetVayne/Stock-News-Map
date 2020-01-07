import pandas as pd
import nltk
import datetime
from textblob import TextBlob

data_raw = pd.read_csv('data/apple2019.csv')
base_time = '2020-01-01 00:00:00'
output = pd.DataFrame(columns=['date', 'title', 'score', 'url'])


def emotion():
    global output
    aa = set()
    for index, item in data_raw.iterrows():
        content = str(item['content'])
        sentence_list = []
        try:
            sentence_list = nltk.sent_tokenize(content)
        except Exception as e:
            print('***')
            print(e)
            print(content)
            print()

        fs = 0
        for sentence in sentence_list:
            blob = TextBlob(sentence)
            feeling = blob.sentiment[0]
            conf = 100 - blob.sentiment[1]
            fs += feeling * conf

        if fs == 0:
            continue

        hot = count_hot(item)
        fs = round(fs * hot, 9)

        output.loc[len(output)] = [item['articleDate'], item['title'], fs, item['url']]


def count_hot(data: pd.DataFrame):
    views = data['views']
    ad_str = data['articleDate']
    ad = datetime.datetime.strptime(ad_str, '%Y-%m-%d %H:%M:%S')
    base = datetime.datetime.strptime(base_time, '%Y-%m-%d %H:%M:%S')
    diff = base.timestamp() - ad.timestamp()
    result = views / diff

    return result


def main():
    emotion()
    output.to_csv('xx.csv', encoding='utf-8')


if __name__ == '__main__':
    main()
