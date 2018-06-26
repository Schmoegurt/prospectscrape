import re
import time
import bs4
import requests

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
    with open('draft_stats', 'a+') as file:

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
