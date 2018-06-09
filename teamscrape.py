import os, sys
import time
import json
from random import randint
import requests
import bs4
import pandas as pd

############################################################################
## This is a series of functions designed to scrape the Elite Prosepects  ##
## webpage and store the results in a tab delimited files. It scraps each ##
## team's roster and stats page for the leagues given. All code written   ##
## by Matthew Barlowe @matt_barlowe on twitter mcbarlowe on github        ##
############################################################################

def scrape_html(url, file_name):
    '''
    Function to pull the html of a webpage and write the html to a text file
    to parse at a later date

    Input:
    url - url to scrape

    Output:
    text_file - file written to local directory containing html
    '''
    r = requests.get(url)
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(r.text)

#This function is not needed for new EP website structure remove after
#final testing
def parse_league_ids(file_name, output_file_name):
    '''
    Function to parse the league id html page from elite prospects and pull
    the league ids and store them in a dictionary which the function will
    return

    Input:
    file_name - string containg path to html file

    Output:
    leagueid_dict - dictionary containing league ids for each league that
    elite prospects keeps track of.
    '''
    league_dict = {}
    with open(file_name, 'r', encoding='utf-8') as f:
        soup = bs4.BeautifulSoup(f, 'lxml')

    leagues = soup.select('table[class=tableborder] a')
    for link in leagues:
        key = str(link.text.strip()).replace('/', '')
        if key in league_dict.keys():
            league_dict['{}-W'.format(key)] = link.attrs['href'].replace('league_home.php?leagueid=', '')
        else:
            league_dict[key] = link.attrs['href'].replace('league_home.php?leagueid=', '')

    write_to_json(league_dict, output_file_name)

#this has been converted to the new EP format
def parse_team_ids(list_of_leagues, start_year, end_year):
    '''
    Function to parse the team ids for each team from the list of leagues

    Input:
    list_of_leagues - a list containing leagues we need to parse for team ids

    Output:
    team_id_dict - JSON file containing every team and their ids
    '''
    teampages_dir = 'leaguepages'
    league_team_dict = {}
    years = list(map(str, list(range(start_year, end_year + 1, 1))))


    for league in list_of_leagues:
        year_dict = {}
        for year in years:
            print(league)
            team_id_dict = {}
            with open(os.path.join(teampages_dir, league, year, '{}.txt'.format(league)), encoding='utf-8') as f:
                soup = bs4.BeautifulSoup(f, 'lxml')
            tables = soup.find('table', {'class': 'table standings table-sortable'})
            for row in tables.find_all('tr'):
                for x in row.find_all('a'):
                    team_id_dict[x.text.strip().replace('/', '')] = x['href'].split('/')[4]
                team_id_dict.pop('#', None)
                team_id_dict.pop('GP', None)
                team_id_dict.pop('TEAM', None)
                team_id_dict.pop('W', None)
                team_id_dict.pop('T', None)
                team_id_dict.pop('L', None)
                team_id_dict.pop('OTW', None)
                team_id_dict.pop('OTL', None)
                team_id_dict.pop('GF', None)
                team_id_dict.pop('GA', None)
                team_id_dict.pop('+-', None)
                team_id_dict.pop('TP', None)
                team_id_dict.pop('POSTSEASON', None)
            year_dict[str(year)] = team_id_dict
        league_team_dict[league] = year_dict
    print(league_team_dict)

    write_to_json(league_team_dict,
                  os.path.join('output_files', 'teamids.json'))

def write_to_json(dictionary, file_name):
    '''
    Quick function to write a dictionary to a json file

    Inputs:
    file_name - Name of file to write to
    dictionary - dictionary to write to json

    Outputs:
    JSON File - Writes JSON file to store the dictionary
    '''
    json_data = json.dumps(dictionary)
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(json_data)

