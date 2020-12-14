import requests
#%matplotlib inline
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import json
from espn_api.football import League
from espn_api.football import Matchup
import os
from matplotlib import font_manager as fm, rcParams
from constants.priv_constants import swid, espn_s2, league_id

#from iPython.display import HTML


year = 2020


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

'''
teamId from schedule json key
compare that to the teams in json
the equivaten key in teams is id
within teams
    ESPN likes to use
        location for "first half of team name"
        and
        nickname for "second half of team name"
'''

df_team = []
for teams in d['teams']:
    df_team.append([teams['id'],
                teams['location'] + " " + teams['nickname']])
df_team = pd.DataFrame(df_team, columns=['teamID', 'teamName'])
df_team.set_index('teamID', inplace=True)
print(f"\n === df_team DataFrame [{len(df_team)} rows x {len(df_team.columns)} columns] ==== \n{df_team}")

df_matchup = []
for game in d['schedule']:
    if 'away' in game:
        df_matchup.append([game['matchupPeriodId'],
                    game['home']['teamId'], game['home']['totalPoints'],
                    game['away']['teamId'], game['away']['totalPoints']])
    else:
        df_matchup.append([game['matchupPeriodId'],
                    game['home']['teamId'], game['home']['totalPoints'],
                    0, 0])
df_matchup = pd.DataFrame(df_matchup, columns=['Week', 'homeID', 'homeScore', 'awayID', 'awayScore'])
df_matchup['Type'] = ['Regular' if w<=13 else 'Playoff' for w in df_matchup['Week']]
print(f"\n === df_matchup DataFrame [{len(df_matchup)} rows x {len(df_matchup.columns)} columns] === \n{df_matchup.head()}")


'''
    Get the Team Names added
    mMatchup API returns IDs for teams, and it separates them as Home and Away, so the keys aren't the same and not indexed
    Have to bring them in separately for both Home and Away teams
'''

df_matchup_merge = pd.merge(df_team, df_matchup, how='outer', on=None, left_on='teamID', right_on='homeID', left_index=False, right_index=False, sort=False)
df_matchup_merge.rename(columns={'teamName':'homeTeam'}, inplace=True)
print(f"\n === df_matchup_merge DataFrame [{len(df_matchup_merge)} rows x {len(df_matchup_merge.columns)} columns] === \n{df_matchup_merge.head()}")

df_matchup_merge = pd.merge(df_team, df_matchup_merge, how='outer', on=None, left_on='teamID', right_on='awayID', left_index=False, right_index=False, sort=False)
df_matchup_merge.rename(columns={'teamName':'awayTeam'}, inplace=True)
print(f"\n === df_matchup_merge DataFrame [{len(df_matchup_merge)} rows x {len(df_matchup_merge.columns)} columns] === \n{df_matchup_merge.head()}")


'''
Win / Loss Margins

Use matplotlib to generate a boxplot showing the win/loss margins for all teams, separated by Regular Season and Playoffs
'''


df_winlossmargin = df_matchup_merge.assign(Margin1 = df_matchup_merge['homeScore'] - df_matchup_merge['awayScore'],
                                    Margin2 = df_matchup_merge['awayScore'] - df_matchup_merge['homeScore'])
df_winlossmargin = (df_winlossmargin[['Week', 'homeTeam', 'Margin1', 'Type']]
    .rename(columns={'homeTeam': 'Team', 'Margin1': 'Margin'})
    .append(df_winlossmargin[['Week', 'awayTeam', 'Margin2', 'Type']]
    .rename(columns={'awayTeam': 'Team', 'Margin2': 'Margin'}))
)
print(f"\n === df_winlossmargin DataFrame [{len(df_winlossmargin)} rows x {len(df_winlossmargin.columns)} columns] === \n{df_winlossmargin.head()}\n")


fig, ax = plt.subplots(1,1, figsize=(16,6))
#order = [9, 4, 11, 3, 1, 10, 6, 2, 5, 12]
sns.boxplot(x='Team', y='Margin', hue='Type',
            data=df_winlossmargin,
#            order=order,
            palette='muted')
ax.axhline(0, ls='--')
ax.set_xlabel('')
ax.set_title('Win/Loss margins')

#plt.rcParams['font.family'] = 'Meslo LG M for Powerline'
# Font Name is Meslo LG M DZ Regular for Powerline.ttf
# Font Location is ~/Library/Fonts/Meslo LG M DZ Regular for Powerline.ttf
fpath = "../../../Library/Fonts/Meslo LG M DZ Regular for Powerline.ttf"
prop = fm.FontProperties(fname=fpath)
fname = os.path.split(fpath)[1]
#ax.set_title('This is a special font: {}'.format(fname), fontproperties=prop)
ax.set_title('Win/Loss Margins', fontproperties=prop)
plt.rcParams['font.serif'] = 'Meslo LG M for Powerline'
plt.rcParams['font.sans-serif'] = 'Meslo LG M for Powerline'
#plt.show()


'''
Lucky / Unlucky Wins and Losses

Let's see who had lucky/unlucky winds and losses this season

'''

# calculate average score per week
df_avgs = (df_matchup_merge
    .filter(['Week', 'homeScore', 'awayScore'])
    .melt(id_vars=['Week'], value_name='Score')
    .groupby('Week')
    .mean()
    .reset_index()
)
print(f"\n === df_avgs DataFrame [{len(df_avgs)} rows x {len(df_avgs.columns)} columns] === \n{df_avgs.head()}")


