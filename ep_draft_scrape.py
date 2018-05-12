import bs4
import requests
import re
import pandas as pd

import time
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
        player_ids = []


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
