import os
import shutil
import re
import time
import json
from random import randint
from unidecode import unidecode
import requests
import bs4
import pandas as pd

############################################################################
## This is a series of functions designed to scrape the Elite Prosepects  ##
## webpage and store the results in a tab delimited files. It scrapes each##
## team's roster and stats page for the leagues given. All code written   ##
## by Matthew Barlowe @matt_barlowe on twitter mcbarlowe on github        ##
############################################################################

def get_birthdate(url):
    '''
    this will pull the birthdate for the player url given

    Inputs:
    url - string of the url of the player

    Outputs:
    birth_date - string of the players birthdate
    '''
    req = requests.get(url)
    soup = bs4.BeautifulSoup(req.text, 'lxml')

    player_info = soup.select('div[class="col-xs-8 fac-lbl-dark"]')
    birth_date = player_info[0].text.strip()

    return birth_date

def create_bd_col(data_frame):

    birth_dates = []
    url_base = 'http://www.eliteprospects.com/player/'

    player_ids = data_frame['player_id'].tolist()
    player_names = data_frame['player'].map(unidecode).tolist()
    player_names = [name.split(' ') for name in player_names]
    player_names = ['-'.join(name) for name in player_names]

    for play_id, name in zip(player_ids, player_names):
        birthday = get_birthdate('{}{}/{}'.format(url_base, play_id, name))
        birth_dates.append(birthday)
        time.sleep(randint(1,5))

    bday_series = pd.Series(birth_dates)

    data_frame['birth_date'] = bday_series.values

    return data_frame


#this function works with new EP format
def scrape_html(url, file_name):
    '''
    Function to pull the html of a webpage and write the html to a text file
    to parse at a later date

    Input:
    url - url to scrape

    Output:
    text_file - file written to local directory containing html
    '''
    req = requests.get(url)
    with open(file_name, 'w', encoding='utf-8') as html_file:
        html_file.write(req.text)

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
    with open(file_name, 'r', encoding='utf-8') as html_file:
        soup = bs4.BeautifulSoup(html_file, 'lxml')

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

#this function works with the new EP format
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

#this function works with the new EP format
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
    player_table = soup.find('table', {'class': 'table table-striped table-sortable skater-stats highlight-stats'})

    goalie_table = soup.find('table', {'class': 'table table-striped table-sortable goalie-stats highlight-stats'})

    team_id = soup.select('meta[name=description]')[0].attrs['content'].split('-')
    team = team_id[0].strip()
    league = team_id[1].strip()
    # parsing player stats
    for row in player_table.find_all('tr'):
        if row.get('class', ['nope'])[0] in ['title', 'space']:
            continue
        player_stats.append([x.text.strip() for x in row.find_all('td')])
    # parsing goalie stats
    for row in goalie_table.find_all('tr'):
        if row.get('class', ['nope'])[0] in ['title', 'space']:
            continue
        goalie_stats.append([x.text.strip() for x in row.find_all('td')])

    player_stats.pop(0)
    goalie_stats.pop(0)
    #create lists for column names
    player_columns = ['player', 'GP', 'G', 'A', 'TP', 'PIM', '+/-',
                      'playoff_GP', 'playoff_G', 'playoff_A', 'playoff_TP',
                      'playoff_PIM', 'playoff_+/-']

    goalie_columns = ['player', 'GP', 'GAA', 'SV%', 'playoff_GP', 'playoff_GAA',
                      'playoff_SV%']

    #create data frames from scraped list of lists
    player_df = pd.DataFrame(player_stats)
    goalie_df = pd.DataFrame(goalie_stats)

    #drop unnecesary columns
    player_df = player_df.drop([0, 8], axis = 1)
    goalie_df = goalie_df.drop([0, 5], axis = 1)

    player_df.columns = player_columns
    goalie_df.columns = goalie_columns

    # remove empty rows
    #player_df = player_df[~(player_df['PLAYER'].str[-1]=='.')]

    # getting player ids
    id_href = []

    for row in player_table.find_all('tr'):
        if row.get('class', ['nope'])[0] in ['title', 'space']:
            continue
        id_href.append([x['href'] for x in row.find_all('a')])

    id_href = [x for x in id_href if len(x) > 0]
    id_href = [x[0] for x in id_href]
    player_ids = [re.search(r'(\/\d+\/)', x).group(1) for x in id_href]
    player_ids = [x.replace('/', '') for x in player_ids]
    player_df['player_id'] = player_ids

    # getting goalie ids
    id_href = []

    for row in goalie_table.find_all('tr'):
        if row.get('class', ['nope'])[0] in ['title', 'space']:
            continue
        id_href.append([x['href'] for x in row.find_all('a')])

    id_href = [x for x in id_href if len(x) > 0]
    id_href = [x[0] for x in id_href]
    goalie_ids = [re.search(r'(\/\d+\/)', x).group(1) for x in id_href]
    goalie_ids = [x.replace('/', '') for x in goalie_ids]
    goalie_df['player_id'] = goalie_ids

    # remove position as its already on the roster table
    player_df['player'] = player_df['player'].str.replace(r'(\(.+\))', '')
    player_df['season'] = season
    goalie_df['season'] = season
    player_df['team'] = team
    goalie_df['team'] = team
    player_df['league'] = league
    goalie_df['league'] = league


    return player_df, goalie_df

