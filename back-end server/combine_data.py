# coding:utf-8
import pandas as pd
import datetime
import calendar
import json

output = pd.DataFrame(columns=['date', 'price', 'news'])

stock = pd.read_csv('data/apple.csv')
stock['date'] = pd.to_datetime(stock['date'])
news = pd.read_csv('data/news.csv')
news['date'] = pd.to_datetime(news['date'])


def add_temp(ds: str, price: float, input: pd.DataFrame, b: bool):
    global output
    record = list()
    record.append(ds)
    record.append(price)

    news_dict = dict()
    news_dict['data'] = None
    data = []

    if b:
        input = input.sort_values(by=['score'], ascending=False).reset_index(drop=True)
        for i, rows in input.iterrows():
            temp = dict()
            temp['title'] = rows['title']
            temp['url'] = rows['url']
            data.append(temp)
    else:
        input = input.sort_values(by=['score'], ascending=True).reset_index(drop=True)
        for i, rows in input.iterrows():
            temp = dict()
            temp['title'] = rows['title']
            temp['url'] = rows['url']
            data.append(temp)

    news_dict['data'] = data
    record.append(json.dumps(news_dict))
    output.loc[len(output)] = record


def good(st, et, days_str: str, price: float, data: pd.DataFrame):
    global output
    news_data = []
    temp = news[(st <= news['date']) & (news['date'] < et) & (news['score'] > 0)]
    temp = temp.sort_values(by=['score'], ascending=False).reset_index(drop=True)
    for i, rows in temp.iterrows():
        nd = {}
        nd['title'] = rows['title']
        nd['url'] = rows['url']
        news_data.append(nd)

    temp = news[(st <= news['date']) & (news['date'] < et) & (news['score'] < 0)]
    temp = temp.sort_values(by=['score'], ascending=True).reset_index(drop=True)
    for i, rows in temp.iterrows():
        nd = {}
        nd['title'] = rows['title']
        nd['url'] = rows['url']
        news_data.append(nd)

    newsx = {}
    newsx['data'] = news_data
    newsx = json.dumps(newsx)

    record = []
    record.append(days_str)
    record.append(today_price)
    record.append(newsx)

    output.loc[len(output)] = record


def bad(st, et, days_str: str, price: float, data: pd.DataFrame):
    global output
    news_data = []

    temp = news[(st <= news['date']) & (news['date'] < et) & (news['score'] < 0)]
    temp = temp.sort_values(by=['score'], ascending=True).reset_index(drop=True)
    for i, rows in temp.iterrows():
        nd = {}
        nd['title'] = rows['title']
        nd['url'] = rows['url']
        news_data.append(nd)

    temp = news[(st <= news['date']) & (news['date'] < et) & (news['score'] > 0)]
    temp = temp.sort_values(by=['score'], ascending=False).reset_index(drop=True)
    for i, rows in temp.iterrows():
        nd = {}
        nd['title'] = rows['title']
        nd['url'] = rows['url']
        news_data.append(nd)

    newsx = {}
    newsx['data'] = news_data
    newsx = json.dumps(newsx)

    record = []
    record.append(days_str)
    record.append(today_price)
    record.append(newsx)

    output.loc[len(output)] = record


def get_month_name(input: int):
    return calendar.month_name[input][0:3]


for i, rows in stock.iterrows():
    if i == 0:
        continue
    add_list = []
    st = rows['date'] - datetime.timedelta(days=1)
    et = rows['date'] + datetime.timedelta(hours=9)
    rel_news = news[(st <= news['date']) & (news['date'] < et)]

    today_price = rows['price']
    last_price = stock.loc[i - 1]['price']

    days_str = get_month_name(rows['date'].month) + ' ' + str(rows['date'].day)

    # print(today_price, last_price)
    if today_price > last_price:
        good(st, et, days_str, today_price, rows)

    else:
        bad(st, et, days_str, today_price, rows)

output.to_csv('apple_data.csv', encoding='utf-8')
