import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def scrape_middlemkt_news():

    date_range_high = datetime.today().date()
    date_range_low = datetime.today().date() - timedelta(days=7)

    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    s = Service('chromedriver/chromedriver')
    driver = webdriver.Chrome(service= s, options=options)

    ma_news_url = 'https://www.themiddlemarket.com/latest-news'
    driver.get(ma_news_url)

    latest_news = driver.find_elements(By.XPATH,"/html/body/main/div/div/div/div[1]/div/div")
    latest_news = latest_news[0].text.split('\n')    

    ma_article_list = [i for count, i in enumerate(latest_news) if count%2 == 0 ] 
    ma_date_list = [i for count, i in enumerate(latest_news) if count%2 != 0 ] 

    theMiddleMarket_news_dict =  dict(zip(ma_article_list, ma_date_list))
    theMiddleMarket_news_dict = {key: datetime.strptime(value.title(), '%B %d, %Y').date() for key, value in theMiddleMarket_news_dict.items()}
    theMiddleMarket_news_dict = {title: date for title, date in theMiddleMarket_news_dict.items() if date >= date_range_low}

    driver.close()

    elephants = pd.read_excel('elephants.xlsx')
    elephants_dict = elephants.set_index('Client').to_dict('index')

    results = {}

    for client in elephants_dict.keys():
        client_res = []
        for title, date in theMiddleMarket_news_dict.items():
            if client.lower() in title.lower():
                client_res.append(title)
        if client_res:
            results[client] = {'news': client_res, 'broker': elephants_dict[client]['Broker'], 'broker_email':elephants_dict[client]['Broker Email']}

    return results