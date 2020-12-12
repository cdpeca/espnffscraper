import requests
#%matplotlib inline
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import json
from espn_api.football import League
from espn_api.football import Matchup

#from iPython.display import HTML

league_id = 8300157
year = 2020
swid = "{2B58A570-7F1A-4E00-8A28-BB8722A843BF}" #SWID COOKIE
espn_s2 = "AECKzk8JH%2BOWbkdA4%2FYwyJbd4c8%2F4qgLqfpkWpcTHPYSOKz4dYdN%2Bu0m3%2BghPGqOMmKK59l%2FRPrfp%2Bk9QPOANaeYzO2nWn%2B1cZDxW7h5EQrUsVrUsJx947DKRiXb01%2BBrl3jYcHYA444QUtg%2B%2BRvIeH9mGv2GllxQoTtyuEzC1KGAnK%2Bo%2BrEYXeIB%2B3s%2F8o7MmqmZ5FEhln8YBXmv2hhi8YbUGpsKdxvF9VI5WiIVPnH4ijF80NpM8wqUnG5m35sjGAm2GTnmG4ftrvi6b0C5NlN" #LONG ESPN S2 COOKIE


if year == 2020:
    league_summary_url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/" + \
        str(year) + \
        "/segments/0/leagues/" + \
        str(league_id)
    league_matchup_url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/" + \
        str(year) + \
        "/segments/0/leagues/" + \
        str(league_id) + \
        "?view=mTeam&view=mRoster&view=mMatchup&view=mSettings"
else:
    league_summary_url = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/" + \
        str(league_id) + \
        "?seasonId=" + \
        str(year)
    league_matchup_url = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/" + \
        str(league_id) + \
        "?seasonId=" + \
        str(year) + \
        "view=mMatchup"

# If league is viewable to public just call the API 
#r = requests.get(url)
# If league is not viewable to public need to call the API with some stored session cookies
#r = requests.get(league_summary_url, cookies={"swid":swid, "espn_s2":espn_s2})
r = requests.get(league_matchup_url, cookies={"swid":swid, "espn_s2":espn_s2})
d = r.json()
#d = r.json()[0] #historical leagues reutrn a JSON in a list of length one, i.e. [0]
#with open('apidump.json', 'w') as json_file:
#    json.dump(d, json_file)

## 'http://fantasy.espn.com/apis/v3/games/ffl/seasons/2019/segments/0/leagues/89417258?view=mDraftDetail&view=mLiveScoring&view=mMatchupScore&view=mPendingTransactions&view=mPositionalRatings&view=mSettings&view=mTeam&view=modular&view=mNav&view=mMatchupScore'

# Win / Loss Margins

df = []
for game in d['schedule']:
    if 'away' in game:
        df.append([game['matchupPeriodId'],
                    game['home']['teamId'], game['home']['totalPoints'],
                    game['away']['teamId'], game['away']['totalPoints']])
    else:
        df.append([game['matchupPeriodId'],
                    game['home']['teamId'], game['home']['totalPoints'],
                    "BYE", "BYE"])
df = pd.DataFrame(df, columns=['Week', 'Home', 'Score', 'Away', 'Score'])
df['Type'] = ['Regular' if w<=13 else 'Playoff' for w in df2['Week']]
print(f"\n{df2}")




# espn-api module

# public league
#league = League(league_id=1245, year=2018)
# private league with cookies
league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
# private league with username and password
#league = League(league_id=1245, year=2018, username='userName', password='pass')
# debug mode
#league = League(league_id=1245, year=2018, debug=True)

matchups =[Matchup(matchup) for matchup in d['schedule']]


print(f"\nLeague Standings ==> {league.standings()}\n")
print(f"League Top PF ==> {league.top_scorer()}\n")
print(f"League Least PF ==> {league.least_scorer()}\n")
print(f"League Top PA ==> {league.most_points_against()}\n")
print(f"League Top Scored Week ==> {league.top_scored_week()}\n")
print(f"League Least Scored Week ==> {league.least_scored_week()}\n")
print(f"League Box Scores ==> {league.box_scores(1)}\n")
print(f"League Scoreboard ==> {league.scoreboard(1)}\n")
#print(f"Leage Power Rankings ==> {league.power_rankings()}")

#print(f"league_summary_url={league_summary_url}")
#print(f"league_matchup_url={league_matchup_url}")
#print(f"text={r.text}")
#print(f"json={d}")
print(f"")
