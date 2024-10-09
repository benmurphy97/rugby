
import pandas as pd
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# create url for specified league and year
league = 'top-14'
year = 2025

if league in ['urc', 'premiership', 'top-14', 'champions-cup']:
    if year < 2025:
        url = f"https://all.rugby/tournament/{league}-{str(year)}/fixtures-results"
    elif year == 2025:
        url = f"https://all.rugby/tournament/{league}/fixtures-results"
    print(url)
else: 
    print("league not recognised")


def get_links_df(url):

    # text of fixtures page
    fixture_text = requests.get(url, headers={ "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"})
    fixture_soup = BeautifulSoup(fixture_text.text)
    li = fixture_soup.find_all("li", class_="clearfix")

    fixture_links = [] # list of links to each fixture
    scores = [] # scores of matches

    # iterate over fixture li elements, getting url and score for match
    for i in li:
        scores.append(i.text.split("\n")[3])
        fix_link = i.find("a")['href']
        fixture_links.append(fix_link)
        
    # create df with all fixture links in it
    links_df = pd.DataFrame(fixture_links,columns=['links'])

    return links_df, scores

links_df, scores = get_links_df(url)

# list to store data from each fixture
list_of_match_dataframes = []
list_of_player_dataframes = []

# loop over links and get match data
for link in links_df['links']:
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


    # the number of dfs is determined on what we know about the match
    # games that have been played already have either 3 or 4 dfs
    # games that are in the upcoming days when we know the team news have 9 dfs
    # games further in the future have 5/6/7 dfs


    # fixture, we dont know team news - just grab meta and home + away team
    if len(dfs) in [5,6,7]:

        home_team = dfs[0].columns[0]
        away_team = dfs[0].columns[2]
        match_df = pd.DataFrame([{"Home team": home_team,
                                "Away team": away_team}])

        match_df['meta'] = match_meta_str

        list_of_match_dataframes.append(match_df)

    # matches called off by covid, ignore
    if 'Coronavirus' in match_meta_str:
        continue

    if 'blessures' in match_meta_str:
        continue

    
    # if the match is a past result
    elif len(dfs) < 5:
        # pack weight and age
        meta_df = dfs[1]

        home_team = meta_df.columns[0]
        away_team = meta_df.columns[2]

        cols = meta_df['VS'].tolist()
        cols.append('team')
        data = meta_df[[home_team, away_team]].T

        data['team'] = data.index
        data.columns = cols

        data_home = data.head(1)
        data_away = data.tail(1)

        data_home = data_home.add_prefix("Home ").reset_index(drop=True)
        data_away = data_away.add_prefix("Away ").reset_index(drop=True)

        match_df = pd.concat([data_home, data_away], axis=1)
        match_df['meta'] = match_meta_str

        # Players in match with events and substitutions 
        # dfs[0]

        match_events = dfs[0]

        # n_tries
        home_tries = ' '.join(match_events['Try'].iloc[:23].dropna().values).split('\'')
        minutes_of_home_tries = [str(int(i)) for i in home_tries if len(i)>0]
        home_n_tries = len(minutes_of_home_tries)

        away_tries = ' '.join(match_events['Try.1'].iloc[:23].dropna().values).split('\'')
        minutes_of_away_tries = [str(int(i)) for i in away_tries if len(i)>0]
        away_n_tries = len(minutes_of_away_tries)

        # n_penalties
        home_pen_kicks = ' '.join(match_events['Penalty'].iloc[:23].dropna().values).split('\'')
        minutes_of_home_pen_kicks = [str(int(i)) for i in home_pen_kicks if len(i)>0]
        home_n_pen_kicks = len(minutes_of_home_pen_kicks)

        away_pen_kicks = ' '.join(match_events['Penalty.1'].iloc[:23].dropna().values).split('\'')
        minutes_of_away_pen_kicks = [str(int(i)) for i in away_pen_kicks if len(i)>0]
        away_n_pen_kicks = len(minutes_of_away_pen_kicks)

        # n_conversions
        home_conversions = ' '.join(match_events['Conversion'].iloc[:23].dropna().values).split('\'')
        minutes_of_home_conversions = [str(int(i)) for i in home_conversions if len(i)>0]
        home_n_conversions = len(minutes_of_home_conversions)

        away_conversions = ' '.join(match_events['Conversion.1'].iloc[:23].dropna().values).split('\'')
        minutes_of_away_conversions = [str(int(i)) for i in away_conversions if len(i)>0]
        away_n_conversions = len(minutes_of_away_conversions)
        
        match_df['home_n_tries'] = home_n_tries
        match_df['minutes_of_home_tries'] = '_'.join(minutes_of_home_tries)
        match_df['away_n_tries'] = away_n_tries
        match_df['minutes_of_away_tries'] = '_'.join(minutes_of_away_tries)

        match_df['home_n_pen_kicks'] = home_n_pen_kicks
        match_df['minutes_of_home_pen_kicks'] = '_'.join(minutes_of_home_pen_kicks)
        match_df['away_n_pen_kicks'] = away_n_pen_kicks
        match_df['minutes_of_away_pen_kicks'] = '_'.join(minutes_of_away_pen_kicks)

        match_df['home_n_conversions'] = home_n_conversions
        match_df['minutes_of_home_conversions'] = '_'.join(minutes_of_home_conversions)
        match_df['away_n_conversions'] = away_n_conversions
        match_df['minutes_of_away_conversions'] = '_'.join(minutes_of_away_conversions)

        list_of_match_dataframes.append(match_df)

        # players in match
        # player_df = pd.DataFrame()
        # home_starters = match_events['Players'].iloc[:15].to_list()
        # home_player_df = pd.DataFrame({"player": home_starters,
        #                               "location": ['home' for i in range(len(home_starters))]})

        # away_starters = match_events['Players.1'].iloc[:15].to_list()
        # away_player_df = pd.DataFrame({"player": away_starters,
        #                               "location": ['away' for i in range(len(away_starters))]})
        
        # player_df = pd.concat([home_player_df, away_player_df])
        # player_df['meta'] = match_meta_str
        # list_of_player_dataframes.append(player_df)


    # matches that havent happened yet but we know team news
    elif len(dfs) == 9:
        # pack weight and age
        meta_df = dfs[2]

        home_team = meta_df.columns[0]
        away_team = meta_df.columns[2]

        cols = meta_df['VS'].tolist()
        cols.append('team')
        data = meta_df[[home_team, away_team]].T

        data['team'] = data.index
        data.columns = cols

        data_home = data.head(1)
        data_away = data.tail(1)

        data_home = data_home.add_prefix("Home ").reset_index(drop=True)
        data_away = data_away.add_prefix("Away ").reset_index(drop=True)

        match_df = pd.concat([data_home, data_away], axis=1)
        match_df['meta'] = match_meta_str

        list_of_match_dataframes.append(match_df)

scores = [i for i in scores if i != 'cancelled']
df = pd.concat(list_of_match_dataframes)
df['match_result'] = scores

out_path = f"0_data/match_data/{league}_{year}.csv"

df.to_csv(out_path, index=False)

