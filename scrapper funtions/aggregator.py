from scrape_middlemkt import scrape_middlemkt_news
from scrape_reuters import scrape_reuters_news
from scrape_nyt import scrape_nyt_news
from scrape_wsj import scrape_wsj_news


def aggregate_news():
    
    theMiddleMarket_news_dict = scrape_middlemkt_news()
    reuters_news_dict = scrape_reuters_news()
    nyt_ma_news_dict = scrape_nyt_news()
    wsj_ma_news_dict = scrape_wsj_news()

    combined_dict = {}
    for i in [nyt_ma_news_dict, theMiddleMarket_news_dict, reuters_news_dict, wsj_ma_news_dict]:
        for k,v in i.items():
            combined_dict[k] = v

    return combined_dict

