
import pandas as pd
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np
import warnings
warnings.filterwarnings('ignore')



url = "https://www.oddsportal.com/rugby-union/world/united-rugby-championship/results/"

match_html_text = requests.get(url, headers={
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
        AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
}).text



dfs = pd.read_html(match_html_text)
print(f"Number of dataframes: {len(dfs)}")
