import requests
import json
import unittest
import os

#
# Your name: Katie Huang
# Who you worked with:
#

'''def read_cache(CACHE_FNAME):
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
    
    return CACHE_DICTION'''



def get_books_for_cache():
    """
    This function cycles through a list of NYT Best seller books
    """
    request_url = "https://api.nytimes.com/svc/books/v3/lists/names.json?api-key=LULfKyQLZp6nERnrISvzNj732a3fX3te"





def write_cache(cache_file, cache_dict):
    """
    This function encodes the cache dictionary (cache_dict) into JSON format and
    writes the contents in the cache file (cache_file) to save the search results.
    """
    #encodes cache_dict into JSON
    info = json.dumps(cache_dict)
    #open cache file
    fw = open(cache_file, 'w')
    #write the cache_dict into cache_file
    fw.write(info)
    fw.close()


def get_data_with_caching(country_code, year, per_page=50):
    """
    This function uses the passed country_code and year to generate a
    request_url and then checks if this url is in the dictionary
    returned by read_cache.  If the request_url exists as a key in the dictionary, 
    it should print 'Using cache for ' followed by the country_code and
    return the results for that request_url.
    If the request_url does not exist in the dictionary, the function should 
    print "Fetching for " followed by the country_code and make a call to the
    World Bank API to get and return the CO2 emission data list searched by country 
    (or countries) and year.
    The documentation of the API is at
    https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation
    If there were results, it should add them to a dictionary
    (key is the request_url, and value is the results)
    and write out the dictionary to a file using write_cache. If there was an exception 
    during the search, it should print out "Exception" and return None.
    """
    api_c_code  = country_code      # country code (e.g. "USA", "USA;CAN")
    api_type    = "EN.ATM.CO2E.PC"  # CO2 emissions data (metric tons per capita)
    api_year    = year              # year (e.g. 2000)
    api_per_page= per_page          # maximum return items (the default value is 50)
    base_url    = "http://api.worldbank.org/v2/country/{}/indicator/{}?format=json&date={}&per_page={}"
    request_url = base_url.format(api_c_code, api_type, api_year, api_per_page)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    CACHE_FNAME = dir_path + '/' + "cache_climate.json"
    CACHE_DICTION  = read_cache(CACHE_FNAME)

    #check to see if request_url exists as a key in CACHE_dictionary
    if request_url in CACHE_DICTION:
        print("Using cache for " + country_code)
    
    #if not in cache, fetch from world bank API
    else:
        try:
            print("Fetching for " + country_code)
            #send request to API and get response (a string)
            r = requests.get(request_url)
            x = json.loads(r.text)
            #add results to dictionary (key: request_url, value: r)
            CACHE_DICTION[request_url] = x
            #write dictionary into cache_file
            write_cache(CACHE_FNAME, CACHE_DICTION)
            
        except:
            print('Exception')
            return None
    
    return CACHE_DICTION[request_url]



     

def country_dict():
    """
    This function returns a dictionary of all countries' information in 2014.
    The key of the dictionary will be a country name (e.g. United States, Canada)
    and the value will be a three letters country code (e.g. USA, CAN)
    Call get_data_with_caching and analyze the returned list to create the dictionary.
    HINT1: API request with the country code "all" returns the data of all countries
    HINT2: Adjust the third parameter of get_data_with_caching (per_page) to get 
    all countries' data (You can find the number of the country data from the API data)
    """
    final_dictionary = {}
    all_data = get_data_with_caching('all', 2014, 264)
    data = all_data[1]
    length = len(data)
    i = 0
    while i < length:
        dictionary = data[i]
        block = dictionary["country"]
        name = block.get("value")
        code = dictionary['countryiso3code']
        final_dictionary[name] = code
        i += 1
    return final_dictionary


    


def reduced_percent(country_name, before, after):
    """
    This function receives three parameters: the name of a country and a before and
    after year.  Call country_dict and convert the country_name
    to a country_code. Call get_data_with_caching and analyze the returned list to
    obtain the CO2 emission data for the two years (before and after) and
    return the percentage difference from the before year to the after year. 
    The return value should be rounded to the first decimal place.
    For example, if the emission in 2000 and 2014 is 16 and 13 respectively,
    the percentage difference is calculated by (16-13)/16*100 = 7.7%.
    """

    country_dictionary = country_dict()
    country_code = country_dictionary[country_name]
    lst_before = get_data_with_caching(country_code, before)
    
    lst_after = get_data_with_caching(country_code, after)
   
    
    chunk_before = lst_before[1]
    chunk_before = chunk_before[0]
    value_before = chunk_before["value"]
    chunk_after = lst_after[1]
    chunk_after = chunk_after[0]
    value_after = chunk_after['value']
    percentage_diff = (value_before - value_after)/value_before*100
    percentage_diff = round(percentage_diff, 1)
    return percentage_diff


