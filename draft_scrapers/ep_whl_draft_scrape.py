import bs4
import requests
import re
import pandas as pd

import time
player_rows = []
#change draft_stats to whatever file name you want it to be or else it will
#overwrite the next time you run the script
league_base = ['nwhl-draft', 'cwhl-draft']
for league in league_base:
    with open(league, 'w') as file:
        file.write('Overall|Team|player|seasons|GP|G|A|TP|PIM|player_id|year\n')
       #change the numbers here to widen or shorten your years to scrape
        years = list(range(2015,2018,1))

        for year in years:
            print(year)
            #scrape draft page
            #change the url to equal the base url of whatever league you are trying
            #to scrape
            url = 'https://www.eliteprospects.com/draft/{}/{}'.format(league,year)
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
            player_ids = []


            for x in range(2, len(players), 9):
                try:
                    player_ids.append(players[x].a['href'])
                except:
                    player_ids.append('11111')
                    continue

            for row, player_id in zip(player_rows, player_ids):
                row.append(player_id)
                row.append(year)

            for row in player_rows:
                row[-2] = re.findall('\d+', row[-2])[0]

            draft_df = pd.DataFrame(player_rows,
                                    columns = ['Overall', 'Team', 'player', 'seasons',
                                               'GP', 'G', 'A', 'TP', 'PIM', 'player_id', 'year'])
            draft_df.to_csv(file, sep='|', header=False, index=False)
            time.sleep(90)
