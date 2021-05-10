# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


from pyquery import PyQuery
from pyparsing import *
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
}

"""
获取所有章节链接
"""
index_url = "http://www.xbiquge.la/15/15021/"
response = requests.get(index_url, headers=headers)
print(response.text)
href = Combine(Word("< a href=""/")+Word(nums)+"/"+Word(nums)+"/" + Word(nums) + Word(".html"">"))
hrefTokens = href.searchString(response.text)
for href in hrefTokens[1:]:
    url="http://www.xbiquge.la" + href[0]
    print(url)