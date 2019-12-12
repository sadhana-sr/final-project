import requests
import json
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






'////////////////////////GOODREADS STUFF BELOW////////////////////////////////////////////////////////'


def update_books(cur, conn):
    '''This function grabs 20 book titles and authors from NYT API and adds it to the cache.
        Then it adds it to the Books table in the database'''

    key_word_entries = 0
    book_entries = 0

    
    key = 'LULfKyQLZp6nERnrISvzNj732a3fX3te'
    request_url = "https://api.nytimes.com/svc/books/v3/lists/names.json?api-key=LULfKyQLZp6nERnrISvzNj732a3fX3te"
    #send request to API and get response (a string)
    response = requests.get(request_url)
    x = json.loads(response.text)
    #get the array of dictionaries
    results = x["results"]


    
    num_data = 0

    len_results = len(results)
    random_list = random.randrange(0, len_results)
    
    #pick one random list
    result = results[random_list]
    lst_name = result['list_name']
    oldest_date =result['oldest_published_date']
    split_old = oldest_date.split('-')
    old_year = split_old[0]
    newest_date = result['newest_published_date']
    # generate a random year for date
    split_new = newest_date.split('-')
    new_year = split_new[0]
    if old_year == new_year:
        year = old_year
    else:
        year = random.randrange(int(old_year), int(new_year))
    date = str(year)+"-05-15"
        
    #get the list data (returns the books on the best sellers list)
    new_request_url_base = "https://api.nytimes.com/svc/books/v3/lists/{}/{}.json?api-key={}"
    new_request_url = new_request_url_base.format(date, lst_name, key)
    response = requests.get(new_request_url)
    k = json.loads(response.text)
            
    #book_results is a dictionary
    book_results = k['results']
    

    #if no books in list (error)
    if len(book_results) == 0:
        #try again
        update_books(cur, conn)





    #books is a list of dictionaries
    books = book_results["books"]        
    num_books = 0
            
    key_word_entries = 0
    book_entries = 0
    while key_word_entries + book_entries < 12:
        repeat = False
        book = books[num_books]
     
        title = book['title']
        author = book['author']

        #check to see if book already in table
        cur.execute('SELECT * FROM Books')
        for row in cur:
            #if the book is already in the table, move to the next book
            if row[1] == title:
                repeat = True
                break

        if repeat == True:
            num_books+=1
            continue
                
                
                
        #get a list of 5 keywords for book
        keywords = get_book_info_goodreads(title, author)
                
                
                
        if keywords == -1:
            num_books += 1
            continue
        if len(keywords) < 5:
            num_books += 1
            continue

        
        #add the list of keywords to the keywords table
        add_to_key_words_table(keywords, cur, conn)
        key_word_entries += 5
                
                
               

        #add book title, author, and 6 keyword ids to book table
        add_to_books_table(title, author, keywords, cur, conn)
        book_entries += 1

        #checks if we reached 18 entries. If we did, returns to main. If not, move onto the next book
        #if key_word_entries + book_entries == 18:
            #print(key_word_entries + book_entries)
            #print("Finished")
            #return
        #else:
        num_books += 1
    print(key_word_entries+book_entries)
        
    

            

