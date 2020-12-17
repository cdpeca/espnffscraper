import pandas as pd
import numpy as np
import seaborn as sns
#import requests
import json
import os
#import mplcairo # on macOS this module must be explicitly be imported before importing matplotlib
import matplotlib
#matplotlib.use("module://mplcairo.macosx")
import matplotlib.pyplot as plt
from constants.priv_constants import swid, espn_s2, league_id
#from espn_api.football import League
from pathlib import Path
#from base_league import BaseLeague
#from requests.espn_requests import EspnFantasyRequests
from request.espn_requests import EspnFantasyRequests
from utils.logger import Logger
from base_settings import BaseSettings
from constant import POSITION_MAP, ACTIVITY_MAP
import sys


year = 2020
league_open_to_public = False
league_id = league_id
swid = swid
espn_s2 = espn_s2
cookies = None
sport='nfl'
debug=False


for i in range(len(sys.argv)):
    if sys.argv[i] == '--debug':
        debug = True


logger = Logger(name=f'{sport} league for espnffscraper', debug=debug)


if espn_s2 and swid:
    cookies = {
        'espn_s2': espn_s2,
        'SWID': swid
    }


espn_request = EspnFantasyRequests(sport=sport, year=year, league_id=league_id, cookies=cookies, logger=logger)
d = espn_request.get_league()

SettingsClass = BaseSettings
currentMatchupPeriod = d['status']['currentMatchupPeriod']
scoringPeriodId = d['scoringPeriodId']
firstScoringPeriod = d['status']['firstScoringPeriod']
if year < 2018:
    current_week = d['scoringPeriodId']
else:
    current_week = scoringPeriodId if scoringPeriodId <=  d['status']['finalScoringPeriod'] else d['status']['finalScoringPeriod']
settings = SettingsClass(d['settings'])

nfl_week = d['status']['latestScoringPeriod']




def construct_url():
#    """Construct a url based on year of league"""
    
    '''
    ESPN has completely different API enpoints for leagues in current year vs. historical leages
    Depending on the year being scraped need to construct the correct API endpoint
    '''

    if year == 2020:
        league_matchup_url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/" + \
            str(year) + \
            "/segments/0/leagues/" + \
            str(league_id) + \
            "?view=mTeam&view=mRoster&view=mMatchup&view=mSettings"
    else:

        league_matchup_url = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/" + \
            str(league_id) + \
            "?seasonId=" + \
            str(year) + \
            "?view=mTeam&view=mRoster&view=mMatchup&view=mSettings"
    #print(f"league_matchup_url ==> {league_matchup_url}")
    return league_matchup_url




def fetch_league_data():
    """Make a call to ESPN API using url and necessary parameters, load JSON response into a local data structure"""

    '''
    Public vs. Private Leagues

    If league is viewable to public can just call the API 
    If league is not viewable to public need to call the API with some stored session cookies
    for now these need to be stored/input in ./constants/priv_constants.py
        league_id
        swid
        espn_s2
    '''
    
    if league_open_to_public:
        r = requests.get(url)
    else:
        r = requests.get(url, cookies={"swid":swid, "espn_s2":espn_s2})


    '''
    Locally store the returned json data

    For leagues in the current year a regular JSON structure is returned
    For historical leagues the JSON structure is returned in a list of length one, i.e. [0]
    '''

    if year > 2017:
        d = r.json()
    else:
        d = r.json()[0] 

    #with open('apidump.json', 'w') as json_file:
    #    json.dump(d, json_file)

    return d



