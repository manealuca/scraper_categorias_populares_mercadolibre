import argparse
import logging
import datetime
import csv
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError
logging.basicConfig(level=logging.INFO)
from common import config
import shop_pages_objects as shop
import re

logger = logging.getLogger(__name__)
is_well_formed_link=re.compile(r'^https?://.+/.+$')
is_root_path = re.compile(r'^/.+$')

def _shop_scraper(shop_site_uid):
    host = config()['shop_sites'][shop_site_uid]['url']

    logging.info('Beginning scrape for {}'.format(host))
    homepage = shop.HomePage(shop_site_uid,host)
    
    articles=[]
    for link in homepage.categorias_links:
        article=_fetch_article(shop_site_uid,host,link)
        if article:
            logger.info('Article fetched!')
            articles.append(article)    

    _save_articles(shop_site_uid,articles)
    


def _save_articles(shop_site_uid,articles):
    now = datetime.datetime.now().strftime('%y_%m_%d')
    out_file_name ='{shop_site_uid}_{datetime}_articles.csv'.format(shop_site_uid=shop_site_uid,
                                                                datetime=now)
    csv_headers = list(filter(lambda property: not property.startswith('_'),dir(articles[0])))
    with open(out_file_name,mode='w+') as f:
        writer=csv.writer(f)
        writer.writerow(csv_headers)
        
        for article in articles:
            row = [str(getattr(article,prop))for prop in csv_headers]
            writer.writerow(row)
            
def _fetch_article(shop_site_uid,host,link):
    logger.info('start fetching article at {}'.format(link))
    
    article = None
    try:
        article = shop.ArticlePage(shop_site_uid, _build_link(host,link))
    except(HTTPError, MaxRetryError) as e:
        logger.warning('Error while fetching the article',exc_info=False)
        
    if article and not article.article_url:
        logger.warning('Invalid article. There is no artcle url')
        return None
    
    return article


def _build_link(host,link):
    if is_well_formed_link.match(link):
        return link
    elif is_root_path.match(link):
        return '{}{}'.format(host,link)
    else:
        return '{host}/{uri}'.format(host=host,uri=link)


if __name__=='__main__':
    parser = argparse.ArgumentParser()

    shop_site_choices= list(config()['shop_sites'].keys())
    parser.add_argument('shop_site',
                        type= str,
                        choices=shop_site_choices,
                        help='the shop site tha you whant to scrape')

    args = parser.parse_args()
    _shop_scraper(args.shop_site)

