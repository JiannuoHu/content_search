import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def scrape_nyt_news():

    date_range_low = datetime.today().date() - timedelta(days=7)

    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    s = Service('chromedriver/chromedriver')
    driver = webdriver.Chrome(service= s, options=options)

    nyt_url = "https://www.nytimes.com/topic/subject/mergers-acquisitions-and-divestitures"
    driver.get(nyt_url)
    nyt_news_raw = driver.find_elements(By.XPATH, '//*[@id="collection-Mergers, Acquisitions and Divestitures"]/div[1]/div')[0].text.split('\n')

    driver.close()

    index_list = []
    date_list = []
    for count, text in enumerate(nyt_news_raw):
        try:
            a_date = datetime.strptime(text, "%b. %d, %Y")
            date_list.append(a_date)
            index_list.append(count -2)
        except:
            pass
    
    title_list = [nyt_news_raw[i] for i in index_list]
    nyt_ma_news_dict = dict(zip(title_list, date_list))

    elephants = pd.read_excel('elephants.xlsx')
    elephants_dict = elephants.set_index('Client').to_dict('index')

    results = {}

    for client in elephants_dict.keys():
        client_res = []
        for title, date in nyt_ma_news_dict.items():
            if client.lower() in title.lower():
                client_res.append(title)
        if client_res:
            results[client] = {'news': client_res, 'broker': elephants_dict[client]['Broker'], 'broker_email':elephants_dict[client]['Broker Email']}

    return results

