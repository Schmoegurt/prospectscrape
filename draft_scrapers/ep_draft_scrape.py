import re
import time
from random import randint
import bs4
import requests
import pandas as pd
from unidecode import unidecode


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
        time.sleep(randint(1,3))

    bday_series = pd.Series(birth_dates)

    data_frame['birth_date'] = bday_series.values

    return data_frame

def draft_scrape(year_list, file_name):
    '''
    this function scrapes the the drafts of the years given in the year_list
    and writes them to the file name given in file_name. It also checks for
    duplicates and will not add the player if they are already in the file

    Inputs:
    year_list - a list of years of which to scrape NHL drafts
    file_name - name of the file the program will save the data to

    Outputs:
    None
    '''

    player_rows = []
    header = 'Overall|Team|player|seasons|GP|G|A|TP|PIM|player_id\n'
    player_ids = []


#change draft_stats to whatever file name you want it to be or else it will
#overwrite the next time you run the script
    with open(file_name, 'a+') as file:

#moves file pointer to the top of the file as opening it with a+ has it on the
#bottom
        file.seek(0)

#reads in lines from file to check later to make sure they aren't duplicated
        file_lines = file.readlines()

#this loop looks for the column headers and if finds them then breaks
#if not then it writes them
        for line in file:
            if header in line:
                break
            else:
                file.write(header)


#delete round headings
        for year in year_list:
            print(year)
            #scrape draft page
            #change the url to equal the base url of whatever league you are trying
            #to scrape
            url = 'https://www.eliteprospects.com/draft/nhl-entry-draft/{}'.format(year)
            req = requests.get(url)
            soup = bs4.BeautifulSoup(req.text, 'lxml')
            players = soup.select('div[id="drafted-players"] td')

            #delete round headings
            for x in players:
                if x.get('colspan', 0) != 0:
                    players.pop(players.index(x))

#remove white space and get text and break into rows for dataframe
            player_rows = [x.text.strip() for x in players]

            player_rows = [player_rows[x:x+9] for x
                           in range(0, len(player_rows), 9)]

            print(player_rows[-1])

#pulls the player url from the table and adds it to a list
            for x in range(2, len(players), 9):
                try:
                    player_ids.append(players[x].a['href'])
                except KeyError:
                    player_ids.append('11111')
                    continue

#appends the player url to the end of each player list
            for row, player_id in zip(player_rows, player_ids):
                row.append(player_id)

#pulls out player id from url using regex
            for row in player_rows:
                row[-1] = re.findall('\d+', row[-1])[0]

#append the year of the draft to each list or "row" in the data set
            for row in player_rows:
                row.append(str(year))

#check to see if the row is in the file already and if not then write it
            for row in player_rows:
                if '{}{}'.format('|'.join(row), '\n') not in file_lines:
                    file.write('{}{}'.format('|'.join(row), '\n'))

#sleep to keep from overloading the EP server and attracting data
            if year == year_list[-1]:
                continue
            else:
                time.sleep(90)

        columns = ['pick', 'team', 'player', 'seasons', 'gp', 'g', 'a', 'tp',
                   'pim' , 'player_id', 'year_of_draft']
        draft_df = pd.read_csv(file_name, sep='|', header=None, names=columns)
        draft_df = create_bd_col(draft_df)
        draft_df.to_csv(file_name, sep='|', index=False)



def main():
    '''
    This script is an NHL draft scraper that scrapes the NHL drafts of the
    years given by the users and stores them in a pipe delimited file

    Inputs:
    None

    Outputs:
    file_name - file containing scraped draft data
    '''

    year_start = int(input('Please input first year of the range you want drafted:\n'))
    year_end = input('Please input last year. If you only need one year enter "None":\n')
    file_name = input('Please input file name:\n')

    if year_end.lower() == 'none':
        years = [year_start]
    else:
        year_end = int(year_end) + 1
        years = list(range(year_start, year_end, 1))

    draft_scrape(years, file_name)



if __name__ == '__main__':
    main()