def get_book_info_goodreads(title, author):
    '''
    this function takes a book and retrieves the top 3 lists and top 3 words from the summary from GoodReads. 
    Returns top 6 key words for the book.
    '''
    key = "4UtmU3WvD5cXnOQvZdoTw"
    format = 'xml'
    _author = ""
    for char in author:
        if char != ' ':
            _author+=char
        else:
            _author+='+'
    _title = ""
    for char in title:
        if char != ' ':
            _title+=char
        else:
            _title+='+'

    
    base_url = "https://www.goodreads.com/book/title.{}?author={}&key={}&title={}"
    request_url = base_url.format(format, _author, key, _title)
    response = requests.get(request_url)
    content = response.content

    
    shelves = []
    root = ET.fromstring(content)

    top_five_words = []
    txt = True
    word_dict = {}

    for tag in root.iter('description'):
            text = tag.text
            if text == None:
                #sometimes goodreads only uses the title for book info. Try the API call with only the title if it doesn't work the first time
                base_url = "https://www.goodreads.com/book/title.{}?&key={}&title={}"
                request_url = base_url.format(format, key, _title)
                response = requests.get(request_url)
                content = response.content
                root = ET.fromstring(content)
                
    #if found, DO THIS
    if '<Element \'error\'' in str(root):
        return -1
    else:
        #description
        for tag in root.iter('description'):
            text = tag.text
            if text == None:
                txt = False
            else:
                text = text.lower()
                split_text = text.split()
                
                for word in split_text:
                    if len(word) > 3 and word.find("th")==-1 and word.find('wo')==-1 and word.find('does')==-1 and word.find('wh')==-1 and word.find('=')==-1:
                        if word.find(','):
                            word = word.strip(',')
                        if word.find('.'):
                            word = word.strip('.')
                        if word.find('<b>'):
                            word = word.strip('<b>')
                        if word.find('</b>'):
                            word = word.strip('</b>')
                        if word.find('<i>'):
                            word = word.strip('<i>')
                        if word.find('</i>'):
                            word = word.strip('</i>')
                        if word.find('<b'):
                            word = word.strip('<b')
                        if word != '' and len(word)> 3:
                            word_dict[word] = word_dict.get(word, 0) + 1
        sorted_dict = sorted(word_dict.items(), key=lambda x: x[1], reverse=True)
                
       
        


        #shelves
        for tag in root.iter('shelf'):
            shelf = tag.attrib['name']
            author_split = author.split()
            first = author_split[0].lower()
            last = author_split[-1].lower()
            if "read" not in shelf and "book" not in shelf and "own" not in shelf and "kindle" not in shelf and "library" not in shelf and "buy" not in shelf and shelf.find("fav") == -1 and shelf.find('audi') == -1 and shelf.find(first) == -1 and shelf.find(last) == -1 and shelf.find('release') == -1 and shelf.find('stars') == -1 and shelf.find('20')==-1 and shelf.find('shelf')==-1 and shelf.find('dnf')==-1 and shelf.find('tbr')==-1 and shelf.find('finish')==-1 and "series" not in shelf and "standalone" not in shelf and "author" not in shelf and shelf.find("fiction")==-1 and shelf.find('adult') == -1 and shelf.find('ya')==-1: 
                shelves.append(shelf)
        
    
        
        # in the case of no description, take all words from shelves
        if txt == True:
            
            top_two_tup = sorted_dict[0:2]
            top_three_shelves= shelves[0:3]
        
        
        
            
            
        else:
            if len(shelves) > 5:
                top_five_words = shelves[0:5]
                return top_five_words
            else:
                return -1

        
        #check if there are 2 words in word_dict
            #if there aren't enough descrip words
        if len(top_two_tup) < 2:
            #then take all 5 from shelves
            if len(shelves) >=5:
                top_five_words = shelves[0:5]
            #if there arent enough shelves or descrip words
            else:
                return -1
            
        #if there arent enough shelves
        if len(top_three_shelves) < 3:
            #if there are enough descip words then take all 5 
            if len(sorted_dict) >=5:
                all_words= []
                    
                for tup in sorted_dict:
                    all_words.append(tup[0])
                top_five_words = all_words[0:5]
                
                #if there arent enough shelves or descrip words
            else:
                return -1

                
        #if there is enough descrip words and shevles
        
        top_two_words = []
        for tup in top_two_tup:
            top_two_words.append(tup[0])

        top_five_words = top_two_words + top_three_shelves


         #return list of key words 
    
    return top_five_words



def check_book_table(title, author, cur, conn):
    cur.execute('SELECT * FROM Books')
    title = title.upper()
    for row in cur:
        if title == row[1] and author == row[2]:
            return True
        
    return False
            

def setUpBooksTable(cur, conn):
     # create Books table if it doesn't already exist
    cur.execute('CREATE TABLE IF NOT EXISTS Books(book_id INT PRIMARY KEY, title TEXT, author TEXT, w_id1 INT,w_id2 INT,w_id3 INT,w_id4 INT,w_id5 INT)')
    #save table
    conn.commit()


def setUpKeyWordsTable(cur,conn):
    #create keyWords table if it doesn't already exist
    cur.execute('CREATE TABLE IF NOT EXISTS KeyWords(id INTEGER PRIMARY KEY, title TEXT)')
    conn.commit()


def add_to_key_words_table(category_list, cur, conn):
    #update keywords table
    

    #insert each word into the table 
    for word in category_list:
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
        if word not in table_list:
            cur.execute("INSERT INTO KeyWords (id,title) VALUES (?,?)",(i,word))

    
    conn.commit()


