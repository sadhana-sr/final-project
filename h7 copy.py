import requests
import json
import unittest
import os
import spotipy
import sys
import spotipy.util as util
import sqlite3
from random_word import RandomWords


token = util.oauth2.SpotifyClientCredentials(client_id = '1ad705cfee3548b9950efb26b457a33e', client_secret = '3a4c9fe4f00542d9816b25148a035664')
cache_token = token.get_access_token()
spotify = spotipy.Spotify(cache_token) 


scope = 'user-read-private'


#
# Your name: Sadhana Ramaseshadri
# Who you worked with:
# OAuth Token: BQBtKFbRuaS9serMaqntRrYdrML59kodnuCCsdNyjLg5LHrJudK9Gs6wFz1BLWOtJO5_IEb02hIfH8oYwg5ulXOpxnZCCVYDP8XFbujAPPzKJgiuyQOZzAzkP4mQPOj-0X2UBDKLcSYk7tT67Hew6l0eg8n0Gq4BpEhVROBY0a-wtmmTRjHtROLcioyNfI5g5FoROkYOI5smU6dWHBiijFSiuACBmEQCjDoORgpG_Ny42p5K2dDsAf9aA90xd7MG2S-pVh1Xpw
# API Key RandomWords: 3f40650948mshfb87ef8f6e80f48p16ef22jsnf380814b03c7
url = "https://api.spotify.com/v1/search"
scope = 'user-library-read'





#function that uses api to get key word
#call it once, get word, plug in, 

#put artist into artist table
#song table plugin id and title
# if sia ID is 2 in song table, then you can trace it back to song table, and then get artist

def update_songs():
    #get a random word from rand word generator
    r = RandomWords()
    r.get_random_word()
    #plug word into spotify and get list of songs

    #call the table functions






def get_songs(keyword):
    
    if len(sys.argv) > 1:
        search_str = sys.argv[1]
    else:
        search_str = keyword

    result = spotify.search(search_str)
    titles = []
    items =  result['tracks']['items']
    for item in items:
        titles.append(item['name'])
    return titles

def get_artists(keyword):
    
    if len(sys.argv) > 1:
        search_str = sys.argv[1]
    else:
        search_str = keyword

    result = spotify.search(search_str)
    artists = []
    items =  result['tracks']['items']
    for item in items:
        artists.append(item['artists'][0]['name'])
    return artists





#database functions



def connectDatabase(db_name):
    # connect to database
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn



def write_song_table(db_filename, cur, conn):
    
    cur.execute("CREATE TABLE IF NOT EXISTS Songs (id INTEGER PRIMARY KEY, Title TEXT, artist_id INT)")
    cur.commit()


def insert_song_table(song_list, artist_list, cur, conn):

    #count how many songs are already in the table
    count = 0
    cur.execute('SELECT * FROM Songs')
    for row in cur:
        count += 1

    #next book will be one over the number in the table
    song_id = count + 1
    
    
    lst_artist_ids = []
    lst_song_names = []

    #retrieve the ids for every artist and append to lst_key_ids
    for artist in artist_list:
        cur.execute('SELECT id FROM Artists WHERE Artist = ?', (artist, ))

        for row in cur:
            artist_id = row[0]
            artist_id = int(artist_id)
            lst_artist_ids.append(artist_id)
    x = 0
    for song in song_list:
        cur.execute('INSERT INTO Songs(id, Title, artist_id) VALUES(?,?,?)', (song_id, song_list[x], lst_artist_ids[x])
        song_id+=1
        x = 0
    
    conn.commit()
    
def insert_artist_table(artist_list, cur, conn):
     for artist in artist_list:
        #count how many items are in the table already and check for any potential keyword duplicates
        cur.execute('SELECT * FROM KeyWords')
        table_list = []
        count = 0
        for row in cur:
            count += 1
            table_list.append(row[1])
        #count = there are this many books


        #id is one above the number of items in the table
        i = count + 1
        if artist not in table_list:
            cur.execute("INSERT INTO Artists (id, Artist) VALUES (?,?)",(i,artist))
        
        
        conn.commit()



def write_artist_table(db_filename):
    
    cur.execute("CREATE TABLE IF NOT EXISTS Artists (id INTEGER PRIMARY KEY, Artist TEXT)")
    cur.commit()
#function that updates table with 20

#------------------------------------------------------------------------------------------
def main():
    '''
    # Get the cached data for BRA
    print("This should use the cache")
    songs = get_songs('word')
    artists = get_artists('word')
    print(songs)
    print(artists)
    
    print("------------")

    print("CACHING")
    CACHE_FNAME = 'cache_tracks.json' 
    cache_dictionary = read_cache(CACHE_FNAME)
    write_cache(CACHE_FNAME, songs)
    write_cache(CACHE_FNAME, artists)

    write_title_table('songs.db')
    insert_title_table('songs.db')
    write_id_table('songs.db')
 

    # You can comment this out to test with just the main, but be sure to uncomment it and test
    # with unittest as well.
    unittest.main(verbosity=2)
    print("------------")
    '''


update_songs()

if __name__ == "__main__":
    main()
