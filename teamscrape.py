import re
import time
import bs4
import pandas
import requests
import json
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
    with open(file_name, 'w') as f:
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
            league_dict[link.text] = link.attrs['href']

    return league_dict

def parse_team_ids(list_of_leagues):
    '''
    Function to parse the team ids for each team from the list of leagues 

    Input:
    list_of_leagues - a list containing leagues we need to parse for team ids

    Output:
    team_id_dict - JSON file containing every team and their ids
    '''
    teampages_dir = 'leaguepages\\'
    team_id_dict = {}


    for league in list_of_leagues:
        with open('{}{}.txt'.format(teampages_dir, league)) as f:
            soup = bs4.BeautifulSoup(f, 'lxml')
            teams = soup.find_all('a', {'href': re.compile('(team\.php\?team=)\d{1,3}')})
            for team in teams:
                team_id_dict[team.text] = team.attrs['href']
    
    write_to_json(team_id_dict, 'teamids.json')
    




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
    with open('leagueids.json', 'r') as f:
        league_dict = json.load(f)
    
    for league in league_scrape_list:
        print(league_dict[league])
        scrape_html('{}{}'.format(url, league_dict[league]), '{}.txt'.format(league))
        time.sleep(10)
    

def main():
    leagues_to_scrape = ['AHL ', 'SHL', ' Allsvenskan', 
    ' KHL', ' Liiga', ' Mestis', 'NCAA', 'OHL', 'QMJHL ', 'WHL', 'USHL', 'USDP']

    leagues_to_parse = ['AHL', 'SHL', 'Allsvenskan', 
    'KHL', 'Liiga', 'Mestis', 'NCAA', 'OHL', 'QMJHL ', 'WHL', 'USHL', 'USDP']
    url_base = 'http://www.eliteprospects.com/'
    # leagues_url_end = 'league_central.php'
    # leagues_html_file = 'leaguepages\league_page.txt'
    # scrape_html('{}{}'.format(url_base, leagues_url_end), 'league_page.txt')
    # league_dict = parse_league_ids(leagues_html_file)
    # write_to_json(league_dict, "leagueids.json")
    # scrape_league_page(leagues_to_scrape, url_base)
    parse_team_ids(leagues_to_parse)


if __name__ == '__main__':
    main()