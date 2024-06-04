

# get player data per match
link = links_df.iloc[0].tolist()[0]

match_link = "https://all.rugby" + link
print("\n", match_link)

match_html_text = requests.get(match_link, headers={
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
}).text

# date, time, venue
match_soup = BeautifulSoup(match_html_text)
match_meta = match_soup.find("div", class_="txtcenter").text
match_meta_str = match_meta.replace("\t", "").replace("\n", " ")
print(match_meta_str)

dfs = pd.read_html(match_html_text)
print(f"Number of dataframes: {len(dfs)}")


# get player data
match_events = dfs[0]
home_players = match_events['Players'].tolist()
home_starters = home_players[:15]
home_players = [i.lower().replace(' ', '-') for i in home_starters]

away_players = match_events['Players.1'].tolist()
away_starters = away_players[:15]
away_players = [i.lower().replace(' ', '-') for i in away_starters]


# for p in home_players:

player_url = "https://all.rugby/player/paolo-buonfiglio"
player_url = "https://all.rugby/player/jacob-stockdale"
player_url = "https://all.rugby/player/steven-kitshoff"


player_html_text = requests.get(player_url, headers={
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
}).text

dfs = pd.read_html(player_html_text)
print(f"Number of dataframes: {len(dfs)}")

player_overall = dfs[0]
p_columns = player_overall.columns.tolist()
p_columns = [i[0] for i in p_columns]
player_overall.columns = p_columns
player_overall = player_overall[player_overall['Season'].isna()]

