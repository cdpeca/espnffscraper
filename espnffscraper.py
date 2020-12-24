import pandas as pd
import numpy as np
import seaborn as sns
import requests
import json
import os
#import mplcairo # on macOS this module must be explicitly be imported before importing matplotlib
import matplotlib
#matplotlib.use("module://mplcairo.macosx")
import matplotlib.pyplot as plt
from settings.settings import *
from pathlib import Path
from request.espn_requests import EspnFantasyRequests
from utils.logger import Logger
from base_settings import BaseSettings
from constant import POSITION_MAP, ACTIVITY_MAP
import sys




def fetch_league():
    """ Construct the URL for API call and fetch all league data """

    cookies = None
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
    leagueName = np.char.strip(d['settings']['name'])

    return d, logger, settings, currentMatchupPeriod, leagueName



def create_team_dataframe(d, logger):
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



def create_matchup_data(d, currentMatchupPeriod, logger, df_team):
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
    #df_matchup.drop(df_matchup[df_matchup['Week'] >= currentMatchupPeriod].index, inplace=True)
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

    df_matchup_merge = df_matchup_merge[['Week', 'Type', 'homeID', 'homeTeam', 'homeScore', 'awayID', 'awayTeam', 'awayScore']]
    df_matchup_merge.sort_values(by=['Week', 'homeID'], inplace=True)
    df_matchup_merge.reset_index(inplace=True, drop=True)

    #print(f"\n === df_matchup_merge DataFrame [{len(df_matchup_merge)} rows x {len(df_matchup_merge.columns)} columns] === \n{df_matchup_merge.head()}")
    if logger:
        logger.log_dataframe(df_matchup_merge, 'df_matchup_merge')

    return df_matchup_merge



