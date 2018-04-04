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
    with open(file_name, 'w', encoding="utf8") as f:
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
            teams = soup.find_all('a', {'href': re.compile(r'(team\.php\?team=)\d{1,9}$')})
            for team in teams:
                team_id_dict[str(team.text).replace('/', '')] = team.attrs['href']
        league_team_dict[league] = team_id_dict
    
    write_to_json(league_team_dict, 'teamids.json')
    
def write_to_json(dictionary, file_name):
    '''
    Quick function to write a dictionary to a json file

    Inputs:
    file_name - Name of file to write to 
    dictionary - dictionary to write to json

    Outputs:
    JSON File - Writes JSON file to store the dictionary
    '''
    json_data = json.dumps(dictionary, ensure_ascii=True)
    with open(file_name, 'w', encoding='UTF-8') as f:
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
    with open(page_file) as f:
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
    with open('teampages\\teamids.json', 'r') as f:
        teams_dict = json.load(f)
    # Use this is you get disconnected to set the list at the last team you 
    # scraped so you don't have to parse the whole dictionary again
    # teams = list(teams_dict.keys())[100:]

    # Use the commented code if your connection gets lost along with the teams list 
    # started at the team you got disconnected on 
    for league in leagues:
        for key, value in teams_dict[league].items():
            for year in years:
                # print(team)
                print(key)
                print(str(year))
                scrape_html('{}{}&year0={}'.format(url_base, value, str(year)), 'teampages\\{}roster{}.txt'.format(str(key).replace(' ', '-'), year))
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
        scrape_html('{}{}'.format(url, league_dict[league]), '{}.txt'.format(league))
        time.sleep(10)
    

def main():
    leagues = ['AHL', 'SHL', 'Allsvenskan', 
    'KHL', 'Liiga', 'Mestis', 'NCAA', 'OHL', 'QMJHL ', 'WHL', 'USHL', 'USDP', 'Extraliga']
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