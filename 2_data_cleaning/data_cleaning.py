# import libraries
import pandas as pd
from os import listdir
from os.path import isfile, join


data_path = "0_data/match_data"
data_files = [f for f in listdir(data_path) if isfile(join(data_path, f))]

dfs = []
for data_file in data_files:
    temp = pd.read_csv(f"{data_path}/{data_file}")
    comp = data_file.split('_')[0]

    temp['competition'] = comp
    dfs.append(temp)

df = pd.concat(dfs)


df['round_stage'] = df['meta'].apply(lambda x: x.split('Round : ')[1])
df['round_stage'] = df['round_stage'].apply(lambda x: x.split('  All times shown are french')[0])


# remove french division 2 teams
# df = df.loc[~df['Home team'].isin(['Grenoble', 'Mont-de-Marsan'])]

# rename teams mispelled
df['Home team'].replace({'Edimbourg': 'Edinburgh',
                         'Trévise': 'Benetton'}, inplace=True)

df['Away team'].replace({'Edimbourg': 'Edinburgh',
                         'Trévise': 'Benetton'}, inplace=True)

# make all teams upper case
df['Home team'] = df['Home team'].str.upper()
df['Away team'] = df['Away team'].str.upper()



# parse match date
df['match_date'] = [i.split(' Kick Off :')[0] for i in df['meta'].tolist()]
df['match_date'] = [i.split(':  ')[1] for i in df['match_date'].tolist()]

df['match_day'] = [i.split(',')[0] for i in df['match_date'].tolist()]
df['match_date'] = [' '.join(i.split(', ')[1:]) for i in df['match_date'].tolist()]
df['match_month'] = [i.split(' ')[0] for i in df['match_date'].tolist()]

# match time
# df['match_time'] = [i.split(' Kick Off : ')[1] for i in df['meta'].tolist()]
# df['match_time'] = [i.split(' Venue')[0] for i in df['match_time'].tolist()]

# df['match_date_time'] = df['match_date'] + ' ' + df['match_time']
# df['match_date_time'] = pd.to_datetime(df['match_date_time'])

# resetting index to match date
df['match_date_'] = pd.to_datetime(df['match_date'])
# create a primary key using home team, away team and date
df['pkey'] = df['Home team'] + '_' + df['Away team'] + '_' + df['match_date_'].astype(str)
df.index = df['match_date_']
df.sort_index(inplace=True)


# parse match result
df = df.loc[df['match_result']!='cancelled']
match_results = [i.split(' - ') for i in df['match_result'].tolist()]


df['home_score'] = [int(i[0]) if ':' not in i[0] else -1 for i in match_results ]
df['away_score'] = [int(i[1]) if len(i) == 2 else -1 for i in match_results]
df['score_diff'] = df['home_score'] - df['away_score']

# pack weight
df['home_pack_weight'] = [int(i.split(' kg')[0]) if type(i)==str else -1 for i in df['Home Pack weight (average)'].tolist()]
df['away_pack_weight'] = [int(i.split(' kg')[0]) if type(i)==str else -1 for i in df['Away Pack weight (average)'].tolist()]

# player ages
df['home_forwards_ages'] = [int(i.split(' ')[0]) if type(i)==str else -1 for i in df['Home Forwards average age'].tolist()]
df['home_backs_ages'] = [int(i.split(' ')[0]) if type(i)==str else -1 for i in df['Home Backs average age'].tolist()]
df['away_forwards_ages'] = [int(i.split(' ')[0]) if type(i)==str else -1 for i in df['Away Forwards average age'].tolist()]
df['away_backs_ages'] = [int(i.split(' ')[0]) if type(i)==str else -1 for i in df['Away Backs average age'].tolist()]



df.drop(columns=['match_result', 
                 'Home JIFF players  ( read JIFF study in Top 14 )', 
                 'Away JIFF players  ( read JIFF study in Top 14 )', 
                 'Home Pack weight (average)', 'Home Forwards average age',
                'Home Backs average age', 'Home Tallest player',
                'Home Differents nationalities for starters',
                'Home Differents nationalities for all the team',
                'Away Pack weight (average)', 'Away Forwards average age',
                'Away Backs average age', 'Away Tallest player',
                'Away Differents nationalities for starters',
                'Away Differents nationalities for all the team',
                'meta', 'match_date_', 'match_month', 'match_day', 'match_date'],
        inplace=True)

df.to_csv(f"{data_path}/cleaned_match_data.csv", index=True)