def create_relative_record_data(df_team, df_matchup_merge, logger, currentMatchupPeriod, leagueName):
    """ Create data strucuture to store relative records by week and by season """


    if currentMatchupPeriod > 13:
        relative_range = 13
    else:
        relative_range = currentMatchupPeriod -1

    df_relative_record_home = df_matchup_merge.query('Week <= @relative_range')
    df_relative_record_home = df_relative_record_home.rename(columns = {'homeID':'team1ID','homeTeam':'team1Name','homeScore':'team1Score','awayID':'team2ID','awayTeam':'team2Name','awayScore':'team2Score'})

    df_relative_record_away = df_matchup_merge.query('Week <= @relative_range')
    df_relative_record_away = df_relative_record_away.rename(columns = {'homeID':'team2ID','homeTeam':'team2Name','homeScore':'team2Score','awayID':'team1ID','awayTeam':'team1Name','awayScore':'team1Score'})

    df_relative_record = pd.concat([df_relative_record_home, df_relative_record_away])
    df_relative_record = df_relative_record.assign(relative_wins='', relative_losses='')
    df_relative_record.sort_values(by=['Week', 'team1Score'], ascending=[True, False], inplace=True)
    df_relative_record.reset_index(inplace=True, drop=True)

    for x in range(relative_range):
        week = df_relative_record.query('Week == (@x+1)').copy()
        for i, row in week.iterrows():
            df_relative_record.loc[i,'relative_wins'] = ((x+1)*10) - (i+1)
            df_relative_record.loc[i,'relative_losses'] = 10 - ((x+1)*10) + i
        #print(f'{week}')

    #pd.set_option('display.max_rows', None)
    #pd.set_option('display.max_columns', None)
    if logger:
        logger.log_dataframe(df_relative_record, 'df_relative_record')

    df_relative_record_total = pd.DataFrame(columns=['teamID', 'teamName', 'relative_wins_total', 'relative_losses_total', 'relative_record_total'])
    for i in range(len(df_team)):
        team = list(df_team.index.values.tolist())[i]
        teamName = df_team.iloc[i, 0]
        #determine_lucky_results(team, teamName, df_matchup_merge, logger, currentMatchupPeriod, df_avgs, leagueName)
        df_relative_record_total = df_relative_record_total.append({'teamID': team,
                                                                    'teamName': teamName,
                                                                    'relative_wins_total': df_relative_record.loc[df_relative_record['team1ID'] == team, 'relative_wins'].sum(),
                                                                    'relative_losses_total': df_relative_record.loc[df_relative_record['team1ID'] == team, 'relative_losses'].sum(),
                                                                    'relative_record_total': str(f"{df_relative_record.loc[df_relative_record['team1ID'] == team, 'relative_wins'].sum()} - {df_relative_record.loc[df_relative_record['team1ID'] == team, 'relative_losses'].sum()}")
                                                                    },
                                                                    ignore_index=True
                                                                    )

    #pd.set_option('display.max_rows', None)
    #pd.set_option('display.max_columns', None)
    if logger:
        logger.log_dataframe(df_relative_record_total, 'df_relative_record_total')

    df_relative_record_total_plot = pd.DataFrame(df_relative_record_total, columns=['teamName', 'relative_record_total'])
    df_relative_record_total_plot.sort_values(by=['relative_record_total'], inplace=True, ascending=False)

    #pd.set_option('display.max_rows', None)
    #pd.set_option('display.max_columns', None)
    if logger:
        logger.log_dataframe(df_relative_record_total_plot, 'df_relative_record_total_plot')


    # Let's try and create a nice looking table in matplotlib for the relative record summary data!!
    # GREAT REFERENCE EXAMPLE FOR FORMATTING A TABLE FROM https://towardsdatascience.com/simple-little-tables-with-matplotlib-9780ef5d0bc4

    title_text = 'Overall Relative Results\n(from regular season only)'
    footer_text = f'as of Week {currentMatchupPeriod}'
    fig_background_color = 'skyblue'
    fig_border = 'steelblue'

    # Pop the headers from the dataframe
    column_headers = df_relative_record_total_plot.columns
    #row_headers = [x.pop(0) for x in df_relative_record_total]
    row_headers = df_relative_record_total_plot['teamName']

    # Table data needs to be non-numeric text. Format the data while we are at it
    cell_text = df_relative_record_total_plot.values

    # Get some lists of color specs for row and column headers
    rcolors = plt.cm.BuPu(np.full(len(row_headers), 0.1))
    ccolors = plt.cm.BuPu(np.full(len(column_headers), 0.1))

    # Create the figure. Setting a small pad on tight_layout
    # seems to better regulate white space. Sometimes experimenting
    # with an explicit figsize here can produce better outcome.
    plt.figure(linewidth=2,
            edgecolor=fig_border,
            facecolor=fig_background_color,
            tight_layout={'pad':1},
            figsize=(10,10)
            )

    # Add a table at the bottom of the axes
    the_table = plt.table(cellText=cell_text,
                        #rowLabels=row_headers,
                        #rowColours=rcolors,
                        rowLoc='right',
                        colColours=ccolors,
                        colLabels=column_headers,
                        loc='center')

    # Scaling is the only influence we have over top and bottom cell padding.
    # Make the rows taller (i.e., make cell y scale larger).
    the_table.scale(1, 2.0)
    # Hide axes
    ax = plt.gca()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # Hide axes border
    plt.box(on=None)
    # Add title
    plt.suptitle(title_text, ha='center', va='top', fontsize=20)
    # Add footer
    plt.figtext(0.95, 0.05, footer_text, horizontalalignment='right', size=6, weight='light')
    # Force the figure to update, so backends center objects correctly within the figure.
    # Without plt.draw() here, the title will center on the axes and not the figure.
    plt.draw()
    # Create image. plt.savefig ignores figure edge and face colors, so map them.
    fig = plt.gcf()


    '''
    # Basic example way to plot a table in matplotlib to get ride of default axes but no other formatting

    #fig, ax = plt.subplots(1,1, figsize=(10,10))

    # hide axes
    #fig.patch.set_visible(False)
    #ax.axis('off')
    #ax.axis('tight')

    #ax.table(cellText=cell_text, colLabels=column_headers, loc='center')

    #fig.tight_layout()
    '''


    plt.tight_layout(pad=3)

    script_dir = os.path.dirname(__file__)
    relative_results_dir = f'plots/{leagueName}/'
    results_dir = os.path.join(script_dir, relative_results_dir)
    if not os.path.isdir(results_dir):
        os.makedirs(results_dir)
    plt.savefig(f'{results_dir}overall_relative_results', dpi=100, transparent=False)


    return df_relative_record, df_relative_record_total, df_relative_record_total_plot



