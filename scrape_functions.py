import os, sys
import time
import json
from random import randint
import requests
import bs4
import pandas as pd

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
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(r.text)
