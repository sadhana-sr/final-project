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


def connectDatabase(db_name):
    # connect to database
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


def write_song_table(db_filename, cur, conn):
    
    cur.execute("CREATE TABLE IF NOT EXISTS Songs (id INTEGER PRIMARY KEY, Title TEXT, word TEXT, artist_id INTEGER)")
    conn.commit()

def write_artist_table(db_filename, cur, conn):
    
    cur.execute("CREATE TABLE IF NOT EXISTS Artists (artist_id INTEGER PRIMARY KEY, Artist TEXT)")
    conn.commit()

def get_artists(keyword, cur, conn):
    
    if len(sys.argv) > 1:
        search_str = sys.argv[1]
    else:
        search_str = keyword

    result = spotify.search(search_str, limit=2)
    

    items =  result['tracks']['items']

    #artist_id = 0
    artist_list = []
    table_list = []
    for item in items:
        artist = item['artists'][0]['name']
        
        artist_list.append(artist)

        count = 0
        cur.execute('SELECT * FROM Artists')
        for row in cur:
            count += 1
            table_list.append(row[1])

            artist_id = count + 1
            if artist not in table_list:

    #try:
                cur.execute("INSERT OR IGNORE INTO Artists (artist_id, Artist) VALUES (?,?)",(artist_id,artist))
        #except:
    #        print("failed")
        #cur.execute('SELECT Artists.Artist, Songs.Title FROM Artists JOIN Songs ON Artists.artist_id = Songs.artist_id WHERE Songs.artist_id = (?)', (artist_id, ))

    conn.commit() 

def get_songs(keyword, cur, conn):
    
    if len(sys.argv) > 1:
        search_str = sys.argv[1]
    else:
        search_str = keyword

    result = spotify.search(search_str, limit=2)

    items =  result['tracks']['items']
    song_id = 0
    artist_id = 0
    songs_list = []
    table_list = []
    for item in items:
        title = item['name']
        songs_list.append(title)

        count = 0
        cur.execute('SELECT * FROM Songs')
        for row in cur:
            count += 1
            table_list.append(row[1])


            artist_id = count + 1
            if title not in table_list:
                artist_id = cur.execute('SELECT artist_id FROM Artists WHERE title = ?', (title, ))

                cur.execute('INSERT OR IGNORE INTO Songs(id, Title, word, artist_id ) VALUES(?,?,?,?)', (song_id, title, keyword, artist_id ))
                cur.execute('SELECT Artists.Artist, Songs.Title FROM Artists INNER JOIN Songs ON Songs.artist_id = Artists.artist_id WHERE Songs.artist_id = ?', (artist_id,))

        
    conn.commit()
   

def update_songs(cur, conn):
    #get a random word from rand word generator
    r = RandomWords()
    rw = r.get_random_word()

    #plug word into spotify and get list of songs
    get_artists(rw, cur, conn)
    get_songs(rw, cur, conn)
    
    #return rand_songs
    #call the table functions

    


#songs and artists(3 tables)



#function that updates table with 20




#------------------------------------------------------------------------------------------
def main():
    
    # Get the cached data for BRA
    
    
    (cur, conn) = connectDatabase('spo.db')

    write_song_table('spo.db', cur, conn)  
    write_artist_table('spo.db', cur, conn)  
    
    update_songs(cur, conn)
    


    #print("Here are our recommended songs:")
    #s = get_songs(keyword, cur, conn)
    #for i in s:
     #   print(i[1] + " by " + i[0])



    #songs = get_songs(word)
    #artists = get_artists(word)
    #print(songs)
    #print(artists)
    
    print("------------")
 
    # You can comment this out to test with just the main, but be sure to uncomment it and test
    # with unittest as well.
    unittest.main(verbosity=2)
    print("------------")
    




if __name__ == "__main__":
    main()

    #in song table have another column with the word given from 
    #pass it into update song table
    #put that in