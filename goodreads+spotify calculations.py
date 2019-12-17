import requests
import csv
import unittest
import string
import sqlite3
import os
import random
import xml.etree.ElementTree as ET
import time
import spotipy
import sys
from random_word import RandomWords
import spotipy.util as util

#
# Names: Katie Huang and Sadhana Ramaseshadri
# 
#


'///////////////////////CONNECT TO DATABASE/////////////////////////////////////////////////////////////'
def connectDatabase(db_name):
    # connect to database
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn
def words(cur, conn):
    #dictionary of frequency of words
    d = {}
    cur.execute('SELECT Songs.artist_id, Artists.Artist FROM Songs INNER JOIN Artists ON Songs.artist_id = Artists.artist_id')
    for artist_id in cur:
        if artist_id not in d:
            d[artist_id] = 1
        else:
            d[artist_id] += 1
    return d

#join artist table and song table
#top 20 words 


def main():

    #connect to database
    cur, conn = connectDatabase('booksandsongs.db')
    
    x = words(cur, conn)
    print(x)


    with open('booksandsongs.csv', 'w') as f:  # Just use 'w' mode in 3.x
        w = csv.DictWriter(f, x.keys())
        w.writeheader()
        w.writerow(x)
    #y = json.dumps(w)
    #print(y)
    
    

if __name__ == "__main__":
    main()
