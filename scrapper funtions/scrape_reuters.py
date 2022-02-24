import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def scrape_reuters_news():
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

        for i in range(len(reuters_news_list)):
            title = reuters_news_list[i].get_text()
            title = title.split('\n\t\t\t\t\t\t\t\t')[1]

            a_date = reuters_timestamp_list[i].get_text()
            if 'am' in a_date or 'pm' in a_date:
                a_date = datetime.today().date()
            else:
                a_date = datetime.strptime(a_date, "%b %d %Y").date()

            reuters_news_dict[title] = a_date

        date_filter = a_date
        page_number += 1


    elephants = pd.read_excel('elephants.xlsx')
    elephants_dict = elephants.set_index('Client').to_dict('index')

    # results = {}

    # for client in elephants_dict.keys():
    #     client_res = []
    #     for title, date in reuters_news_dict.items():
    #         if client.lower() in title.lower():
    #             client_res.append(title)
    #     if client_res:
    #         results[client] = {'news': client_res, 'broker': elephants_dict[client]['Broker'], 'broker_email':elephants_dict[client]['Broker Email']}

    return reuters_news_dict

