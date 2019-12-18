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
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
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
        if artist_id[1] not in d:
            d[artist_id[1]] = 1
        else:
            d[artist_id[1]] += 1
    return d

#join artist table and song table
#top 20 words 


def second_calc(cur, conn):

    d = {}
    cur.execute('SELECT Books.w_id1, KeyWords.title FROM Books INNER JOIN KeyWords ON Books.w_id1=KeyWords.id') 
    for row in cur:
        if row[0] not in d:
            d[row[0]] = 1
        else:
            d[row[0]] += 1

        #second join
    cur.execute('SELECT Books.w_id2, KeyWords.title FROM Books INNER JOIN KeyWords ON Books.w_id2=KeyWords.id')
    for row in cur:
        if row[0] not in d:
            d[row[0]] = 1                
        else:
            d[row[0]] += 1

            
    cur.execute('SELECT Books.w_id3, KeyWords.title FROM Books INNER JOIN KeyWords ON Books.w_id3=KeyWords.id')
    for row in cur:
        if row[0] not in d:
            d[row[0]] = 1                
        else:
            d[row[0]] += 1

    cur.execute('SELECT Books.w_id4, KeyWords.title FROM Books INNER JOIN KeyWords ON Books.w_id4=KeyWords.id')
    for row in cur:
        if row[0] not in d:
            d[row[0]] = 1            
        else:
            d[row[0]] += 1

    cur.execute('SELECT Books.w_id5, KeyWords.title FROM Books INNER JOIN KeyWords ON Books.w_id5=KeyWords.id')
    for row in cur:
        if row[0] not in d:
            d[row[0]] = 1
        else:
            d[row[0]] += 1

    print(d)
    return d



def graph_1(dictionary):
    pass

    
    print(dictionary)
    # Use these to make sure that your x axis labels fit on the page
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.ylim((0,25))
    
    x_values = dictionary.keys()
    y_values = dictionary.values()
    plt.xlabel('Artist')
    plt.ylabel('# of Words')
    plt.title('Number of Words Associated with Each Artist')
    plt.bar(x_values, y_values, color='orange')

    plt.show() 


def graph_2(dictionary):
    pass

    
    print(dictionary)
    # Use these to make sure that your x axis labels fit on the page
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.ylim((0,25))
    
    x_values = dictionary.keys()
    y_values = dictionary.values()
    plt.xlabel('Artist')
    plt.ylabel('# of Words')
    plt.title('Number of Words Associated with Each Artist')
    plt.bar(x_values, y_values, color='green')

    plt.show() 


def main():

    #connect to database
    cur, conn = connectDatabase('booksandsongs.db')
    
    x = words(cur, conn)
    y = second_calc(cur, conn)


    with open('booksandsongs.csv', 'w') as f:  # Just use 'w' mode in 3.x
        w = csv.DictWriter(f, x.keys())
        w.writeheader()
        w.writerow(x)

    
    
    #graph_1(x)
    graph_2(y)
    second_calc(cur, conn)

if __name__ == "__main__":
    main()
