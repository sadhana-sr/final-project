import requests
import json
import unittest
import string
import sqlite3
import os
import random
import xml.etree.ElementTree as ET

#
# Your name: Katie Huang
# Who you worked with:
#


 


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
    while key_word_entries + book_entries < 18:
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
            

        
        
   

def connectDatabase(db_name):
    # connect to database
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


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
    




            
    



    


    
    
    
        
    









def main():

    #connect to database
    cur, conn = connectDatabase('books.db')

    #set up both tables if they don't already exist
    setUpKeyWordsTable(cur, conn)
    setUpBooksTable(cur, conn)

    #update both tables with new books and their info
    update_books(cur, conn)
    

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

        

    





    
    
    
    
    # You can comment this out to test with just the main, but be sure to uncomment it and test
    # with unittest as well.
    #unittest.main(verbosity=2)
    #print("------------")


if __name__ == "__main__":
    main()