def add_to_books_table(title, author, words, cur, conn):

    #count how many books are already in the table
    count = 0
    cur.execute('SELECT * FROM Books')
    for row in cur:
        count += 1

    #next book will be one over the number in the table
    book_id = count + 1
    
    
    lst_key_ids = []

    #retrieve the ids for every key word and append to lst_key_ids
    for word in words:
        cur.execute('SELECT id FROM KeyWords WHERE title = ?', (word, ))

        for row in cur:
            word_id = row[0]
            word_id = int(word_id)
            lst_key_ids.append(word_id)
    

    #insert the book's id, title, author, and all 6 keyword ids from lst_key_ids
    cur.execute('INSERT INTO Books(book_id, title, author, w_id1, w_id2, w_id3, w_id4, w_id5) VALUES(?,?,?,?,?,?,?,?)', (book_id, title, author, lst_key_ids[0], lst_key_ids[1], lst_key_ids[2], lst_key_ids[3], lst_key_ids[4]))

    conn.commit()

def retrieve_kw_ids_from_book_table(title, cur, conn):
    title = title.upper()
    #first join
    key_word_lst = []
    cur.execute('SELECT Books.title, KeyWords.title FROM Books INNER JOIN KeyWords ON Books.w_id1=KeyWords.id WHERE Books.title = ?', (title, )) 
    for row in cur:
        if row[0] == title:
            w1 = row[1]
            key_word_lst.append(w1)
           

    #second join
    cur.execute('SELECT Books.title, KeyWords.title FROM Books INNER JOIN KeyWords ON Books.w_id2=KeyWords.id WHERE Books.title = ?', (title, ))
    for row in cur:
        if row[0] == title:
            w2 = row[1]
            key_word_lst.append(w2)
            


        
    cur.execute('SELECT Books.title, KeyWords.title FROM Books INNER JOIN KeyWords ON Books.w_id3=KeyWords.id WHERE Books.title = ?', (title, ))
    for row in cur:
        if row[0] == title:
            w3 = row[1]
            key_word_lst.append(w3)
            
        

    cur.execute('SELECT Books.title, KeyWords.title FROM Books INNER JOIN KeyWords ON Books.w_id4=KeyWords.id WHERE Books.title = ?', (title, ))
    for row in cur:
        if row[0] == title:
            w4 = row[1]
            key_word_lst.append(w4)
           

    cur.execute('SELECT Books.title, KeyWords.title FROM Books INNER JOIN KeyWords ON Books.w_id5=KeyWords.id WHERE Books.title = ?', (title, ))
    for row in cur:
        if row[0] == title:
            w5 = row[1]
            key_word_lst.append(w5)
         
    print(key_word_lst)
    return key_word_lst





    
'///////////////////////////////////SPOTIFY STUFF BELOW///////////////////////////////////////////////'



            
token = util.oauth2.SpotifyClientCredentials(client_id = '1ad705cfee3548b9950efb26b457a33e', client_secret = '3a4c9fe4f00542d9816b25148a035664')
cache_token = token.get_access_token()
spotify = spotipy.Spotify(cache_token) 


scope = 'user-read-private'


# OAuth Token: BQBtKFbRuaS9serMaqntRrYdrML59kodnuCCsdNyjLg5LHrJudK9Gs6wFz1BLWOtJO5_IEb02hIfH8oYwg5ulXOpxnZCCVYDP8XFbujAPPzKJgiuyQOZzAzkP4mQPOj-0X2UBDKLcSYk7tT67Hew6l0eg8n0Gq4BpEhVROBY0a-wtmmTRjHtROLcioyNfI5g5FoROkYOI5smU6dWHBiijFSiuACBmEQCjDoORgpG_Ny42p5K2dDsAf9aA90xd7MG2S-pVh1Xpw
# API Key RandomWords: 3f40650948mshfb87ef8f6e80f48p16ef22jsnf380814b03c7
url = "https://api.spotify.com/v1/search"
scope = 'user-library-read'

