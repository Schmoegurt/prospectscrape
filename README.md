### THIS IS NOW OBSOLETE WITH UPDATED ELITEPROSPECTS PAGE WILL KNOW WHEN NEW VERSION IS READY
# Elite Prospect Scraper

This is a script for scraping the Elite Prospects website. It will parse
each teams roster and stat page from each league you pass to it over the
range of years you provide as well. From there it will compile the data
into three `|` delimited files labeled `goalie_stats`, `player_stats`,
and `roster`. A fourth file `errorfile.txt.` will be create from the parsing
to log which files couldn't be succesfully parsed because there were
no stats/rosters to parse that season.

The script will also create three new directories `output_file`,
`leaguepages`, and `teampages`. Leaguepages will hold the html files
of each leagues main page that will be scraped to get the teams. It will also
store a `teamids.json` file that holds the league ids for every league on
elite prospects.

The `output_file` folder will be where your stat files and
error file will be written. And finally the `teampages` stores all the html
for each team per season. You can delete these once your stats are compiled
but if you need the info again you'll have to rescrape it.

Please do not abuse this as the people at Elite Prospects do work hard. This
is for research purposes only.

The easiest way to run this program is to clone it directly from
Github. If you have git change to the directory you want to download the
repo to and type:

```bash
git clone https://github.com/mcbarlowe/prospectscrape.git
```
Next I would create a virtual environment and then install the neccesary packages
by using pip and the `requirements.txt` file with this command: `pip install requirements.txt`.
Once that's downloaded you'll need to change into the `prospectscrape` directory to then edit
the `teamscrape.py` script with whatever text editor you want.

There are two main variables in the `main()` function you'll need
to change depending on what leagues and years you want to scrape. The
first is the `leagues` variable. This is an empty list you will fill with
the leagues you want to scrape. So if you want to just scrape say the
KHL you would change it to `['KHL']`. If you wanted to scrape Liiga
and the QMJHL, you would need to change it to `['Liiga', 'QMJHL']` and
so on.

The next variable you will need to change the year variables in this
function: `scrape_team_page(url_base, leagues, 2003, 2018)`. The first year
is the start year you want to begin scraping. Once those two isues are
set to the parameters you want then save the file and run the script like
you normally would. Happy scraping.

One more word of advice this is a slow process especially as you try to scrape multiple
leagues/seasons in one go. I've made it slower by making the program wait randomly
between scrapes so just don't expect it to be quick.