team = 9
teamName = '🖕 🖕'

# grab all games with this team
df_team_luck = df_matchup_merge.query('homeID == @team | awayID == @team').reset_index(drop=True)

# move the team of interest to "homeTeam" column
ix = list(df_team_luck['awayID'] == team)
df_team_luck.loc[ix, ['homeID','homeScore','awayID','awayScore']] = \
    df_team_luck.loc[ix, ['awayID','awayScore','homeID','homeScore']].values

# add new score and wins columns
df_team_luck = (df_team_luck
    .assign(Chg1 = df_team_luck['homeScore'] - df_avgs['Score'],
            Chg2 = df_team_luck['awayScore'] - df_avgs['Score'],
            Win = df_team_luck['homeScore'] > df_team_luck['awayScore'])
)
df_team_luck.sort_values(by=['Week'], inplace=True, ascending=True)
print(f"\n === df_team_luck DataFrame [{len(df_team_luck)} rows x {len(df_team_luck.columns)} columns] === \n{df_team_luck}")


# VISUALIZE now that we have average weekly scores and team lucky/unlucy data

fig, ax = plt.subplots(1,1, figsize=(8,8))

z = 60

ax.fill_between([0,z], 0, [0,z], facecolor='b', alpha=0.1)
ax.fill_between([-z,0], -z, [-z,0], facecolor='b', alpha=0.1)
ax.fill_between([0,z], [0,z], z, facecolor='r', alpha=0.1)
ax.fill_between([-z,0], [-z,0], 0, facecolor='r', alpha=0.1)

ax.scatter(data=df_team_luck.query('Win'), x='Chg1', y='Chg2', 
           c=['b' if t=='Regular' else 'r' for t in df_team_luck.query('Win')['Type']], 
           s=100,
           marker='o',
           label='Win')
ax.scatter(data=df_team_luck.query('not Win'), x='Chg1', y='Chg2', 
           c=['b' if t=='Regular' else 'r' for t in df_team_luck.query('not Win')['Type']], 
           s=100,
           marker='x',
           label='Loss')
ax.plot([-z,z],[-z,z], 'k--')
ax.legend()

# center x/y axes on origin
ax.spines['left'].set_position('zero')
ax.spines['right'].set_color('none')
ax.spines['bottom'].set_position('zero')
ax.spines['top'].set_color('none')
ax.yaxis.tick_left()
ax.xaxis.tick_bottom()

# remove origin ticklabels
tx = list(range(-z,z+1,10))
tx.remove(0)
ax.yaxis.set(ticks=tx, ticklabels=tx)
ax.xaxis.set(ticks=tx, ticklabels=tx)

ax.tick_params(axis='x', colors='gray')
ax.tick_params(axis='y', colors='gray')

ax.text(z-10, -12, 'Points \n  for', style='italic')
ax.text(-18, z-10, ' Points \nagainst', style='italic')
ax.text(z/2-5, z-8, 'UNLUCKY\n   LOSS', style='italic', color='red')
ax.text(z-12, z/2-5, 'LUCKY\n WIN', style='italic', color='blue')

ax.set(title='Team #%s Scores (centered at league average)' % teamName)

# use annotation function to assign labels (i.e. opponent team anme) to each plotted data point
# ... ideally this could be done as the point were added to the scatter chart
# ... may want to consider changing this to a dataframe query as iteration is expensive

for i, row in df_team_luck.iterrows():
    if row['homeTeam'] == 'teamName':
        ax.annotate(row['awayTeam'],
                    (row['Chg1'], row['Chg2']),
                    textcoords="offset points", # how to position the texxt
                    xytext=(0,10), # distance from text to points (x,y)
                    ha='center') # horizontal alignment can be left, right or center
    elif row['awayTeam'] == teamName:
        ax.annotate(row['homeTeam'],
                    (row['Chg1'], row['Chg2']),
                    textcoords="offset points", # how to position the texxt
                    xytext=(0,10), # distance from text to points (x,y)
                    ha='center') # horizontal alignment can be left, right or center


plt.show()


'''
espn-api module
https://github.com/cwendt94/espn-api.git

Enable use of espn-api Python module
'''

# public league
#league = League(league_id=1245, year=2018)
# private league with cookies
#######################league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
# private league with username and password
#league = League(league_id=1245, year=2018, username='userName', password='pass')
# debug mode
#league = League(league_id=1245, year=2018, debug=True)

########################matchups =[Matchup(matchup) for matchup in d['schedule']]

'''
Console debugging

Various output options for basic testing and debugging

'''


'''
print(f"\nLeague Standings ==> {league.standings()}\n")
print(f"League Top PF ==> {league.top_scorer()}\n")
print(f"League Least PF ==> {league.least_scorer()}\n")
print(f"League Top PA ==> {league.most_points_against()}\n")
print(f"League Top Scored Week ==> {league.top_scored_week()}\n")
print(f"League Least Scored Week ==> {league.least_scored_week()}\n")
print(f"League Box Scores ==> {league.box_scores(1)}\n")
print(f"League Scoreboard ==> {league.scoreboard(1)}\n")
print(f"Leage Power Rankings ==> {league.power_rankings()}")
'''

'''
print(f"league_summary_url={league_summary_url}")
print(f"league_matchup_url={league_matchup_url}")
print(f"text={r.text}")
print(f"json={d}")
'''
print(f"")
