
import re
import time
import datetime

import requests
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from selectolax.parser import HTMLParser
import pandas as pd
from urllib.parse import urlencode

proxy_params = {
      'api_key': 'f56c714b-73ee-4d18-87c9-5048eb4d7e70',
      'url': 'https://www.amazon.in/product-reviews/B09N3ZNHTY/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=positive&reviewerType=all_reviews&pageNumber=9#reviews-filter-bar',
  }
url = urlencode(proxy_params)
print(url)
# response = requests.get(
#   url='https://proxy.scrapeops.io/v1/',
#   params=urlencode(proxy_params),
#   timeout=120,
# )
# # print(response.text)
# Construct the full URL
full_url = 'https://proxy.scrapeops.io/v1/?' + url

# Make the request
response = requests.get(
    url=full_url,
    timeout=120,
)
print(full_url)
# Do something with the response...
# print(response.text)