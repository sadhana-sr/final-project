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

def first_calc(cur, conn):
#This function calculates out how many words are associated with each artist
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
#This function finds out how many words are associated with how many songs

    d = {}
    cur.execute('SELECT Books.w_id1, KeyWords.title FROM Books INNER JOIN KeyWords ON Books.w_id1=KeyWords.id') 
    for row in cur:
        if row[1] not in d:
            d[row[1]] = 1
        else:
            d[row[1]] += 1

        #second join
    cur.execute('SELECT Books.w_id2, KeyWords.title FROM Books INNER JOIN KeyWords ON Books.w_id2=KeyWords.id')
    for row in cur:
        if row[1] not in d:
            d[row[1]] = 1                
        else:
            d[row[1]] += 1

            
    cur.execute('SELECT Books.w_id3, KeyWords.title FROM Books INNER JOIN KeyWords ON Books.w_id3=KeyWords.id')
    for row in cur:
        if row[1] not in d:
            d[row[1]] = 1                
        else:
            d[row[1]] += 1

    cur.execute('SELECT Books.w_id4, KeyWords.title FROM Books INNER JOIN KeyWords ON Books.w_id4=KeyWords.id')
    for row in cur:
        if row[1] not in d:
            d[row[1]] = 1            
        else:
            d[row[1]] += 1

    cur.execute('SELECT Books.w_id5, KeyWords.title FROM Books INNER JOIN KeyWords ON Books.w_id5=KeyWords.id')
    for row in cur:
        if row[1] not in d:
            d[row[1]] = 1
        else:
            d[row[1]] += 1

    #print(d)
    return d



def graph_1(dictionary):
    pass

    
    sorted_dictionary = {k: v for k, v in sorted(dictionary.items(), key=lambda item: item[1])}
    first_thirty =  {k: sorted_dictionary[k] for k in list(sorted_dictionary)[-30:]}
    # Use these to make sure that your x axis labels fit on the page
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.ylim((0,6))
    
    x_values = first_thirty.keys()
    y_values = first_thirty.values()
    plt.xlabel('Artist')
    plt.ylabel('# of Words')
    plt.title('Number of Words Associated with Each Artist')
    plt.bar(x_values, y_values, color='pink')

    plt.show() 


def histogram(cur, conn):
    
    artists = []
    cur.execute('SELECT Songs.artist_id, Artists.Artist FROM Songs INNER JOIN Artists ON Songs.artist_id = Artists.artist_id')
    for artist_id in cur:
        artists.append(artist_id[0])
    print(artists)

    plt.xticks(rotation=90)
    plt.xlabel('Number of Words')
    plt.ylabel('Frequency')
    plt.title('Frequency of Words per Artist')
    plt.hist(artists, rwidth= 1, color = '#c0f7fa', edgecolor = '#ddcfc1', linewidth = 2)
    plt.show()



def graph_2(dictionary):
    pass

    
    #print(dictionary)
    # Use these to make sure that your x axis labels fit on the page
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.ylim((0,20))
    
    first_hundred =  {k: dictionary[k] for k in list(dictionary)[:100]}
   
    
    x_values = first_hundred.keys()
    y_values = first_hundred.values()
    plt.xlabel('Word')
    plt.ylabel('# of Occurences')
    plt.title('Number of Artists that Each Word Yields')
    plt.xticks(fontsize = 5)
    plt.bar(x_values, y_values, color=['purple', 'pink', 'red', 'orange', 'yellow'])


    plt.show() 


def main():

    #connect to database
    cur, conn = connectDatabase('booksandsongs.db')
    
    x = first_calc(cur, conn)
    y = second_calc(cur, conn)



    
    
    graph_1(x)
    graph_2(y)
    second_calc(cur, conn)
    histogram(cur, conn)



    with open('booksandsongs.csv', 'w') as f:  
        w = csv.DictWriter(f, x.keys())
        w.writeheader()
        w.writerow(x)
        


if __name__ == "__main__":
    main()
