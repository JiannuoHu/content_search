import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def scrape_wsj_news(event, context):

    date_range_high = datetime.today().date()
    date_range_low = datetime.today().date() - timedelta(days=7)

    user_agent = 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405'
    wsj_deals_url = "https://www.wsj.com/news/types/deals-deal-makers?page={}"
    page_number = 1
    date_filter = date_range_high

    title_list = []
    date_list = []
    link_list = []

    while date_filter >= date_range_low:
        wsj_raw = requests.get(wsj_deals_url.format(page_number), headers={'User-Agent': user_agent})
        status = True
        timer = 0

        while status and timer <=9:
            if wsj_raw.status_code != 200:
                print("wsj page {} status code is not 200, entering sleep for 3 seconds".format(page_number))
                time.sleep(3)
                timer += 3
                wsj_raw = requests.get(wsj_deals_url.format(page_number), headers={'User-Agent': user_agent})
            else:
                status = False
        
        if wsj_raw.status_code == 200:

            wsj_bs4 = BeautifulSoup(wsj_raw.content, features="lxml")

            for article in wsj_bs4.select('h2[class*="headline"]'):
                content = article.get_text()
                link = article.find('a')['href']
                title_list.append(content)
                link_list.append(link)

            combined_ts = wsj_bs4.select('div[class*="timestamp"]')
            if combined_ts != []:
                for timestamp in combined_ts:
                    try:
                        a_date = timestamp.find('div').get_text()
                        a_date = datetime.strptime(a_date, "%B %d, %Y").date()
                        date_list.append(a_date)
                    except:
                        pass
            else:
                a_date = datetime.today().date() - timedelta(days=8)

            date_filter = a_date
            page_number += 1
        
        else:
            date_filter = datetime.today().date() - timedelta(days=8)

    wsj_news_dict = dict(zip(title_list, zip(date_list, link_list)))
    wsj_news_dict = {title: info[1] for title, info in wsj_news_dict.items() if info[0] >= date_range_low}

    return wsj_news_dict