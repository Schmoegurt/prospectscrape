import bs4
import pandas
import requests

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

def main():
    url = 'http://www.eliteprospects.com/league_central.php'
    scrape_league_ids(url, 'league_page.txt')

if __name__ == '__main__':
    main()

        

    



