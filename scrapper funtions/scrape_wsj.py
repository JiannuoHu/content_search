import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def scrape_wsj_news():

    date_range_high = datetime.today().date()
    date_range_low = datetime.today().date() - timedelta(days=7)
    user_agent = 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405'
    wsj_deals_url = "https://www.wsj.com/news/types/deals-deal-makers?page={}"
    page_number = 1
    date_filter = date_range_high

    while date_filter >= date_range_low:
        wsj_raw = requests.get(wsj_deals_url.format(page_number), headers={'User-Agent': user_agent})
        wsj_bs4 = BeautifulSoup(wsj_raw.content, features="lxml")

        title_list = []
        for artilce in wsj_bs4.select('h2[class*="headline"]'):
            content = artilce.get_text()
            title_list.append(content)

        date_list = []
        for timestamp in wsj_bs4.select('div[class*="timestamp"]'):
            a_date = timestamp.get_text()
            a_date = datetime.strptime(a_date, "%B %d, %Y").date()
            date_list.append(a_date)

        date_filter = a_date
        page_number += 1

    wsj_news_dict = dict(zip(title_list, date_list))
    wsj_news_dict = {title: date for title, date in wsj_news_dict.items() if date >= date_range_low}

    return wsj_news_dict