#this function has been converted for the new EP format
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
    team_id = soup.select('meta[name=description]')[0].attrs['content'].split('-')
    team = team_id[0].strip()
    league = team_id[1].strip()

    # get season year and team name from file name
    season = page_file[-8:-4]

    # code for parsing the stats page for that team's season
    stats = soup.find('table', {'class': 'table table-striped table-sortable roster'})

    # parsing team roster
    for row in stats.find_all('tr'):
        if row.get('class', ['nope'])[0] == 'title':
            continue
        team_roster.append([x.text.strip() for x in row.find_all('td')])

    #dropping unneccesary columns and creating names for them
    team_roster.pop(0)
    roster_df = pd.DataFrame(team_roster)
    roster_df.drop([0, 1, 2], axis=1, inplace=True)
    roster_df.columns = ['player', 'age', 'birth_year', 'birthplace', 'HT', 'WT', 'shoots']
    roster_df['player'] = roster_df['player'].str.strip()


    # create position column
    roster_df['position'] = roster_df['player'].str.extract(r'(\(.+\))')
    roster_df['position'] = roster_df['position'].str.replace('(', '')
    roster_df['position'] = roster_df['position'].str.replace(')', '')
    roster_df['player'] = roster_df['player'].str.replace(r'(\(.+\))', '')

    # drop empty rows
    roster_df = roster_df[~(roster_df['player']=='')]
    roster_df = roster_df.dropna(axis=0, how='all')

    #the strips don't remove the C and A markings so we have to remove them
    #with a created function
    def clean_name(name):
        new_name = name.split(' ')
        clean_name = ' '.join(new_name[0:2])
        return clean_name
    roster_df['player'] = roster_df['player'].str.replace('\\n', '')
    roster_df.replace(u'\xa0',u'', regex=True, inplace=True)
    roster_df['player'] = roster_df['player'].map(clean_name)

    # getting player ids
    id_href = []
    player_ids = []
    for row in stats.find_all('tr'):
        id_href.append([x['href'] for x in row.find_all('a')])

    #clean up the links pulled to only have the links for players and no
    #extraneous links. Also pull the id form the link using regex and clean
    #them up
    id_href = [x for x in id_href if len(x) > 1]
    id_href = [x[0] for x in id_href]
    player_ids = [re.search(r'(\/\d+\/)', x).group(1) for x in id_href]
    player_ids = [x.replace('/', '') for x in player_ids]


    # Add player ids, season, team, and league for each player
    roster_df['player_id'] = player_ids
    roster_df['season'] = season
    roster_df['team'] = team
    roster_df['league'] = league

    return roster_df