def create_team_dataframe():
    """Fetch all of the teams in the league and construct the team name"""

    '''
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
    #print(f"\n === df_team DataFrame [{len(df_team)} rows x {len(df_team.columns)} columns] ==== \n{df_team}\n")
    if logger:
        logger.log_dataframe(df_team, 'df_team')
    
    
    return df_team


def determine_win_loss_margins():
    """Generate a chart showing margins of wins and losses for each team in league, broken out by regular and playoff seasons"""

    df_matchup = []
    for game in d['schedule']:
        if 'away' in game and game['matchupPeriodId'] < (currentMatchupPeriod + 1):
            df_matchup.append([game['matchupPeriodId'],
                        game['home']['teamId'], game['home']['totalPoints'],
                        game['away']['teamId'], game['away']['totalPoints']])
        elif 'home' in game and game['matchupPeriodId'] < (currentMatchupPeriod + 1):
            df_matchup.append([game['matchupPeriodId'],
                        game['home']['teamId'], game['home']['totalPoints'],
                        'BYE', 0])
    df_matchup = pd.DataFrame(df_matchup, columns=['Week', 'homeID', 'homeScore', 'awayID', 'awayScore'])
    df_matchup['Type'] = ['Regular' if w<=13 else 'Playoff' for w in df_matchup['Week']]
    #print(f"\n === df_matchup DataFrame [{len(df_matchup)} rows x {len(df_matchup.columns)} columns] === \n{df_matchup.head()}")
    if logger:
        logger.log_dataframe(df_matchup, 'df_matchup')

    '''
        Get the Team Names added
        mMatchup API returns IDs for teams, and it separates them as Home and Away, so the keys aren't the same and not indexed
        Have to bring them in separately for both Home and Away teams
    '''

    df_matchup_merge = pd.merge(df_team, df_matchup, how='outer', on=None, left_on='teamID', right_on='homeID', left_index=False, right_index=False, sort=False)
    df_matchup_merge.rename(columns={'teamName':'homeTeam'}, inplace=True)
    df_matchup_merge['homeTeam'].fillna(value='BYE', inplace=True)
    #print(f"\n === df_matchup_merge DataFrame [{len(df_matchup_merge)} rows x {len(df_matchup_merge.columns)} columns] === \n{df_matchup_merge.head()}")

    df_matchup_merge = pd.merge(df_team, df_matchup_merge, how='outer', on=None, left_on='teamID', right_on='awayID', left_index=False, right_index=False, sort=False)
    df_matchup_merge.rename(columns={'teamName':'awayTeam'}, inplace=True)
    df_matchup_merge['awayTeam'].fillna(value='BYE', inplace=True)
    
    #print(f"\n === df_matchup_merge DataFrame [{len(df_matchup_merge)} rows x {len(df_matchup_merge.columns)} columns] === \n{df_matchup_merge.head()}")
    if logger:
        logger.log_dataframe(df_matchup_merge, 'df_matchup_merge')
    
    # Create dataframe to stage data for this plot
    df_winlossmargin = df_matchup_merge.assign(Margin1 = df_matchup_merge['homeScore'] - df_matchup_merge['awayScore'],
                                                Margin2 = df_matchup_merge['awayScore'] - df_matchup_merge['homeScore'])
    df_winlossmargin = (df_winlossmargin[['Week', 'homeTeam', 'Margin1', 'Type']]
        .rename(columns={'homeTeam': 'Team', 'Margin1': 'Margin'})
        .append(df_winlossmargin[['Week', 'awayTeam', 'Margin2', 'Type']]
        .rename(columns={'awayTeam': 'Team', 'Margin2': 'Margin'})))
    index_names = df_winlossmargin[df_winlossmargin['Team'] == 'BYE' ].index
    df_winlossmargin.drop(index_names, inplace=True)
    #print(f"\n === df_winlossmargin DataFrame [{len(df_winlossmargin)} rows x {len(df_winlossmargin.columns)} columns] === \n{df_winlossmargin.head()}\n")
    if logger:
        logger.log_dataframe(df_winlossmargin, 'df_winlossmargin')

    # Create a boxplot for the win/loss margine separated by regular season and playoffs
    fig, ax = plt.subplots(1,1, figsize=(10,10))
    #order = [9, 4, 11, 3, 1, 10, 6, 2, 5, 12]
    sns.boxplot(x='Team', y='Margin', hue='Type',
                data=df_winlossmargin,
    #            order=order,
                palette='muted')
    ax.axhline(0, ls='--')
    ax.set_xlabel('')
    ax.set_title('Win/Loss Margins')

    #plt.show()

    return df_matchup_merge

def calculate_weekly_averages():
    """ calculate average scores per week for the league """


    df_avgs = (df_matchup_merge
        .filter(['Week', 'homeScore', 'awayScore'])
        .melt(id_vars=['Week'], value_name='Score')
        .groupby('Week')
        .mean()
        .reset_index()
    )
    #print(f"\n === df_avgs DataFrame [{len(df_avgs)} rows x {len(df_avgs.columns)} columns] === \n{df_avgs.head()}")
    if logger:
        logger.log_dataframe(df_avgs, 'df_avgs')

    return df_avgs


def determine_lucky_results(team, teamName):
    """Generate charts showing lucky/unlucky wins and losses"""


    # grab all games with this team
#    df_team_luck = df_matchup_merge.query('homeID == @team | awayID == @team').reset_index(drop=True)
    df_team_luck = df_matchup_merge.query('(homeID == @team | awayID == @team) & Week < @currentMatchupPeriod').reset_index(drop=True)

    # move the team of interest to "homeTeam" column
    ix = list(df_team_luck['awayID'] == team)
    df_team_luck.loc[ix, ['homeID','homeTeam','homeScore','awayID','awayTeam','awayScore']] = \
        df_team_luck.loc[ix, ['awayID','awayTeam','awayScore','homeID','homeTeam','homeScore']].values
    
    # add new score and wins columns
    df_team_luck = (df_team_luck
        .assign(Chg1 = df_team_luck['homeScore'] - df_avgs['Score'],
                Chg2 = df_team_luck['awayScore'] - df_avgs['Score'],
                Win = df_team_luck['homeScore'] > df_team_luck['awayScore']))

    # Replace BYE week opponent scores of 0 with the weekly average
    df_team_luck.loc[df_team_luck.awayScore == 0, 'Chg2'] = 0
    
    # Replace BYE week opponent scopes of 0 with the weekly average -- longer way of doing it
    '''
    mask = df_team_luck.awayScore == 0
    column_name = 'Chg2'
    df_team_luck.loc[mask, column_name] = 0
    '''

    df_team_luck.sort_values(by=['Week'], inplace=True, ascending=True)   
    #print(f"\n === df_team_luck DataFrame [{len(df_team_luck)} rows x {len(df_team_luck.columns)} columns] === \n{df_team_luck}")
    if logger:
        logger.log_dataframe(df_team_luck, f'df_team_luck==> {team}: {teamName}')

    # VISUALIZE now that we have average weekly scores and team lucky/unlucy data

    fig, ax = plt.subplots(1,1, figsize=(10,10))

    z = 70

    ax.fill_between([0,z], 0, [0,z], facecolor='b', alpha=0.1)
    ax.fill_between([-z,0], -z, [-z,0], facecolor='b', alpha=0.1)
    ax.fill_between([0,z], [0,z], z, facecolor='r', alpha=0.1)
    ax.fill_between([-z,0], [-z,0], 0, facecolor='r', alpha=0.1)

    ax.scatter(data=df_team_luck.query('Win and (Type == "Regular")'), x='Chg1', y='Chg2', 
        c='b', 
        s=100,
        marker='o',
        label='Win - Regular Season') 
    ax.scatter(data=df_team_luck.query('Win and (Type == "Playoff")'), x='Chg1', y='Chg2', 
        c='r', 
        s=100,
        marker='o',
        label='Win - Playoffs') 
    ax.scatter(data=df_team_luck.query('(not Win) and (Type == "Regular")'), x='Chg1', y='Chg2', 
        c='b', 
        s=100,
        marker='x',
        label='Loss - Regular Season') 
    ax.scatter(data=df_team_luck.query('(not Win) and (Type == "Playoff")'), x='Chg1', y='Chg2', 
        c='r', 
        s=100,
        marker='x',
        label='Loss - Playoffs') 
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

    ax.set(title='Team %s Scores (centered at league average)' % teamName)

    # use annotation function to assign labels (i.e. opponent team anme) to each plotted data point
    # ... ideally this could be done as the point were added to the scatter chart
    # ... may want to consider changing this to a dataframe query as iteration is expensive

    for i, row in df_team_luck.iterrows():
        if row['homeID'] == team:
            ax.annotate(row['awayTeam'],
                        (row['Chg1'], row['Chg2']),
                        textcoords="offset points", # how to position the texxt
                        xytext=(0,10), # distance from text to points (x,y)
                        ha='center') # horizontal alignment can be left, right or center
        elif row['awayID'] == team:
            ax.annotate(row['homeTeam'],
                        (row['Chg1'], row['Chg2']),
                        textcoords="offset points", # how to position the texxt
                        xytext=(0,10), # distance from text to points (x,y)
                        ha='center') # horizontal alignment can be left, right or center

    #plt.show()


#url = construct_url()

#d = fetch_league_data()

df_team = create_team_dataframe()

df_matchup_merge = determine_win_loss_margins()

df_avgs = calculate_weekly_averages()

#for i in range(1):
for i in range(len(df_team)):
    team = list(df_team.index.values.tolist())[i]
    teamName = df_team.iloc[i, 0]
    determine_lucky_results(team, teamName)

#plt.tight_layout()
plt.show()


'''
espn-api module
https://github.com/cwendt94/espn-api.git

Enable use of espn-api Python module
'''

# public league
#league = League(league_id=league_id, year=year)

# private league with cookies
#league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)

# private league with username and password
#league = League(league_id=league_id, year=year, username='userName', password='pass')

# debug mode
#league = League(league_id=league_id, year=year, debug=True)




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
