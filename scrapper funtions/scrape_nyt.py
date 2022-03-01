import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def scrape_nyt_news():
    date_range_low = datetime.today().date() - timedelta(days=7)
    user_agent = 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405'
    ma_news_url = "https://www.nytimes.com/topic/subject/mergers-acquisitions-and-divestitures"
    nyt_raw = requests.get(ma_news_url, headers={'User-Agent': user_agent})

    status = True
    timer = 0

    while status and timer <=9:
        if nyt_raw.status_code != 200:
            print("nyt status code is not 200, entering sleep for 3 seconds")
            time.sleep(3)
            timer += 3
            nyt_raw = requests.get(ma_news_url, headers={'User-Agent': user_agent})
        else:
            status = False

    title_list = []
    date_list = []

    if nyt_raw.status_code == 200:
        nyt_content = BeautifulSoup(nyt_raw.content)

        title_list = nyt_content.find_all('ol')[0].find_all('h2')
        link_list = nyt_content.find_all('ol')[0].find_all('a')

        if title_list !=[] and link_list !=[]:
            try:
                title_list = [i.get_text() for i in title_list]
                
                date_list = []
                link_list = [i['href'].split('/')[1:4] for i in link_list]
                
                for sub in link_list:
                    date_elements = [int(i) for i in sub]
                    a_date = datetime(year = date_elements[0], month = date_elements[1], day = date_elements[2]).date()
                    date_list.append(a_date)
            except:
                title_list = []
                date_list = []
        else:
            title_list = []
            date_list = []

    nyt_ma_news_dict = dict(zip(title_list, date_list))
    nyt_ma_news_dict = {title: str(date) for title, date in nyt_ma_news_dict.items() if date >= date_range_low}

    return nyt_ma_news_dict

