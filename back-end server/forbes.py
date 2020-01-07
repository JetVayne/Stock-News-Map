# coding: utf-8
import re
import time
import requests
import bs4
from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# from urllib.parse import urlparse
# import urllib.request
# import json
# import os
import datetime
import pandas as pd

base_time = '2019-01-01'
base_ts = datetime.datetime.now().replace(microsecond=0).timestamp()
url_set = set()
art_data = list()
output = pd.DataFrame(columns=['articleDate', 'title', 'views', 'content', 'author', 'url'])


def crawler():
    global url_set, art_data
    url_token = 'https://www.forbes.com/simple-data/search/more/?q=Apple&start='
    news_index = 0
    flag = True
    null = 0
    while flag:
        time_error = 0
        url = url_token + str(news_index)
        doc = get_doc(url)
        if doc:
            article_list = doc.select('article')
            if len(article_list) != 0:
                for article in article_list:
                    ts = article.select('div.stream-item__date')[0].get('data-date')
                    art_date = get_time(ts)
                    # print(art_date)
                    if check_time(art_date):
                        art_url = article.select('a.stream-item__title')[0].get('href')
                        views = get_views(article)
                        # print(views)
                        if views == 0:
                            print('***', url)

                        vps = get_vps(views, art_date)
                        x_vps = int(vps * 100000)

                        if art_url not in url_set:
                            url_set.add(art_url)
                            record = dict()
                            record['url'] = art_url
                            record['views'] = views
                            record['vps'] = vps
                            record['x_vps'] = x_vps
                            record['time'] = art_date
                            art_data.append(record)

                    else:
                        time_error += 1
                    # break
            else:
                null += 1

        if time_error == 20:
            flag = False

        news_index += 20

        # break


def get_views(el: bs4.BeautifulSoup):
    result = 0
    vs = el.select('div.stream-item__views')
    if len(vs) == 0 or len(vs[0].text) == 0:
        return result

    ts_str = vs[0].text.replace(',', '')
    regex = re.findall(r'[0-9]+', ts_str)
    if len(regex) == 0:
        return result
    if regex[0].isnumeric():
        result = int(regex[0])
    else:
        return result

    return result


def get_vps(views: int, art_date: datetime.datetime):
    pass_sec = base_ts - art_date.timestamp()
    vps = views / pass_sec
    return vps


def check_time(input: datetime.datetime):
    base = datetime.datetime.strptime(base_time, '%Y-%m-%d')
    if input >= base:
        return True
    else:
        return False


def get_time(ts: str):
    if len(ts) > 10:
        ts = int(ts[0:10])
    elif len(ts) == 10:
        ts = int(ts)

    return datetime.datetime.fromtimestamp(ts)


def get_doc(url: str) -> bs4.BeautifulSoup:
    result = None
    for i in range(3):
        res = None
        try:
            res = requests.get(url)
        except Exception as e:
            print('Failed to grt page. ', url)
            print(e)
            # time.sleep(3)
            continue

        if res.status_code == 200:
            res.encoding = 'utf8'
            html = res.text
            html = html.encode("utf8", 'ignore').decode("utf8", "ignore")
            clean_html = get_clean_html(html)
            doc = None
            try:
                doc = BeautifulSoup(clean_html, 'html.parser')
            except Exception as e:
                print('Failed to parse res to doc. ', url)
                print(e)
                continue

            result = doc
            break
        else:
            time.sleep(3)
            continue

    return result


def parse_article():
    for data in art_data:
        url = data['url']
        views = data['views']
        vps = data['vps']
        x_vps = data['x_vps']
        art_time = str(data['time'])
        doc = get_doc(url)
        time.sleep(5)
        if doc:
            article_el = doc.select('page[id = "article-0"]')
            if len(article_el) == 0:
                print('***')
                print(data)
                try:
                    print(doc)
                except Exception as e:
                    print(e)
                    pass
                print(article_el)
                print()
                continue

            article = article_el[0]
            title = article.select('h1.fs-headline.speakable-headline.font-base')[0].text
            author = article.select(
                'div.fs-author-name.contrib-byline-author.speakable-author > a[data-ga-track = "contrib block byline"]')[
                0].text
            content = get_content(article)
            # print(content)

            record = [art_time, title, views, content, author, url]
            save(record)

        # break


def get_clean_html(input: str):
    replace_list = ['&nbsp;', u'\xa0', u'\u0000', u'\xa9', u'\u20ac',
                    u'\xeb', u'\xa3', u'\xf8', u'\U0001f308', u'\u02bb',
                    u'\xe7', u'\xbb', u'\xb3', u'\U0001f3f4', u'\xe4',
                    u'\u2011', u'\U0001f64c', u'\xf1', u'\xae', u'\U0001f384']
    result = input
    for rs in replace_list:
        result = result.replace(rs, '')

    return result


def save(record: list):
    global output
    output.loc[len(output)] = record


def get_content(article: bs4.BeautifulSoup):
    temp_content = article.select('div.article-container.color-body.font-body > div')[0].children

    clean = []
    for i in temp_content:
        if i.name == 'p':
            clean.append(i)

    result = ''
    for i in clean:
        result += i.text.strip()

    return result


def output_data():
    global output
    output = output.sort_values(['articleDate']).reset_index(drop=True)
    output.to_csv('apple2019-3.csv', encoding='utf8')


def main():
    crawler()
    parse_article()
    output_data()
    # print(output)


if __name__ == '__main__':
    main()