def parse_team_stats(page_file):
    '''
    This function scrapes the teams roster and stats pages for each year
    of the team that is scraped

    Inputs:
    web_page - web page to scrape

    Outputs:
    stats_df - data frame containing stats and data from the web page
    '''
    player_stats = []
    goalie_stats = []
    #get season and team info from file name
    season = page_file[-13:-9]
    with open(page_file, encoding='utf-8') as f:
        soup = bs4.BeautifulSoup(f, 'lxml')
    # code for parsing the stats page for that team's season
    stats = soup.find_all('table')
    team = soup.select('meta[property=og:title]')[0].attrs['content']
    team_id = soup.select('meta[property=og:url]')[0].attrs['content']
    team_id = team_id[team_id.index('=')+1:]
    # parsing player stats
    for row in stats[15].find_all('tr'):
        player_stats.append([x.text for x in row.find_all('td')])
    # parsing goalie stats
    for row in stats[16].find_all('tr'):
        goalie_stats.append([x.text for x in row.find_all('td')])

    # create column names for goalie/player dataframes
    player_header = player_stats.pop(0)
    goalie_header = goalie_stats.pop(0)
    #create data frames from scraped list of lists
    player_df = pd.DataFrame(player_stats, columns=player_header)
    goalie_df = pd.DataFrame(goalie_stats, columns=goalie_header)
    # remove empty rows
    player_df = player_df[~(player_df['PLAYER'].str[-1]=='.')]

    # getting player ids
    id_href = []
    player_ids = []
    for row in stats[15].find_all('tr'):
        id_href.append([x['href'] for x in row.find_all('a')])
    for row in id_href:
        if len(row) == 1:
            player_ids.append(row[0])
    print(len(player_ids))
    print(player_df.shape)
    # Clean up player nubers and ids
    player_df['player_id'] = player_ids
    player_df['player_id'] = player_df['player_id'].str.replace('player.php\?player=', '')

    # getting goalie ids
    id_href = []
    goalie_ids = []
    for row in stats[16].find_all('tr'):
        id_href.append([x['href'] for x in row.find_all('a')])
    for row in id_href:
        if len(row) == 1:
            goalie_ids.append(row[0])
    print(goalie_ids)
    print(goalie_df.shape)
    # Clean up player nubers and ids
    goalie_df['player_id'] = goalie_ids
    goalie_df['player_id'] = goalie_df['player_id'].str.replace('player.php\?player=', '')

    # remove position as its already on the roster table
    player_df['PLAYER'] = player_df['PLAYER'].str.replace(r'(\(.+\))', '')

    # drop # column as its not needed
    goalie_df = goalie_df.drop(columns =['#'])
    player_df = player_df.drop(columns =['#'])
    player_col_names = ['Player', 'GP', 'G', 'A', 'TP', 'PIM', '+/-', ' ',
                        'playoff_GP', 'playoff_G', 'playoff_A', 'playoff_TP',
                        'playoff_PIM', 'playoff_+/-', 'player_id']
    goalie_col_names = ['Player', 'GP', 'GAA', 'SV%', ' ', 'playoff_GP',
                        'playoff_GAA', 'playoff_SV%', 'player_id']

    player_df.columns = player_col_names
    goalie_df.columns = goalie_col_names
    player_df['season'] = season
    goalie_df['season'] = season
    player_df['team'] = team
    goalie_df['team'] = team
    player_df['team_id'] = team_id
    goalie_df['team_id'] = team_id


    return player_df, goalie_df

