import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os, shutil, uuid

def scrape_website(event, context):

    func_dict = {'reuters': scrape_reuters_news,
                 'wsj': scrape_wsj_news,
                 'nyt': scrape_nyt_news,
                 'themiddlemarket':scrape_middlemkt_news}

    news_dict = func_dict[event['website']](event, context)
    elephants_list = event['elephants']

    results = {}
    results['records'] = []

    for each_company in elephants_list:

        client = each_company['company']
        client_res = []

        for title in news_dict.keys():
            if client.lower() in title.lower():
               client_res.append(title)

        if client_res:
            results['records'].append({'company':client,
                                       'broker': each_company['broker'], 
                                       'broker_email':each_company['broker_email'],
                                       'news': client_res, })
    
    if not results['records']:
        if news_dict:
            return {'app_success': "we couldn't find any revelant clients from the {} news.".format(event['website'])}
        else:
            return {'app_success': "the website {} might change the html settings".format(event['website'])}
    else:
        results['app_success'] = 'we scrapped news from {} suceessfully'.format(event['website'])

    return results

def setup():
    BIN_DIR = "/tmp/bin"
    if not os.path.exists(BIN_DIR):
        print("Creating bin folder")
        os.makedirs(BIN_DIR)

    LIB_DIR = '/tmp/bin/lib'
    if not os.path.exists(LIB_DIR):
        print("Creating lib folder")
        os.makedirs(LIB_DIR)
        
    for filename in ['chromedriver', 'headless-chromium', 'lib/libgconf-2.so.4', 'lib/libORBit-2.so.0']:
        oldfile = f'/opt/{filename}'
        newfile = f'{BIN_DIR}/{filename}'
        shutil.copy2(oldfile, newfile)
        os.chmod(newfile, 0o775)

def lambda_driver():
    setup()
    chrome_options = webdriver.ChromeOptions()
    _tmp_folder = '/tmp/{}'.format(uuid.uuid4())

    if not os.path.exists(_tmp_folder):
        os.makedirs(_tmp_folder)

    if not os.path.exists(_tmp_folder + '/user-data'):
        os.makedirs(_tmp_folder + '/user-data')

    if not os.path.exists(_tmp_folder + '/data-path'):
        os.makedirs(_tmp_folder + '/data-path')

    if not os.path.exists(_tmp_folder + '/cache-dir'):
        os.makedirs(_tmp_folder + '/cache-dir')

    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280x1696')
    chrome_options.add_argument('--user-data-dir={}'.format(_tmp_folder + '/user-data'))
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--v=99')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--data-path={}'.format(_tmp_folder + '/data-path'))
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--homedir={}'.format(_tmp_folder))
    chrome_options.add_argument('--disk-cache-dir={}'.format(_tmp_folder + '/cache-dir'))
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')

    chrome_options.binary_location = "/tmp/bin/headless-chromium"
    driver = webdriver.Chrome('/tmp/bin/chromedriver', options=chrome_options)

    return driver

def normal_driver():

    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(service = Service("./layers/latest_chromedriver/chromedriver"), options=options)

    return driver

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

        for i in range(len(reuters_news_list)):
            title = reuters_news_list[i].get_text()
            title = title.split('\n\t\t\t\t\t\t\t\t')[1]

            a_date = reuters_timestamp_list[i].get_text()
            if 'am' in a_date or 'pm' in a_date:
                a_date = datetime.today().date()
            else:
                a_date = datetime.strptime(a_date, "%b %d %Y").date()

            reuters_news_dict[title] = str(a_date)

        date_filter = a_date
        page_number += 1

        return reuters_news_dict

def scrape_wsj_news(event, context):

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
    wsj_news_dict = {title: str(date) for title, date in wsj_news_dict.items() if date >= date_range_low}

    return wsj_news_dict


def scrape_nyt_news(event, context):

    date_range_low = datetime.today().date() - timedelta(days=7)

    if context:
        driver = lambda_driver()
    else:
        driver = normal_driver()

    nyt_url = "https://www.nytimes.com/topic/subject/mergers-acquisitions-and-divestitures"
    driver.get(nyt_url)
    nyt_news_raw = driver.find_elements(By.XPATH, '//*[@id="collection-Mergers, Acquisitions and Divestitures"]/div[1]/div')[0].text.split('\n')

    index_list = []
    date_list = []
    for count, text in enumerate(nyt_news_raw):
        try:
            a_date = datetime.strptime(text, "%b. %d, %Y").date()
            date_list.append(a_date)
            index_list.append(count -2)
        except:
            pass
    
    title_list = [nyt_news_raw[i] for i in index_list]
    nyt_ma_news_dict = dict(zip(title_list, date_list))
    nyt_ma_news_dict = {title: str(date) for title, date in nyt_ma_news_dict.items() if date >= date_range_low}

    return nyt_ma_news_dict

def scrape_middlemkt_news(event, context):

    date_range_low = datetime.today().date() - timedelta(days=7)
    
    if context:
        driver = lambda_driver()
    else:
        driver = normal_driver()

    ma_news_url = 'https://www.themiddlemarket.com/latest-news'
    driver.get(ma_news_url)

    latest_news = driver.find_elements(By.XPATH,"/html/body/main/div/div/div/div[1]/div/div")
    latest_news = latest_news[0].text.split('\n')    

    ma_article_list = [i for count, i in enumerate(latest_news) if count%2 == 0 ] 
    ma_date_list = [i for count, i in enumerate(latest_news) if count%2 != 0 ] 

    theMiddleMarket_news_dict =  dict(zip(ma_article_list, ma_date_list))
    theMiddleMarket_news_dict = {key: datetime.strptime(value.title(), '%B %d, %Y').date() for key, value in theMiddleMarket_news_dict.items()}
    theMiddleMarket_news_dict = {title: str(date) for title, date in theMiddleMarket_news_dict.items() if date >= date_range_low}

    return theMiddleMarket_news_dict