def write_song_table(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Songs (id INTEGER PRIMARY KEY, Title TEXT, word TEXT, artist_id INTEGER)")
    conn.commit()

def write_artist_table(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Artists (artist_id INTEGER PRIMARY KEY, Artist TEXT)")
    conn.commit()


def update_songs(cur, conn):
    #get a random word from rand word generator
    r = RandomWords()
    rw = r.get_random_word()

    #plug word into spotify and update tables
    get_artists(rw, cur, conn)
    get_songs(rw, cur, conn)


def get_artists(keyword, cur, conn):
    
    if len(sys.argv) > 1:
        search_str = sys.argv[1]
    else:
        search_str = keyword

    result = spotify.search(search_str, limit=2)
    

    items =  result['tracks']['items']


    artist_list = []
    table_list = []
    
    count = 0

    #count how many artists ae in the table currently
    cur.execute('SELECT * FROM Artists')
    for row in cur:
        count += 1
        table_list.append(row[1])

        
    artist_id = count + 1
    
    for item in items:
        artist = item['artists'][0]['name']
        
        artist_list.append(artist)

        
        if artist not in artist_list:

    #try:
            cur.execute("INSERT OR IGNORE INTO Artists (artist_id, Artist) VALUES (?,?)",(artist_id,artist))
            artist_id += 1
            conn.commit() 
        #except:
    #        print("failed")
        #cur.execute('SELECT Artists.Artist, Songs.Title FROM Artists JOIN Songs ON Artists.artist_id = Songs.artist_id WHERE Songs.artist_id = (?)', (artist_id, ))

    


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
    count = 0
    
    
   

    for item in items:
        table_list = []
        title = item['name']
        artist = item['artists'][0]
        artist = artist['name']

        artist_list = []
        cur.execute('SELECT * FROM Songs')
        for row in cur:
            table_list.append(row[1])
        
        song_id = len(table_list) + 1
        if title in table_list:
            continue

        else:

            #count how many artists are in the table currently
            cur.execute('SELECT * FROM Artists')
            for row in cur:
                artist_list.append(row[1])

        
            artist_id = len(artist_list) + 1

        
            if artist not in artist_list:

                cur.execute("INSERT INTO Artists (artist_id, Artist) VALUES (?,?)",(artist_id,artist))

                conn.commit() 



            artist_ids = []
            cur.execute('SELECT artist_id FROM Artists WHERE Artist = ?', (artist, ))
            for row in cur:
                art_id = int(row[0])
            
                artist_ids.append(art_id)


           # print(song_id)
           # print(title)
            
            cur.execute('INSERT INTO Songs(id, Title, word, artist_id ) VALUES(?,?,?,?)', (song_id, title, keyword, artist_ids[0]))
            
                
            cur.execute('SELECT Songs.Title, Artists.Artist FROM Artists INNER JOIN Songs ON Songs.artist_id = Artists.artist_id WHERE Songs.artist_id = ?', (artist_id,))

                #artist_id += 1
                #song_id += 1
            count += 1   
            if count % 20:
                time.sleep(5)

            conn.commit()
        
   
    
    
    
        
    


'///////////////////////////////////////// MAIN //////////////////////////////////////////////////////////'


def main():

    #connect to database
    cur, conn = connectDatabase('booksandsongs.db')

    #set up tables if they don't already exist
    setUpKeyWordsTable(cur, conn)
    setUpBooksTable(cur, conn)
    write_song_table(cur, conn)
    write_artist_table(cur, conn)
    

    #for noun in nouns:
    #    get_songs(noun, cur, conn)

    #update tables

    #update_books(cur, conn)

    #update_songs(cur, conn)




    #keywords list
    key_words = []

    #songs list
    songs_list = []

    found = False
    while found == False:
        title = input("Please enter the name of a book: ")
        author = input("Please enter the first and last name of the author of the book: ")
        #check if book is in database
        status = check_book_table(title, author, cur, conn)
        if status == True:
            print('Fetching from database')
            #get list of keywords
            key_words = retrieve_kw_ids_from_book_table(title, cur, conn)
        #if not, call via API and store in database
        else:
            print('Fetching from Goodreads')
            key_words = get_book_info_goodreads(title, author)
            if key_words != -1:
                found = True
                #store keywords into table
                add_to_key_words_table(key_words, cur, conn)
                add_to_books_table(title.upper(), author, key_words, cur, conn)
                print('successfully stored into database')
            else:
                print("Book not found. Please check for any typos in the title and author or enter a new book")
        #print recommeneded songs
        for word in key_words:
            get_songs(word, cur, conn)
            
        
        #print("Here are our recommended songs:")
        #for song in songs_list:
            #print(song)


if __name__ == "__main__":
    main()