def parse_team_roster(page_file):
    '''
    This function scrapes the teams roster page for each year
    of the team that is scraped

    Inputs:
    page_file - web page to scrape

    Outputs:
    roster_df - data frame containing stats and data from the web page
    '''
    team_roster = []
    player_ids = []
    with open(page_file, encoding='utf-8') as f:
        soup = bs4.BeautifulSoup(f, 'lxml')

    # parse team code
    team_id = soup.select('meta[property=og:url]')[0].attrs['content']
    team_id = team_id[team_id.index('=')+1:]
    # get season year and team name from file name
    season = page_file[-8:-4]
    team = soup.select('meta[property=og:title]')[0].attrs['content']
    # code for parsing the stats page for that team's season
    stats = soup.find_all('table')
    # parsing team roster
    for row in stats[15].find_all('tr'):
        team_roster.append([x.text for x in row.find_all('td')])

    roster_header = team_roster.pop(0)
    roster_df = pd.DataFrame(team_roster, columns=roster_header)
    print(roster_df.head())
    roster_df['PLAYER'] = roster_df['PLAYER'].str.strip()
    # create position column
    roster_df['Position'] = roster_df['PLAYER'].str.extract(r'(\(.+\))')
    roster_df['Position'] = roster_df['Position'].str.replace('(', '')
    roster_df['Position'] = roster_df['Position'].str.replace(')', '')
    roster_df['\\xa0#'] = roster_df['Position'].str.replace('#', '')
    roster_df['PLAYER'] = roster_df['PLAYER'].str.replace(r'(\(.+\))', '')
    #rearrange columns and rename some
    colnames = roster_df.columns.tolist()
    # remove columns that have no data
    colnames.pop(9)
    colnames.pop(0)
    colnames.pop()
    colnames = colnames[:3] + colnames[-1:] + colnames[3:-1]
    roster_df = roster_df[colnames]
    #rename columns in df
    colnames[0] = 'Number'
    colnames[-1] = 'Shots'
    roster_df.columns = colnames
    # drop empty rows
    roster_df = roster_df[~(roster_df['PLAYER']=='')]
    roster_df = roster_df.dropna(axis=0, how='all')

    # getting player ids
    id_href = []
    player_ids = []
    for row in stats[15].find_all('tr'):
        id_href.append([x['href'] for x in row.find_all('a')])
    id_href = id_href[1:]
    for row in id_href:
        if len(row) > 1:
            player_ids.append(row[0])
    # Clean up player numbers and ids
    roster_df['player_id'] = player_ids
    roster_df['player_id'] = roster_df['player_id'].str.replace('player.php\?player=', '')
    roster_df['Number'] = roster_df['Number'].str.replace('#', '')
    roster_df['team_id'] = team_id
    roster_df['season'] = season
    print(roster_df.columns)
    roster_df['HT'] = roster_df['HT'].str.slice(start=3)
    roster_df['WT'] = roster_df['WT'].str.slice(start=2)
    roster_df['team'] = team

    return roster_df

def scrape_team_page(url_base, leagues):
    '''
    Function to pull the html for each teams seasons and save it to the file

    Inputs:
    url_base - The Elite Prospects base url
    leagues - list of leagues to scrape
    start_year - year to start scraping the teams pages
    end_year - year to end scraping teams pages

    Outputs:
    text_files - a bunch of text files containing each teams roster and stats
    pages html for the past 20 years
    '''

    # opens team ids file and loads them in a dictionary
    with open(os.path.join('output_files', 'teamids.json'), 'r', encoding ='utf-8') as f:
        teams_dict = json.load(f)

    for league in leagues:
        # Checks for directory existence if exist catches exception and moves on
        try:
            os.mkdir(os.path.join('teampages', league))
        except FileExistsError as ex:
            print('Folder already exists')

        for year, teams in teams_dict[league].items():
            try:
                os.mkdir(os.path.join('teampages', league, year))
            except FileExistsError as ex:
                pass
            for team, team_id in teams.items():
    # Checks for directory existence if exist catches exception and moves on
                scrape_html('{}team.php?team={}&year0={}'.format(url_base, team_id, year),
                            os.path.join('teampages', league, year,
                            '{}roster{}.txt'.format(team.replace(' ', '-').replace('/', ''), year)))
                scrape_html('{}team.php?team={}&year0={}&status=stats'.format(url_base, team_id, year),
                            os.path.join('teampages', league, year,
                            '{}{}stats.txt'.format(team.strip().replace(' ', '-'), year)))
                time.sleep(randint(1,10))

