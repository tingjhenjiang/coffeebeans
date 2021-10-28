# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from lxml import etree
import requests
import pandas as pd
import tensorflow as tf
import urllib,dask,re,os,time,io,copy
from dask.diagnostics import ProgressBar
#import ckipnlp
from ckipnlp.pipeline import CkipPipeline, CkipDocument

destSaveCSVfile = "TGC_website_goods.csv"
gpu_num_workers = 3

# %% [markdown]
# # 蒐集資料及預處理資料

# %%
def strtrimandjoin(x):
  x = map(lambda x: x.strip(), x)
  return "".join(x)

def get_good_data_links(catgurl):
  catg, catgurl = catgurl
  goods_data_raw = requests.get(catgurl)
  goods_data_raw.encoding = 'UTF-8'
  goods_data_raw = goods_data_raw.text
  goods_data_etree = etree.HTML(goods_data_raw)
  goods_links = ['https://www.tgc-coffee.com'+x.get("href") for x in goods_data_etree.xpath("//ul[contains(@class,'boxify-container')]/li/a")]
  return catg, goods_links

def get_good_data_dict(goodurl):
  catg, goodurl = goodurl
  good_data_raw = requests.get(goodurl)
  good_data_raw.encoding = 'UTF-8'
  good_data_raw = good_data_raw.text
  good_data_etree = etree.HTML(good_data_raw)
  good_title = strtrimandjoin(good_data_etree.xpath("//div[contains(@class,'title')]/h1/text()") )
  good_title = good_title.replace("【TGC】","").replace("[TGC ]","").replace("[TGC]","").strip()
  good_summary = strtrimandjoin(good_data_etree.xpath("//p[contains(@class,'product-summary')]/text()") )
  good_description = strtrimandjoin(good_data_etree.xpath("//div[contains(@class,'description-container')]//text()") )
  good_price = good_data_etree.xpath("//div[contains(@class,'same-price')]//text()") # or contains(@class,'messagetobuy')]
  good_price = [gp.strip() for gp in good_price]
  good_price = [gp for gp in good_price if gp!='']
  try:
    #print("select last element from {}".format(good_price))
    good_price = good_price[-1]
  except Exception as e:
    #print("error in selecting last element at {} for {} and price is {}".format(goodurl, e, good_price))
    good_price = good_price
  try:
    good_price = int(good_price.replace("NT$","").replace(",",""))
  except Exception as e:
    #print("error at str to int {} for {} and price is {}".format(goodurl, e, good_price))
    good_price = None
  good_data = {
    'title':good_title,
    'category':catg,
    'summary':good_summary,
    'description':good_description,
    'price':good_price,
    'alltext':"\n".join([good_title,good_summary,good_description]),
    'url':goodurl
  }
  return good_data

pipeline = CkipPipeline()
def getwsres(srctext):
    doc = CkipDocument(raw=srctext)
    pipeline.get_ws(doc)
    returnres = []
    for line in doc.ws:
        returnres.append(line.to_text())
    return returnres

def get_tgc_website_goods_data_raw():
  toRetrieveUrls = {
      '伴手禮':'https://www.tgc-coffee.com/categories/famous-product?limit=72',
      '臺灣咖啡豆':'https://www.tgc-coffee.com/categories/%E5%92%96%E5%95%A1%E8%B1%86?limit=72',
      '台灣滴濾式':'https://www.tgc-coffee.com/categories/%E6%BF%BE%E6%8E%9B%E5%BC%8F?limit=72',
      '世界咖啡豆':'https://www.tgc-coffee.com/categories/%E5%92%96%E5%95%A1%E8%B1%86-1?limit=72',
      '世界滴濾式':'https://www.tgc-coffee.com/categories/%E6%BF%BE%E6%8E%9B%E5%BC%8F-1?limit=72',
      '即溶沖泡高山系列':'https://www.tgc-coffee.com/categories/%E9%AB%98%E5%B1%B1%E7%B3%BB%E5%88%97?limit=72',
      '即溶沖泡華山系列':'https://www.tgc-coffee.com/categories/%E8%8F%AF%E5%B1%B1%E7%B3%BB%E5%88%97?limit=72',
      '即溶沖泡白咖啡系列':'https://www.tgc-coffee.com/categories/%E7%99%BD%E5%92%96%E5%95%A1%E7%B3%BB%E5%88%97?limit=72',
      '即溶沖泡醇黑系列':'https://www.tgc-coffee.com/categories/%E9%86%87%E9%BB%91%E7%B3%BB%E5%88%97?limit=72',
      '即溶沖泡麥片、奶茶系列':'https://www.tgc-coffee.com/categories/%E9%BA%A5%E7%89%87%E3%80%81%E5%A5%B6%E8%8C%B6?limit=72',
      '樂活養生系列':'https://www.tgc-coffee.com/categories/%E6%A8%82%E6%B4%BB%E9%A4%8A%E7%94%9F%E7%B3%BB%E5%88%97?limit=72',
      '咖啡周邊商品':'https://www.tgc-coffee.com/categories/coffee-equipment?limit=72'
  }

  tgc_website_goods_data_raw = [dask.delayed(get_good_data_links)([goodcatg,toRetrieveUrl]) for goodcatg,toRetrieveUrl in toRetrieveUrls.items()]
  tgc_website_goods_data_raw = dask.compute(*tgc_website_goods_data_raw)
  tgc_website_goods_data_raw = [(catg,url) for catg,urls_in_a_catg in tgc_website_goods_data_raw for url in urls_in_a_catg]
  tgc_website_goods_data_raw = [dask.delayed(get_good_data_dict)(gd) for gd in tgc_website_goods_data_raw]
  tgc_website_goods_data_raw = dask.compute(*tgc_website_goods_data_raw, num_workers=1, scheduler='threads')
  tgc_website_goods_data_raw = pd.DataFrame.from_records(tgc_website_goods_data_raw)
  return tgc_website_goods_data_raw


def get_tgc_website_goods_data_wseg(tgc_website_goods_data_raw):
  wsed_description = [dask.delayed(getwsres)(singletext) for singletext in tgc_website_goods_data_raw['alltext']]
  wsed_description = dask.compute(*wsed_description, num_workers=gpu_num_workers, scheduler='threads')
  copied_wsed_description = copy.deepcopy(wsed_description)
  tgc_website_goods_data_raw['alltextseg'] = pd.Series(map(lambda x: " ".join(x).replace("\u3000"," "), copied_wsed_description) )
  tgc_website_goods_data_raw_save = tgc_website_goods_data_raw.reset_index(drop=True)
  return tgc_website_goods_data_raw_save