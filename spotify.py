import requests
import json
import unittest
import os
import spotipy
import sys
import spotipy.util as util
import sqlite3


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


def read_cache(CACHE_FNAME):
    """
    This function reads from the JSON cache file and returns a dictionary from the cache data. 
    If the file doesn’t exist, it returns an empty dictionary.
    """

    try:
        cache_file = open(CACHE_FNAME, 'r', encoding="utf-8") # Try to read the data from the file
        cache_contents = cache_file.read()  # If it's there, get it into a string
        CACHE_DICTION = json.loads(cache_contents) # And then load it into a dictionary
        cache_file.close() # Close the file, we're good, we got the data in a dictionary.
    except:
        CACHE_DICTION = {}
    
    return CACHE_DICTION

def write_cache(CACHE_FNAME, cache_dict):
    """
    This function encodes the cache dictionary (cache_dict) into JSON format and
    writes the contents in the cache file (cache_file) to save the search results.
    """
    pass
    cd = json.dumps(cache_dict)
    
    cf = open(CACHE_FNAME, "w")
    cf.write(cd)
    cf.close()
    print(cf)


#function that uses api to get key word
#call it once, get word, plug in, 

#put artist into artist table
#song table plugin id and title
# if sia ID is 2 in song table, then you can trace it back to song table, and then get artist

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

def write_title_table(db_filename):
    
    conn = sqlite3.connect(db_filename)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS Spotify (Title TEXT, Artist TEXT, artist_id INT)")


def insert_title_table(db_filename):
    conn = sqlite3.connect(db_filename)
    cur = conn.cursor()
    songs = get_songs('word')

    for song in songs:
        cur.execute("INSERT INTO Spotify(Title) VALUES(?)",song)
    conn.commit()
    


def write_id_table(db_filename):
    
    conn = sqlite3.connect(db_filename)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS Artists (Artist TEXT, artist_id INT)")
 
#function that updates table with 20

#------------------------------------------------------------------------------------------

def main():
    
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


if __name__ == "__main__":
    main()

