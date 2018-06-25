import re
import time
import bs4
import requests
import pandas as pd

'''
player_rows = []

#change draft_stats to whatever file name you want it to be or else it will
#overwrite the next time you run the script
with open('draft_stats', 'w') as file:
    file.write('Overall|Team|player|seasons|GP|G|A|TP|PIM|player_id\n')
   #change the numbers here to widen or shorten your years to scrape
    years = list(range(2003,2018,1))

    for year in years:
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

        player_rows = [player_rows[x:x+9] for x in range(0, len(player_rows), 9)]

        print(player_rows[-1])

        #get player ids


        #pulls the player url from the table and adds it to a list
        for x in range(2, len(players), 9):
            try:
                player_ids.append(players[x].a['href'])
            except:
                player_ids.append('11111')
                continue

        #appends the player url to the end of each player list
        for row, player_id in zip(player_rows, player_ids):
            row.append(player_id)

        #pulls out player id from url using regex
        for row in player_rows:
            row[-1] = re.findall('\d+', row[-1])[0]

        draft_df = pd.DataFrame(player_rows,
                                columns = ['Overall', 'Team', 'player', 'seasons',
                                           'GP', 'G', 'A', 'TP', 'PIM', 'player_id'])
        draft_df.to_csv(file, sep='|', header=False, index=False)
        time.sleep(90)
'''
def draft_scrape(year_list):
    player_rows = []
    header = 'Overall|Team|player|seasons|GP|G|A|TP|PIM|player_id\n'
    player_ids = []


#change draft_stats to whatever file name you want it to be or else it will
#overwrite the next time you run the script
    with open('draft_stats', 'a+') as file:

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

#create dataframe from the data to write to the file opened above
            draft_df = pd.DataFrame(player_rows,
                                    columns = ['Overall', 'Team', 'player',
                                               'seasons', 'GP', 'G', 'A', 'TP',
                                               'PIM', 'player_id'])

            draft_df['draft_year'] = year
            draft_df.to_csv(file, sep='|', header=False, index=False)

#sleep to keep from overloading the EP server and attracting data
            if year == year_list[-1]:
                continue
            else:
                time.sleep(90)

def main():

    year_start = int(input('Please input first year of the range you want drafted:\n'))
    year_end = input('Please input last year. If you only need one year enter "None":\n')

    if year_end.lower() == 'none':
        years = [year_start]
    else:
        year_end = int(year_end) + 1
        years = list(range(year_start, year_end,1))

    draft_scrape(years)



if __name__ == '__main__':
    main()
