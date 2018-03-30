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
        soup = bs4.BeautifulSoup(f, 'html.parser')
        leagues = soup.select('table[class=tableborder] a ')
        for link in leagues:
            league_dict[link.text] = link.attrs['href']

    return league_dict

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


def main():
    url_base = 'http://www.eliteprospects.com/'
    leagues_url_end = 'league_central.php'
    leagues_html_file = 'league_page.txt'
    # scrape_html('{}{}'.format(url_base, leagues_url_end), 'league_page.txt')
    league_dict = parse_league_ids(leagues_html_file)
    write_to_json(league_dict, "leagueids.json")


if __name__ == '__main__':
    main()