#this has been converted to the new Elite Prospects webpage format
def scrape_league_page(league_scrape_list, url, year_start, year_end):
    '''
    function to scrape each league page and return each team in the league
    and their repsective url and id number as well

    Input:
    league- the league to scrape the home page
    league_dict- dictionary containing urls of all the leagues

    Output:
    home_page_html - File containing html of each league home page
    '''

    # using the list of leagues provided pulls the league url from
    # dictionary and scrapes that leagues home page
    years = list(map(str, list(range(year_start, year_end+1, 1))))
    for league in league_scrape_list:
        os.mkdir(os.path.join('leaguepages', league))
        print(league)
        for year in years:
            print(year)
            os.mkdir(os.path.join('leaguepages', league, year))
            scrape_html('{}league/{}/{}-{}'.format(url, league,
                                                   str(int(year)-1), year),
                        os.path.join('leaguepages', league, year,
                                     '{}.txt'.format(league)))
            time.sleep(10)

def add_headers():
    '''
    function to write headers to the files produced in the parse_all_files() function

    Inputs:
    None

    Outputs:
    text files - The three text files create in parse_all_files() function but with column headers
    '''
    player_df = pd.read_csv(os.path.join('output_files', 'player_stats'), sep='|', header=None,
                            names=['Player', 'GP', 'G', 'A', 'TP', 'PIM', '+/-', ' ', 'playoff_GP',
                                   'playoff_G', 'playoff_A', 'playoff_TP', 'playoff_PIM', 'playoff_+/-',
                                   'player_id', 'season', 'team', 'team_id'])
    player_df.to_csv(os.path.join('output_files', 'player_stats'), sep='|', index=False)
    goalie_df = pd.read_csv(os.path.join('output_files', 'goalie_stats'), sep='|', header=None,
                            names=['Player', 'GP', 'GAA', 'SV%', ' ', 'playoff_GP', 'playoff_GAA',
                                   'playoff_SV%', 'player_id', 'season', 'team', 'team_id'])
    goalie_df.to_csv(os.path.join('output_files', 'goalie_stats'), sep='|', index=False)
    roster_df = pd.read_csv(os.path.join('output_files', 'rosters'), low_memory=False, sep='|', header=None,
                            names=['#', 'Player', 'Age', 'Position', 'Birthdate', 'Birthplace',
                                   'HT', 'WT', 'Shots', 'player_id', 'team_id', 'season', 'team'])
    roster_df.to_csv(os.path.join('output_files', 'rosters'), sep='|', index=False)

def parse_all_files():
    '''
    This function parses all the text (both roster and stats) files scraped
    with the team_page_scrape function

    Inputs:
    None

    Outputs:
    text file - four text files containg, error log, roster info, player stats, goalie stats
    '''
    with open(os.path.join('output_files', 'rosters'), 'w', encoding='utf-8') as a:
        with open(os.path.join('output_files', 'player_stats'), 'w', encoding='utf-8') as b:
            with open(os.path.join('output_files', 'goalie_stats'), 'w', encoding='utf-8') as c:
                 with open (os.path.join('output_files', 'errorfile.txt'), 'w', encoding='utf-8') as e:
                    for root, subdir, files in os.walk('teampages'):
                        for name in files:
                            if 'stats' in name:
                                try:
                                    player_df, goalie_df = parse_team_stats(os.path.join(root, name))
                                    player_df.to_csv(b, sep='|', header=False, index=False)
                                    goalie_df.to_csv(c, sep='|', header=False, index=False)
                                except Exception as ex:
                                    print(ex)
                                    e.write('{}{}'.format(name, '\n'))
                            else:
                                try:
                                    roster_df = parse_team_roster(os.path.join(root, name))
                                    roster_df.to_csv(a, sep='|', header=False, index=False)
                                except Exception as ex:
                                    print(ex)
                                    e.write('{}{}'.format(name, '\n'))