def determine_win_loss_margins(df_matchup_merge, logger, leagueName):

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

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout(pad=3)

    script_dir = os.path.dirname(__file__)
    relative_results_dir = f'plots/{leagueName}/'
    results_dir = os.path.join(script_dir, relative_results_dir)
    if not os.path.isdir(results_dir):
        os.makedirs(results_dir)
    plt.savefig(f'{results_dir}/winlossmargins.png', dpi=100, transparent=False)



def calculate_weekly_averages(df_matchup_merge, logger, currentMatchupPeriod):
    """ calculate average scores per week for the league """


    df_previous_matchup_merge = df_matchup_merge.query('Week < @currentMatchupPeriod').reset_index(drop=True)

    df_avgs = (df_previous_matchup_merge
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



def determine_lucky_results(team, teamName, df_matchup_merge, logger, currentMatchupPeriod, df_avgs,leagueName):
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
    ax.text(z/2-5, z-8, 'UNLUCKY LOSS\nw/ high points', style='italic', color='red')
    ax.text(z-20, z/2-5, 'LUCKY WIN\nw/ high points', style='italic', color='blue')
    ax.text(-z+1, -z/2-15, 'UNLUCKY LOSS\nw/ low points', style='italic', color='red')
    ax.text(-z+10, -z+1, 'LUCKY WIN\nw/ low points', style='italic', color='blue')
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

    plt.tight_layout(pad=3)

    script_dir = os.path.dirname(__file__)
    relative_results_dir = f'plots/{leagueName}/'
    results_dir = os.path.join(script_dir, relative_results_dir)
    if not os.path.isdir(results_dir):
        os.makedirs(results_dir)
    plt.savefig(f'{results_dir}{teamName}-lucky_unlucky_wins_losses', dpi=100, transparent=False)



def construct_url(): # deprecating this function in favor for fetch_league(), althogh this works just fine
    """Construct a url based on year of league"""

    '''
    ESPN has completely different API enpoints for leagues in current year vs. historical leagues
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



def fetch_league_data(): # depreciating this function in favor of fetch_league(), although this works just fine
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

    # This is useful if you want to dump the requested data into a json file for analysis of the data structure
    #with open('apidump.json', 'w') as json_file:
    #    json.dump(d, json_file)

    return d



def main():
    """ main() function """

    '''
    To run the program...
        python3 espnffscraper.py
    If you want to see output of the data to the console run debug mode
        python3 espnffscraper.py --debug
    If you want to put debug data in a file pipe to a file
        python3 espnffscraper.py --debub > debut.txt (or any filename yuo want)


    Public vs. Private Leagues
        If league is viewable to public can just call the API
        If league is not viewable to public need to call the API with some stored session cookies

    For now these need to be stored/input in ./constants/priv_constants.py
        league_id = <your league ID>
        swid = <your swid>
        espn_s2 = <your espn_s2>
        year = <your league year>
        league_open_to_public = <True/False, if your league is viewable to public or pivate
        sport = 'nfl' -- This would also technically work with a NBA league as well
    '''


    # deprecating this function in favor for fetch_league(), althogh this works just fine
    #url = construct_url()

    # depreciating this function in favor of fetch_league(), although this works just fine
    #d = fetch_league_data()

    d, logger, settings, currentMatchupPeriod, leagueName = fetch_league()

    df_team = create_team_dataframe(d, logger)

    df_matchup_merge = create_matchup_data(d, currentMatchupPeriod, logger, df_team)

    df_relative_record, df_relative_record_total, df_relative_record_total_plot  = create_relative_record_data(df_team, df_matchup_merge, logger, currentMatchupPeriod, leagueName)

    determine_win_loss_margins(df_matchup_merge, logger, leagueName)

    df_avgs = calculate_weekly_averages(df_matchup_merge, logger, currentMatchupPeriod)

    for i in range(len(df_team)):
        team = list(df_team.index.values.tolist())[i]
        teamName = df_team.iloc[i, 0]
        determine_lucky_results(team, teamName, df_matchup_merge, logger, currentMatchupPeriod, df_avgs, leagueName)

    plt.show()


    print(f'All done. Are you lucky or unlucky?\n')
if __name__ == '__main__':
    main()

