import requests
import json
import unittest
import string
import sqlite3
import os
import random
import xml.etree.ElementTree as ET

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


            print(song_id)
            print(title)
            
            cur.execute('INSERT INTO Songs(id, Title, word, artist_id ) VALUES(?,?,?,?)', (song_id, title, keyword, artist_ids[0]))
            
                
            cur.execute('SELECT Songs.Title, Artists.Artist FROM Artists INNER JOIN Songs ON Songs.artist_id = Artists.artist_id WHERE Songs.artist_id = ?', (artist_id,))

                #artist_id += 1
                #song_id += 1
                
                

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
    

    
    nouns = [
        'people',
        'history',
        'way',
        'art',
        'world',
        'information',
        'map',
        'two',
        'family',
        'government',
        'health',
        'system',
        'computer',
        'meat',
        'year',
        'thanks',
        'music',
        'person',
        'reading',
        'method',
        'data',
        'food',
        'understanding',
        'theory',
        'law',
        'bird',
        'literature',
        'problem',
        'software',
        'control',
        'knowledge',
        'power',
        'ability',
        'economics',
        'love',
        'internet',
        'television',
        'science',
        'library',
        'nature',
        'fact',
        'product',
        'idea',
        'temperature',
        'investment',
        'area',
        'society',
        'activity',
        'story',
        'industry',
        'media',
        'thing',
        'oven',
        'community',
        'definition',
        'safety',
        'quality',
        'development',
        'language',
        'management',
        'player',
        'variety',
        'video',
        'week',
        'security',
        'country',
        'exam',
        'movie',
        'organization',
        'equipment',
        'physics',
        'analysis',
        'policy',
        'series',
        'thought',
        'basis',
        'boyfriend',
        'direction',
        'strategy',
        'technology',
        'army',
        'camera',
        'freedom',
        'paper',
        'environment',
        'child',
        'instance',
        'month',
        'truth',
        'marketing',
        'university',
        'writing',
        'article',
        'department',
        'difference',
        'goal',
        'news',
        'audience',
        'fishing',
        'growth',
        'income',
        'marriage',
        'user',
        'combination',
        'failure',
        'meaning',
        'medicine',
        'philosophy',
        'teacher',
        'communication',
        'night',
        'chemistry',
        'disease',
        'disk',
        'energy',
        'nation',
        'road',
        'role',
        'soup',
        'advertising',
        'location',
        'success',
        'addition',
        'apartment',
        'education',
        'math',
        'moment',
        'painting',
        'politics',
        'attention',
        'decision',
        'event',
        'property',
        'shopping',
        'student',
        'wood',
        'competition',
        'distribution',
        'entertainment',
        'office',
        'population',
        'president',
        'unit',
        'category',
        'cigarette',
        'context',
        'introduction',
        'opportunity',
        'performance',
        'driver',
        'flight',
        'length',
        'magazine',
        'newspaper',
        'relationship',
        'teaching',
        'cell',
        'dealer',
        'debate',
        'finding',
        'lake',
        'member',
        'message',
        'phone',
        'scene',
        'appearance',
        'association',
        'concept',
        'customer',
        'death',
        'discussion',
        'housing',
        'inflation',
        'insurance',
        'mood',
        'woman',
        'advice',
        'blood',
        'effort',
        'expression',
        'importance',
        'opinion',
        'payment',
        'reality',
        'responsibility',
        'situation',
        'skill',
        'statement',
        'wealth',
        'application',
        'city',
        'county',
        'depth',
        'estate',
        'foundation',
        'grandmother',
        'heart',
        'perspective',
        'photo',
        'recipe',
        'studio',
        'topic',
        'collection',
        'depression',
        'imagination',
        'passion',
        'percentage',
        'resource',
        'setting',
        'ad',
        'agency',
        'college',
        'connection',
        'criticism',
        'debt',
        'description',
        'memory',
        'patience',
        'secretary',
        'solution',
        'administration',
        'aspect',
        'attitude',
        'director',
        'personality',
        'psychology',
        'recommendation',
        'response',
        'selection',
        'storage',
        'version',
        'alcohol',
        'argument',
        'complaint',
        'contract',
        'emphasis',
        'highway',
        'loss',
        'membership',
        'possession',
        'preparation',
        'steak',
        'union',
        'agreement',
        'cancer',
        'currency',
        'employment',
        'engineering',
        'entry',
        'interaction',
        'limit',
        'mixture',
        'preference',
        'region',
        'republic',
        'seat',
        'tradition',
        'virus',
        'actor',
        'classroom',
        'delivery',
        'device',
        'difficulty',
        'drama',
        'election',
        'engine',
        'football',
        'guidance',
        'hotel',
        'match',
        'owner',
        'priority',
        'protection',
        'suggestion',
        'tension',
        'variation',
        'anxiety',
        'atmosphere',
        'awareness',
        'bread',
        'climate',
        'comparison',
        'confusion',
        'construction',
        'elevator',
        'emotion',
        'employee',
        'employer',
        'guest',
        'height',
        'leadership',
        'mall',
        'manager',
        'operation',
        'recording',
        'respect',
        'sample',
        'transportation',
        'boring',
        'charity',
        'cousin',
        'disaster',
        'editor',
        'efficiency',
        'excitement',
        'extent',
        'feedback',
        'guitar',
        'homework',
        'leader',
        'mom',
        'outcome',
        'permission',
        'presentation',
        'promotion',
        'reflection',
        'refrigerator',
        'resolution',
        'revenue',
        'session',
        'singer',
        'tennis',
        'basket',
        'bonus',
        'cabinet',
        'childhood',
        'church',
        'clothes',
        'coffee',
        'dinner',
        'drawing',
        'hair',
        'hearing',
        'initiative',
        'judgment',
        'lab',
        'measurement',
        'mode',
        'mud',
        'orange',
        'poetry',
        'police',
        'possibility',
        'procedure',
        'queen',
        'ratio',
        'relation',
        'restaurant',
        'satisfaction',
        'sector',
        'signature',
        'significance',
        'song',
        'tooth',
        'town',
        'vehicle',
        'volume',
        'wife',
        'accident',
        'airport',
        'appointment',
        'arrival',
        'assumption',
        'baseball',
        'chapter',
        'committee',
        'conversation',
        'database',
        'enthusiasm',
        'error',
        'explanation',
        'farmer',
        'gate',
        'girl',
        'hall',
        'historian',
        'hospital',
        'injury',
        'instruction',
        'maintenance',
        'manufacturer',
        'meal',
        'perception',
        'pie',
        'poem',
        'presence',
        'proposal',
        'reception',
        'replacement',
        'revolution',
        'river',
        'son',
        'speech',
        'tea',
        'village',
        'warning',
        'winner',
        'worker',
        'writer',
        'assistance',
        'breath',
        'buyer',
        'chest',
        'chocolate',
        'conclusion',
        'contribution',
        'cookie',
        'courage',
        'dad',
        'desk',
        'drawer',
        'establishment',
        'examination',
        'garbage',
        'grocery',
        'honey',
        'impression',
        'improvement',
        'independence',
        'insect',
        'inspection',
        'inspector',
        'king',
        'ladder',
        'menu',
        'penalty',
        'piano',
        'potato',
        'profession',
        'professor',
        'quantity',
        'reaction',
        'requirement',
        'salad',
        'sister',
        'supermarket',
        'tongue',
        'weakness',
        'wedding',
        'affair',
        'ambition',
        'analyst',
        'apple',
        'assignment',
        'assistant',
        'bathroom',
        'bedroom',
        'beer',
        'birthday',
        'celebration',
        'championship',
        'cheek',
        'client',
        'consequence',
        'departure',
        'diamond',
        'dirt',
        'ear',
        'fortune',
        'friendship',
        'funeral',
        'gene',
        'girlfriend',
        'hat',
        'indication',
        'intention',
        'lady',
        'midnight',
        'negotiation',
        'obligation',
        'passenger',
        'pizza',
        'platform',
        'poet',
        'pollution',
        'recognition',
        'reputation',
        'shirt',
        'sir',
        'speaker',
        'stranger',
        'surgery',
        'sympathy',
        'tale',
        'throat',
        'trainer',
        'uncle',
        'youth',
        'time',
        'work',
        'film',
        'water',
        'money',
        'example',
        'while',
        'business',
        'study',
        'game',
        'life',
        'form',
        'air',
        'day',
        'place',
        'number',
        'part',
        'field',
        'fish',
        'back',
        'process',
        'heat',
        'hand',
        'experience',
        'job',
        'book',
        'end',
        'point',
        'type',
        'home',
        'economy',
        'value',
        'body',
        'market',
        'guide',
        'interest',
        'state',
        'radio',
        'course',
        'company',
        'price',
        'size',
        'card',
        'list',
        'mind',
        'trade',
        'line',
        'care',
        'group',
        'risk',
        'word',
        'fat',
        'force',
        'key',
        'light',
        'training',
        'name',
        'school',
        'top',
        'amount',
        'level',
        'order',
        'practice',
        'research',
        'sense',
        'service',
        'piece',
        'web',
        'boss',
        'sport',
        'fun',
        'house',
        'page',
        'term',
        'test',
        'answer',
        'sound',
        'focus',
        'matter',
        'kind',
        'soil',
        'board',
        'oil',
        'picture',
        'access',
        'garden',
        'range',
        'rate',
        'reason',
        'future',
        'site',
        'demand',
        'exercise',
        'image',
        'case',
        'cause',
        'coast',
        'action',
        'age',
        'bad',
        'boat',
        'record',
        'result',
        'section',
        'building',
        'mouse',
        'cash',
        'class',
        'nothing',
        'period',
        'plan',
        'store',
        'tax',
        'side',
        'subject',
        'space',
        'rule',
        'stock',
        'weather',
        'chance',
        'figure',
        'man',
        'model',
        'source',
        'beginning',
        'earth',
        'program',
        'chicken',
        'design',
        'feature',
        'head',
        'material',
        'purpose',
        'question',
        'rock',
        'salt',
        'act',
        'birth',
        'car',
        'dog',
        'object',
        'scale',
        'sun',
        'note',
        'profit',
        'rent',
        'speed',
        'style',
        'war',
        'bank',
        'craft',
        'half',
        'inside',
        'outside',
        'standard',
        'bus',
        'exchange',
        'eye',
        'fire',
        'position',
        'pressure',
        'stress',
        'advantage',
        'benefit',
        'box',
        'frame',
        'issue',
        'step',
        'cycle',
        'face',
        'item',
        'metal',
        'paint',
        'review',
        'room',
        'screen',
        'structure',
        'view',
        'account',
        'ball',
        'discipline',
        'medium',
        'share',
        'balance',
        'bit',
        'black',
        'bottom',
        'choice',
        'gift',
        'impact',
        'machine',
        'shape',
        'tool',
        'wind',
        'address',
        'average',
        'career',
        'culture',
        'morning',
        'pot',
        'sign',
        'table',
        'task',
        'condition',
        'contact',
        'credit',
        'egg',
        'hope',
        'ice',
        'network',
        'north',
        'square',
        'attempt',
        'date',
        'effect',
        'link',
        'post',
        'star',
        'voice',
        'capital',
        'challenge',
        'friend',
        'self',
        'shot',
        'brush',
        'couple',
        'exit',
        'front',
        'function',
        'lack',
        'living',
        'plant',
        'plastic',
        'spot',
        'summer',
        'taste',
        'theme',
        'track',
        'wing',
        'brain',
        'button',
        'click',
        'desire',
        'foot',
        'gas',
        'influence',
        'notice',
        'rain',
        'wall',
        'base',
        'damage',
        'distance',
        'feeling',
        'pair',
        'savings',
        'staff',
        'sugar',
        'target',
        'text',
        'animal',
        'author',
        'budget',
        'discount',
        'file',
        'ground',
        'lesson',
        'minute',
        'officer',
        'phase',
        'reference',
        'register',
        'sky',
        'stage',
        'stick',
        'title',
        'trouble',
        'bowl',
        'bridge',
        'campaign',
        'character',
        'club',
        'edge',
        'evidence',
        'fan',
        'letter',
        'lock',
        'maximum',
        'novel',
        'option',
        'pack',
        'park',
        'plenty',
        'quarter',
        'skin',
        'sort',
        'weight',
        'baby',
        'background',
        'carry',
        'dish',
        'factor',
        'fruit',
        'glass',
        'joint',
        'master',
        'muscle',
        'red',
        'strength',
        'traffic',
        'trip',
        'vegetable',
        'appeal',
        'chart',
        'gear',
        'ideal',
        'kitchen',
        'land',
        'log',
        'mother',
        'net',
        'party',
        'principle',
        'relative',
        'sale',
        'season',
        'signal',
        'spirit',
        'street',
        'tree',
        'wave',
        'belt',
        'bench',
        'commission',
        'copy',
        'drop',
        'minimum',
        'path',
        'progress',
        'project',
        'sea',
        'south',
        'status',
        'stuff',
        'ticket',
        'tour',
        'angle',
        'blue',
        'breakfast',
        'confidence',
        'daughter',
        'degree',
        'doctor',
        'dot',
        'dream',
        'duty',
        'essay',
        'father',
        'fee',
        'finance',
        'hour',
        'juice',
        'luck',
        'milk',
        'mouth',
        'peace',
        'pipe',
        'stable',
        'storm',
        'substance',
        'team',
        'trick',
        'afternoon',
        'bat',
        'beach',
        'blank',
        'catch',
        'chain',
        'consideration',
        'cream',
        'crew',
        'detail',
        'gold',
        'interview',
        'kid',
        'mark',
        'mission',
        'pain',
        'pleasure',
        'score',
        'screw',
        'sex',
        'shop',
        'shower',
        'suit',
        'tone',
        'window',
        'agent',
        'band',
        'bath',
        'block',
        'bone',
        'calendar',
        'candidate',
        'cap',
        'coat',
        'contest',
        'corner',
        'court',
        'cup',
        'district',
        'door',
        'east',
        'finger',
        'garage',
        'guarantee',
        'hole',
        'hook',
        'implement',
        'layer',
        'lecture',
        'lie',
        'manner',
        'meeting',
        'nose',
        'parking',
        'partner',
        'profile',
        'rice',
        'routine',
        'schedule',
        'swimming',
        'telephone',
        'tip',
        'winter',
        'airline',
        'bag',
        'battle',
        'bed',
        'bill',
        'bother',
        'cake',
        'code',
        'curve',
        'designer',
        'dimension',
        'dress',
        'ease',
        'emergency',
        'evening',
        'extension',
        'farm',
        'fight',
        'gap',
        'grade',
        'holiday',
        'horror',
        'horse',
        'host',
        'husband',
        'loan',
        'mistake',
        'mountain',
        'nail',
        'noise',
        'occasion',
        'package',
        'patient',
        'pause',
        'phrase',
        'proof',
        'race',
        'relief',
        'sand',
        'sentence',
        'shoulder',
        'smoke',
        'stomach',
        'string',
        'tourist',
        'towel',
        'vacation',
        'west',
        'wheel',
        'wine',
        'arm',
        'aside',
        'associate',
        'bet',
        'blow',
        'border',
        'branch',
        'breast',
        'brother',
        'buddy',
        'bunch',
        'chip',
        'coach',
        'cross',
        'document',
        'draft',
        'dust',
        'expert',
        'floor',
        'god',
        'golf',
        'habit',
        'iron',
        'judge',
        'knife',
        'landscape',
        'league',
        'mail',
        'mess',
        'native',
        'opening',
        'parent',
        'pattern',
        'pin',
        'pool',
        'pound',
        'request',
        'salary',
        'shame',
        'shelter',
        'shoe',
        'silver',
        'tackle',
        'tank',
        'trust',
        'assist',
        'bake',
        'bar',
        'bell',
        'bike',
        'blame',
        'boy',
        'brick',
        'chair',
        'closet',
        'clue',
        'collar',
        'comment',
        'conference',
        'devil',
        'diet',
        'fear',
        'fuel',
        'glove',
        'jacket',
        'lunch',
        'monitor',
        'mortgage',
        'nurse',
        'pace',
        'panic',
        'peak',
        'plane',
        'reward',
        'row',
        'sandwich',
        'shock',
        'spite',
        'spray',
        'surprise',
        'till',
        'transition',
        'weekend',
        'welcome',
        'yard',
        'alarm',
        'bend',
        'bicycle',
        'bite',
        'blind',
        'bottle',
        'cable',
        'candle',
        'clerk',
        'cloud',
        'concert',
        'counter',
        'flower',
        'grandfather',
        'harm',
        'knee',
        'lawyer',
        'leather',
        'load',
        'mirror',
        'neck',
        'pension',
        'plate',
        'purple',
        'ruin',
        'ship',
        'skirt',
        'slice',
        'snow',
        'specialist',
        'stroke',
        'switch',
        'trash',
        'tune',
        'zone',
        'anger',
        'award',
        'bid',
        'bitter',
        'boot',
        'bug',
        'camp',
        'candy',
        'carpet',
        'cat',
        'champion',
        'channel',
        'clock',
        'comfort',
        'cow',
        'crack',
        'engineer',
        'entrance',
        'fault',
        'grass',
        'guy',
        'hell',
        'highlight',
        'incident',
        'island',
        'joke',
        'jury',
        'leg',
        'lip',
        'mate',
        'motor',
        'nerve',
        'passage',
        'pen',
        'pride',
        'priest',
        'prize',
        'promise',
        'resident',
        'resort',
        'ring',
        'roof',
        'rope',
        'sail',
        'scheme',
        'script',
        'sock',
        'station',
        'toe',
        'tower',
        'truck',
        'witness',
        'a',
        'you',
        'it',
        'can',
        'will',
        'if',
        'one',
        'many',
        'most',
        'other',
        'use',
        'make',
        'good',
        'look',
        'help',
        'go',
        'great',
        'being',
        'few',
        'might',
        'still',
        'public',
        'read',
        'keep',
        'start',
        'give',
        'human',
        'local',
        'general',
        'she',
        'specific',
        'long',
        'play',
        'feel',
        'high',
        'tonight',
        'put',
        'common',
        'set',
        'change',
        'simple',
        'past',
        'big',
        'possible',
        'particular',
        'today',
        'major',
        'personal',
        'current',
        'national',
        'cut',
        'natural',
        'physical',
        'show',
        'try',
        'check',
        'second',
        'call',
        'move',
        'pay',
        'let',
        'increase',
        'single',
        'individual',
        'turn',
        'ask',
        'buy',
        'guard',
        'hold',
        'main',
        'offer',
        'potential',
        'professional',
        'international',
        'travel',
        'cook',
        'alternative',
        'following',
        'special',
        'working',
        'whole',
        'dance',
        'excuse',
        'cold',
        'commercial',
        'low',
        'purchase',
        'deal',
        'primary',
        'worth',
        'fall',
        'necessary',
        'positive',
        'produce',
        'search',
        'present',
        'spend',
        'talk',
        'creative',
        'tell',
        'cost',
        'drive',
        'green',
        'support',
        'glad',
        'remove',
        'return',
        'run',
        'complex',
        'due',
        'effective',
        'middle',
        'regular',
        'reserve',
        'independent',
        'leave',
        'original',
        'reach',
        'rest',
        'serve',
        'watch',
        'beautiful',
        'charge',
        'active',
        'break',
        'negative',
        'safe',
        'stay',
        'visit',
        'visual',
        'affect',
        'cover',
        'report',
        'rise',
        'walk',
        'white',
        'beyond',
        'junior',
        'pick',
        'unique',
        'anything',
        'classic',
        'final',
        'lift',
        'mix',
        'private',
        'stop',
        'teach',
        'western',
        'concern',
        'familiar',
        'fly',
        'official',
        'broad',
        'comfortable',
        'gain',
        'maybe',
        'rich',
        'save',
        'stand',
        'young',
        'heavy',
        'hello',
        'lead',
        'listen',
        'valuable',
        'worry',
        'handle',
        'leading',
        'meet',
        'release',
        'sell',
        'finish',
        'normal',
        'press',
        'ride',
        'secret',
        'spread',
        'spring',
        'tough',
        'wait',
        'brown',
        'deep',
        'display',
        'flow',
        'hit',
        'objective',
        'shoot',
        'touch',
        'cancel',
        'chemical',
        'cry',
        'dump',
        'extreme',
        'push',
        'conflict',
        'eat',
        'fill',
        'formal',
        'jump',
        'kick',
        'opposite',
        'pass',
        'pitch',
        'remote',
        'total',
        'treat',
        'vast',
        'abuse',
        'beat',
        'burn',
        'deposit',
        'print',
        'raise',
        'sleep',
        'somewhere',
        'advance',
        'anywhere',
        'consist',
        'dark',
        'double',
        'draw',
        'equal',
        'fix',
        'hire',
        'internal',
        'join',
        'kill',
        'sensitive',
        'tap',
        'win',
        'attack',
        'claim',
        'constant',
        'drag',
        'drink',
        'guess',
        'minor',
        'pull',
        'raw',
        'soft',
        'solid',
        'wear',
        'weird',
        'wonder',
        'annual',
        'count',
        'dead',
        'doubt',
        'feed',
        'forever',
        'impress',
        'nobody',
        'repeat',
        'round',
        'sing',
        'slide',
        'strip',
        'whereas',
        'wish',
        'combine',
        'command',
        'dig',
        'divide',
        'equivalent',
        'hang',
        'hunt',
        'initial',
        'march',
        'mention',
        'spiritual',
        'survey',
        'tie',
        'adult',
        'brief',
        'crazy',
        'escape',
        'gather',
        'hate',
        'prior',
        'repair',
        'rough',
        'sad',
        'scratch',
        'sick',
        'strike',
        'employ',
        'external',
        'hurt',
        'illegal',
        'laugh',
        'lay',
        'mobile',
        'nasty',
        'ordinary',
        'respond',
        'royal',
        'senior',
        'split',
        'strain',
        'struggle',
        'swim',
        'train',
        'upper',
        'wash',
        'yellow',
        'convert',
        'crash',
        'dependent',
        'fold',
        'funny',
        'grab',
        'hide',
        'miss',
        'permit',
        'quote',
        'recover',
        'resolve',
        'roll',
        'sink',
        'slip',
        'spare',
        'suspect',
        'sweet',
        'swing',
        'twist',
        'upstairs',
        'usual',
        'abroad',
        'brave',
        'calm',
        'concentrate',
        'estimate',
        'grand',
        'male',
        'mine',
        'prompt',
        'quiet',
        'refuse',
        'regret',
        'reveal',
        'rush',
        'shake',
        'shift',
        'shine',
        'steal',
        'suck',
        'surround',
        'anybody',
        'bear',
        'brilliant',
        'dare',
        'dear',
        'delay',
        'drunk',
        'female',
        'hurry',
        'inevitable',
        'invite',
        'kiss',
        'neat',
        'pop',
        'punch',
        'quit',
        'reply',
        'representative',
        'resist',
        'rip',
        'rub',
        'silly',
        'smile',
        'spell',
        'stretch',
        'stupid',
        'tear',
        'temporary',
        'tomorrow',
        'wake',
        'wrap',
        'yesterday',
    ]



    





    for noun in nouns:
        get_songs(noun, cur, conn)

    #update tables

    #update_books(cur, conn)

    #update_songs(cur, conn)




    #keywords list
    key_words = []

    #songs list
    songs_list = []
'''
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
'''

if __name__ == "__main__":
    main()


    
    

    

        

    





    
    
    
