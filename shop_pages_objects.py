
import bs4
import requests
from common import config

class ShopPage:
    def __init__(self,shop_site_uid,url):
        self._config=config()['shop_sites'][shop_site_uid]
        self._queries = self._config['queries']        
        self._html = None
    
        self._visit(url)


    def _select(self,query_string):
        return self._html.select(query_string)
    
        
    def _visit(self,url):
        response = requests.get(url)
        response.raise_for_status()
        self._html = bs4.BeautifulSoup(response.text,'html.parser')
    

class HomePage(ShopPage):
    def __init__(self,shop_site_uid,url):
       super().__init__(shop_site_uid,url)
        
    @property
    def categorias_links(self):
        link_list=[]
        for link in self._select(self._queries['homepage_categorias_links']):
            if link and link.has_attr('href'):
                link_list.append(link)
        
        return set(link['href']for link in link_list)




class ArticlePage(ShopPage):
    def __init__(self,shop_site_uid,url):
        super().__init__(shop_site_uid,url)
            
    @property
    def article_url(self):
        result = self._select(self._queries['article_url'])    
        return result[0].text if len(result) else '' 
    
    
    @property
    def article_title(self):
        result = self._select(self._queries['article_title'])    
        return result[0].text if len(result) else ''        
        