def clean_data():
    import numpy as np
    '''
    function to clean the compiled data from parsing the roster and stats pages of each team

    Inputs:
    None

    Ouputs:
    three pipe delimited files of cleaned data
    '''
    # replace all the white space lines that matching the player ids created

    player_df = pd.read_csv(os.path.join('output_files', 'player_stats'), sep='|')
    goalie_df = pd.read_csv(os.path.join('output_files', 'goalie_stats'), sep='|')
    player_df = player_df.drop(columns = [' '])
    goalie_df = goalie_df.drop(columns = [' '])
    player_df = player_df.replace(r'^\s+$', np.nan, regex=True)
    player_df = player_df[pd.isna(player_df['GP']) == 0]
    player_df = player_df.replace(to_replace='-', value=0)
    player_df = player_df.replace(to_replace='--6', value = -6)
    player_df.fillna(value=0, inplace=True)
    player_df[['GP', 'G', 'A', 'TP', 'PIM', '+/-', 'playoff_GP', 'playoff_G',
               'playoff_A', 'playoff_TP', 'playoff_PIM', 'playoff_+/-']] =  player_df[
                   ['GP', 'G', 'A', 'TP', 'PIM', '+/-', 'playoff_GP', 'playoff_G',
                    'playoff_A', 'playoff_TP', 'playoff_PIM', 'playoff_+/-']].astype('int')

    player_df.to_csv(os.path.join('output_files', 'player_stats')
                     , sep='|', index=False)
    goalie_df.to_csv(os.path.join('output_files', 'goalie_stats')
                     , sep='|', index=False)

def directory_setup():
    try:
        os.mkdir('teampages')
    except FileExistsError as ex:
        print('Folder already exists')
    try:
        os.mkdir('leaguepages')
    except FileExistsError as ex:
        print('Folder already exists')
    try:
        os.mkdir('output_files')
    except FileExistsError as ex:
        print('Folder already exists')

def cleanup(delimited_file):
    '''
    This will be a function to zip the html text pages and store them in a zip
    file.
    Inputs:
    delimited_file - a pipe delimited file containing player data

    Outputs:
    cleaned_file - a pipe delimited file where the data as been clean
    '''
    stat_df = pd.read_csv(delimited_file, sep='|')
    stat_df = stat_df.groupby(['player_id', 'Player', 'season', 'team', 'team_id'],
                                as_index=False).sum()
    stat_df.to_csv(delimited_file, sep='|', index=False)

    return

def main():
    # adjust here to select which leages you want to scrape the team pages of
    '''
    leagues = ['AHL', 'SHL', 'Allsvenskan',
                'KHL', 'Liiga', 'Mestis', 'NCAA', 'OHL',
                'QMJHL', 'WHL', 'USHL', 'USDP', 'Extraliga']
    '''
    leagues = ['Liiga']
    url_base = 'http://www.eliteprospects.com/'
    directory_setup()
    # if you need to rebuild the leagueid json file that comes with this repo then
    # scrape the central league page

    # This compiles a tem id dictionary based on what leagues you pass to
    # it from the leagues list variable the repo comes built in with the team ids
    # of the leagues in the list above if you want to add more just delete the
    # leagues and insert the ones you want and uncomment the next two lines.
    # If you want women's leagues those will be appended with a '-W' where
    # they have the same name as men's leagues.
    #scrape_league_page(leagues, url_base, 2017, 2018)
    parse_team_ids(leagues, 2017, 2018)

    # This scrapes the team pages and actually gathers the html for each teams
    # from the roster and stats pages and writes them to the disk. The
    # parse_all_files actually compiles all that html and produces |
    # delimited files of the data.
    #scrape_team_page(url_base, leagues)
    #parse_all_files()

    # The next two functions add the headers and cleans up the player_stats
    # data there will be duplicates for some players if they played in special
    # tournaments like the Memorial Cup or Champions League in Europe. This is more
    # so for goalies than players as I don't want to average sv% and without
    # shot for against can't accurately calculate
    #add_headers()
    #clean_data()
    #cleanup(os.path.join('output_files', 'player_stats'))
if __name__ == '__main__':
    main()
