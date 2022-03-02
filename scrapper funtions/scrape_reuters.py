import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def scrape_reuters_news(event, context):

    date_range_high = datetime.today().date()
    date_range_low = datetime.today().date() - timedelta(days=7)
    user_agent = 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405'

    date_filter = date_range_high
    page_number = 1
    reuters_news_dict = {}
    reuters_news_url = "https://www.reuters.com/news/archive/mergersnews?view=page&page={}&pageSize=10"

    while date_filter >= date_range_low:

        reuters_raw = requests.get(reuters_news_url.format(page_number), headers={'User-Agent': user_agent})
        reuters_bs4 = BeautifulSoup(reuters_raw.content, features="lxml")

        reuters_news_block = reuters_bs4.find_all('div', class_ = 'column1 col col-10')
        reuters_news_list  = reuters_news_block[0].find_all('h3', class_ = 'story-title')
        reuters_timestamp_list = reuters_news_block[0].find_all('span', class_ = 'timestamp')

        link_list = [i.find('a')['href'] for i in reuters_news_block[0].find_all('div', class_ = 'story-content')]
        link_list = ['reuters.com'+ i for i in link_list]

        for i in range(len(reuters_news_list)):
            title = reuters_news_list[i].get_text()
            title = title.split('\n\t\t\t\t\t\t\t\t')[1]

            a_date = reuters_timestamp_list[i].get_text()
            if 'am' in a_date or 'pm' in a_date:
                a_date = datetime.today().date()
            else:
                a_date = datetime.strptime(a_date, "%b %d %Y").date()

            reuters_news_dict[title] = [a_date, link_list[i]]

        date_filter = a_date
        page_number += 1
    
    reuters_news_dict = {title: info[1] for title, info in reuters_news_dict.items() if info[0] >= date_range_low}

    return reuters_news_dict