#this function has been converted for the new EP format
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
                scrape_html('{}team/{}/{}/{}-{}'.format(url_base, team_id, unidecode(team),
                                                     str(int(year)-1), year),
                            os.path.join('teampages', league, year,
                            '{}roster{}.txt'.format(team.replace(' ', '-').replace('/', ''), year)))
                scrape_html('{}team/{}/{}/{}-{}?tab=stats#players'\
                            .format(url_base, team_id, unidecode(team), str(int(year)-1), year),
                            os.path.join('teampages', league, year,
                            '{}{}stats.txt'.format(team.strip().replace(' ', '-'), year)))
                time.sleep(randint(1,10))

#this function has been converted to the new Elite Prospects webpage format
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

#this has been converted to new EP format
def add_headers():
    '''
    function to write headers to the files produced in the parse_all_files() function

    Inputs:
    None

    Outputs:
    text files - The three text files create in parse_all_files() function but with column headers
    '''
    player_df = pd.read_csv(os.path.join('output_files', 'player_stats'), sep='|', header=None,
                            names=['player', 'GP', 'G', 'A', 'TP', 'PIM', '+/-', 'playoff_GP',
                                   'playoff_G', 'playoff_A', 'playoff_TP', 'playoff_PIM', 'playoff_+/-',
                                   'player_id', 'season', 'team', 'league'])
    player_df.to_csv(os.path.join('output_files', 'player_stats'), sep='|', index=False)
    goalie_df = pd.read_csv(os.path.join('output_files', 'goalie_stats'), sep='|', header=None,
                            names=['player', 'GP', 'GAA', 'SV%', 'playoff_GP', 'playoff_GAA',
                                   'playoff_SV%', 'player_id', 'season', 'team',
                                   'league'])
    goalie_df.to_csv(os.path.join('output_files', 'goalie_stats'), sep='|', index=False)
    roster_df = pd.read_csv(os.path.join('output_files', 'rosters'), low_memory=False, sep='|', header=None,
                            names=['player', 'age', 'birth_year',
                                   'birthplace', 'HT', 'WT', 'shoots',
                                   'contract', 'position', 'player_id',
                                   'season', 'team', 'league', 'birthdate']
)
    roster_df.to_csv(os.path.join('output_files', 'rosters'), sep='|', index=False)

#this function works with the new EP format
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
                                    roster_df = create_bd_col(roster_df)
                                    roster_df.to_csv(a, sep='|', header=False, index=False)
                                except Exception as ex:
                                    print(ex)
                                    e.write('{}{}'.format(name, '\n'))

#this function works with the new EP format
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

#this works with new EP format
def directory_setup():
    shutil.rmtree('teampages')
    shutil.rmtree('leaguepages')
    shutil.rmtree('output_files')
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

#rework this to actually zip files and to work with new EP format
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
    stat_df = stat_df.groupby(['player_id', 'player', 'season', 'team', 'league'],
                                as_index=False).sum()
    stat_df.to_csv(delimited_file, sep='|', index=False)

    return

def main():
    # adjust here to select which leages you want to scrape the team pages of

    leagues = ['GTMMHL']
    url_base = 'http://www.eliteprospects.com/'
    directory_setup()

    #changes these variables to adjust which years you want to scrape
    start_year = 2017
    end_year  = 2018

    # This compiles a team id dictionary based on what leagues you pass to
    # it from the leagues list variable the repo comes built in with the team ids
    # of the leagues in the list above if you want to add more just delete the
    # leagues and insert the ones you want and uncomment the next two lines.
    # If you want women's leagues those will be appended with a '-W' where
    # they have the same name as men's leagues.
    scrape_league_page(leagues, url_base, start_year, end_year)
    parse_team_ids(leagues, start_year, end_year)

    # This scrapes the team pages and actually gathers the html for each teams
    # from the roster and stats pages and writes them to the disk. The
    # parse_all_files actually compiles all that html and produces |
    # delimited files of the data.
    scrape_team_page(url_base, leagues)
    parse_all_files()

    # The next two functions add the headers and cleans up the player_stats
    # data there will be duplicates for some players if they played in special
    # tournaments like the Memorial Cup or Champions League in Europe. This is more
    # so for goalies than players as I don't want to average sv% and without
    # shot for against can't accurately calculate
    add_headers()
    clean_data()
    cleanup(os.path.join('output_files', 'player_stats'))
if __name__ == '__main__':
    main()