def top_ranking():
    """
    EXTRA QUESTION
    This function returns the top ten CO2 emission countries in 2014.
    The list of top ten countries in 2014 is provided as the list 'top_countries'. 
    Return a list of a tuple (country name, CO2 emission value) sorted by the value.
    The value should be rounded to the first decimal place.
    HINT: The API returns several countries data in a single request if you use
    a country code separated by semicolons, such as "USA;CAN;BRA". 
    """

    top_countries = ['Bahrain', 'Brunei Darussalam', 'Kuwait', 'Luxembourg',
     'New Caledonia', 'Qatar', 'Saudi Arabia', 'Trinidad and Tobago',
     'United Arab Emirates', 'United States']

    pass

#######################################
#### DO NOT CHANGE AFTER THIS LINE ####
#######################################

class TestHomework8(unittest.TestCase):
    def setUp(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.cache = dir_path + '/' + "cache_climate.json"
        
    def test_write_cache(self):
        dict = read_cache(self.cache)
        write_cache(self.cache,dict)
        dict2 = read_cache(self.cache)
        self.assertEqual(dict, dict2)

    def test_get_data_with_caching(self):
        data1 = get_data_with_caching('BRA', 2000)
        self.assertEqual(type(data1), type([]))
        self.assertEqual(data1[0]['page'], 1)
        self.assertEqual(data1[1][0]['countryiso3code'], "BRA")
        data2 = get_data_with_caching('ARB', 2000)
        self.assertEqual(data2[1][0]['countryiso3code'], "ARB")
        url = "http://api.worldbank.org/v2/country/ARB/indicator/EN.ATM.CO2E.PC?format=json&date=2000&per_page=50"
        dict_new = read_cache(self.cache)
        res = dict_new[url]
        self.assertEqual(res[1][0]['countryiso3code'], "ARB")
    
    def test_country_dictionary(self):
        c_dict = country_dict()
        self.assertEqual(type(c_dict), type({}))
        self.assertEqual(c_dict['Arab World'], "ARB")
        self.assertEqual(c_dict['United States'], "USA")
        self.assertEqual(c_dict['Zimbabwe'], "ZWE")

    def test_reduced_percent(self):
        self.assertEqual(type(reduced_percent('Canada', 1998, 2008)), type(1.0))
        self.assertEqual(reduced_percent('United States', 2005, 2014), 15.8)
        self.assertEqual(reduced_percent('Canada', 2000, 2008), 3.1)

    def test_top_ranking_EXTRA_(self):
        data2 = top_ranking()
        self.assertEqual(type(data2), type([]))
        self.assertEqual(len(data2), 10)
        self.assertEqual(data2,
        [   ('Qatar', 43.9), ('Trinidad and Tobago', 34.0),('Kuwait', 25.8),
            ('Bahrain', 23.5),('United Arab Emirates', 22.9),
            ('Brunei Darussalam', 22.2), ('Saudi Arabia', 19.4), ('Luxembourg', 17.4),
            ('United States', 16.5), ('New Caledonia', 16.0)
        ])

def main():
    
    # Get the cached data for BRA
    print("This should use the cache")
    data1 = get_data_with_caching('BRA', 2000)
    
    # fetch the data for ARB
    print("This should fetch new data")
    data2 = get_data_with_caching('ARB', 2000)

    # fetch the data for ARB again
    print("This should use the cache")
    data2 = get_data_with_caching('ARB', 2000)
    
    # get the country name and code dictionary
    print("Getting the country dictionary")
    dict = country_dict()
    print("The country code for 'United States' is: " + dict['United States'])
    
    # The reduced % of CO2 emission in the US between 2005 to 2014
    print("----CO2 Reduction----")
    value2 = reduced_percent('United States', 2005, 2014)
    print("The US reduced {}% of CO2 emission in 2014 compared to 2005".format(value2))
    
    # EXTRA. Top 10 of CO2 emission countries in 2014
    print("----[EXTRA] Top ten countries----")
    print("The top ten CO2 emission countries in 2014:")
    ten_list = top_ranking()
    if ten_list != None:
        for x in range(10):
            print("No.{}: {} ({})".format(x+1, ten_list[x][0], ten_list[x][1]))
    
    print("------------")

    # You can comment this out to test with just the main, but be sure to uncomment it and test
    # with unittest as well.
    unittest.main(verbosity=2)
    print("------------")


if __name__ == "__main__":
    main()
