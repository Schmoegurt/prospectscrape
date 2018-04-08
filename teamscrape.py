import re
import time
import bs4
import pandas as pd
import requests
import json
from random import randint
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

def parse_league_ids(file_name):
    '''
    Function to parse the league id html page from elite prospects and pull
    the league ids and store them in a dictionary which the function will 
    return

    Input:
    file_name - string containg path to html file

    Output:
    leaugeid_dict - dictionary containing league ids for each league that 
    elite prospects keeps track of.
    '''
    league_dict = {}
    with open(file_name, 'r') as f:
        soup = bs4.BeautifulSoup(f, 'lxml')
        leagues = soup.select('table[class=tableborder] a')
        for link in leagues:
            key = str(link.text.strip()).replace('/', '')
            league_dict[key] = link.attrs['href']

    write_to_json(league_dict, "leagueids.json")

def parse_team_ids(list_of_leagues):
    '''
    Function to parse the team ids for each team from the list of leagues 

    Input:
    list_of_leagues - a list containing leagues we need to parse for team ids

    Output:
    team_id_dict - JSON file containing every team and their ids
    '''
    teampages_dir = 'leaguepages\\'
    league_team_dict = {}


    for league in list_of_leagues:
        team_id_dict = {}
        with open('{}{}.txt'.format(teampages_dir, league)) as f:
            soup = bs4.BeautifulSoup(f, 'lxml')
            tables = soup.find_all('table')
            for row in tables[15].find_all('tr'):
                for x in row.find_all('a'):
                    team_id_dict[x.text.replace('/', '')] = x['href']
        league_team_dict[league] = team_id_dict
        print(league_team_dict)
    
    write_to_json(league_team_dict, 'teampages\\teamids.json')
    
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
    with open(file_name, 'w') as f:
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
    with open(page_file, encoding='utf-8') as f:
        soup = bs4.BeautifulSoup(f, 'lxml')
    # code for parsing the stats page for that team's season
    stats = soup.find_all('table')
    # parsing player stats
    for row in stats[15].find_all('tr'):
        player_stats.append([x.text for x in row.find_all('td')])
    # parsing goalie stats
    for row in stats[16].find_all('tr'):
        goalie_stats.append([x.text for x in row.find_all('td')])
    
    player_header = player_stats.pop(0)
    goalie_header = goalie_stats.pop(0)
    player_df = pd.DataFrame(player_stats, columns=player_header)
    goalie_df = pd.DataFrame(goalie_stats, columns=goalie_header)
    # remove empty rows
    player_df = player_df[(player_df['PLAYER'].str[-1]==')')]
    
    # getting player ids
    id_href = []
    player_ids = []
    for row in stats[15].find_all('tr'):
        id_href.append([x['href'] for x in row.find_all('a')])
    for row in id_href:
        if len(row) == 1:
            player_ids.append(row[0])
    player_ids.pop(0)
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
    player_df['PLAYER'] = player_df['PLAYER'].str.replace(r'(\(.+\))', '', expand=False)

    # drop # column as its not needed 
    goalie_df = goalie_df.drop(columns =['#'])
    player_df = player_df.drop(columns =['#'])
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
    team_code = soup.select('meta[property=og:url]')
    team_id = team_code[0].attrs['content']
    team_id = team_id[team_id.index('=')+1:]
    # get season year from file name
    season = page_file[-8:-4]
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
    roster_df['PLAYER'] = roster_df['PLAYER'].str.replace(r'(\(.+\))', '', expand=False)
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
    # Clean up player nubers and ids
    roster_df['player_id'] = player_ids
    roster_df['player_id'] = roster_df['player_id'].str.replace('player.php\?player=', '')
    roster_df['Number'] = roster_df['Number'].str.replace('#', '')
    roster_df['team_id'] = team_id
    roster_df['season'] = season
    print(roster_df.columns)
    roster_df['HT'] = roster_df['HT'].str.slice(start=3)
    roster_df['WT'] = roster_df['WT'].str.slice(start=2)


    return roster_df

def scrape_team_page(url_base, leagues, start_year, end_year):
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
    # creates list of years to scrape for each team adjust as neccesary
    years = list(range(start_year, end_year, 1))
    # opens team ids file and loads them in a dictionary
    with open('teampages\\teamids.json', 'r', encoding ='utf-8') as f:
        teams_dict = json.load(f)
    # Use this is you get disconnected to set the list at the last team you 
    # scraped so you don't have to parse the whole dictionary again
    # teams = list(teams_dict.keys())[100:]

    # Use the commented code if your connection gets lost along with the teams list 
    # started at the team you got disconnected on 
    error_list = []
    for league in leagues:
        for key, value in teams_dict[league].items():
            for year in years:
                # print(team)
                print(key)
                print(str(year))
                scrape_html('{}{}&year0={}'.format(url_base, value, str(year)), 'teampages\\{}roster{}.txt'.format(str(key).replace(' ', '-').replace('/', ''), year))
                scrape_html('{}{}&year0={}&status=stats'.format(url_base, value, str(year)), 'teampages\\{}{}stats.txt'.format(str(key).replace(' ', '-'), year))
                # scrape_html('{}{}&year0={}'.format(url_base, teams_dict[team], str(year)), 'teampages\\{}roster{}.txt'.format(team.replace(' ', '-'), year))
                # scrape_html('{}{}&year0={}&status=stats'.format(url_base, teams_dict[team], str(year)), 'teampages\\{}{}stats.txt'.format(team.replace(' ', '-'), year))
                time.sleep(randint(1,15))

def scrape_league_page(league_scrape_list, url):
    '''
    function to scrape each league page and return each team in the league 
    and their repsective url and id number as well 

    Input:
    league- the league to scrape the home page 
    league_dict- dictionary containing urls of all the leagues 

    Output:
    home_page_html - File containing html of each league home page
    '''
    # opens id json file and forms a dictionary
    with open('leaguepages\\leagueids.json', 'r') as f:
        league_dict = json.load(f)
    
    # using the list of leagues provided pulls the league url from 
    # dictionary and scrapes that leagues home page
    for league in league_scrape_list:
        scrape_html('{}{}'.format(url, league_dict[league]), 'leaguepages\\{}.txt'.format(league))
        time.sleep(10)
    

def main():
    # leagues = ['AHL', 'SHL', 'Allsvenskan', 
    # 'KHL', 'Liiga', 'Mestis', 'NCAA', 'OHL', 'QMJHL', 'WHL', 'USHL', 'USDP', 'Extraliga']
    leagues = ['Extraliga']
    url_base = 'http://www.eliteprospects.com/'
    # leagues_url_end = 'league_central.php'
    # leagues_html_file = 'leaguepages\\league_page.txt'
    # scrape_html('{}{}'.format(url_base, leagues_url_end), 'league_page.txt')
    # parse_league_ids(leagues_html_file)
    # scrape_league_page(leagues, url_base)
    # parse_team_ids(leagues)
    scrape_team_page(url_base, leagues, 2003, 2018)
    


if __name__ == '__main__':
    main()