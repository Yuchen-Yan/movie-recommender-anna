import json
import pandas as pd 
from pymongo import MongoClient

pd.options.mode.chained_assignment = None

#reading csv file, assuming we are using the dataset from kaggle
def read_csv(file):
    #if the file is tmdb_5000
    if file == 'tmdb_5000_movies.csv':
        df = pd.read_csv(file)
        df = extract_tmdb_5000_Columns(df)

    return df

#extracting columns from tmdb 5000 csv file
def extract_tmdb_5000_Columns(df):

    df = df[['title','tagline', 'overview', 
            'release_date', 'popularity', 'genres', 'keywords',
            'spoken_languages', 'production_companies', 'production_countries',
            'vote_average', 'vote_count']]

    #preprocess and renaming variable
    df['production_countries'] = df['production_countries'].str.replace('iso_3166_1', 'abbrev')
    df['spoken_languages'] = df['spoken_languages'].str.replace('iso_639_1', 'abbrev')
    df['spoken_languages'] = df['spoken_languages'].str.replace('", "name":.*},', '"},')
    df['spoken_languages'] = df['spoken_languages'].str.replace('", "name":.*}]', '"}]')
    return df

#Displaying columns with percentage of nulls
def display_percentage_of_nulls(df):
    num_of_rows = df.shape[0]
    for column in df:
        percent = 100 * df[column].isnull().sum() / num_of_rows
        print(column, str(percent) + '%')

#Query
#By title
def get_movies_by_title(df, title):
    return df.loc[df['title'] == title]

#By release date
def get_movies_by_release_date(df, date):
    return df.loc[df['release_date'] == date]

#By genre
def get_movies_by_genre(df, genre):
    return df[df['genres'].str.contains(genre)]

#By list of genres (Only movie that satisfy all genres will return)
def get_movies_by_list_of_genres(df, genres):
    df1 = df 
    for g in genres:
        df1 = df1[df1['genres'].str.contains(g)]
    return df1

#By keyword
def get_movies_by_keyword(df, keyword):
    return df[df['keywords'].str.contains(keyword)]

#By list of keywords
def get_movies_by_list_of_keywords(df, keywords):
    df1 = df
    for k in keywords:
        df1 = df1[df1['keywords'].str.contains(k)]
    return df1

#By language
def get_movies_by_language(df, language, ln):
    if len(language) > 2:
        #ln = ln[ln['full'].str.contains(language)]
        for index, row in ln[ln['full'].str.contains(language)].iterrows():
            shortForm = row['abb']
            return df[df['spoken_languages'].str.contains('"' + shortForm + '"')]         
    else:
        return df[df['spoken_languages'].str.contains('"' + language + '"')] 


#By country
def get_movies_by_country(df, country):
    return df[df['production_countries'].str.contains(country)] 

#By list of countries
def get_movies_by_list_of_countries(df, countries):
    df1 = df    
    for country in countries:
        df1 = df1[df1['production_countries'].str.contains(country)]
    return df1

#By company
def get_movies_by_company(df, company):
    return df[df['production_companies'].str.contains(company)]

def get_movies_by_list_of_companies(df, companies):
    df1 = df     
    for c in companies:
        df1 = df1[df1['production_companies'].str.contains(company)]
    return df1 

#ADD DATAFRAME TO DB (OPTIONAL)
def add_data_to_db(df, name):
    db_name = 'comp9321asst2'
    mongo_port = 27017
    mongo_host = 'localhost'

    client = MongoClient(mongo_host, mongo_port)
    db = client[db_name]
    c = db[name]
    records = json.loads(df.T.to_json()).values()
    c.insert(records)


if __name__ == "__main__":
    csv_file = "tmdb_5000_movies.csv"
    df = read_csv(csv_file)
    #dict of language abbrevation and its long form
    ln = pd.read_csv("languages.csv")

    ##########
    #examples
    ##########

    #return only one movie with name "The Avengers"
    print(get_movies_by_title(df, "The Avengers"))
    #return two movies that are released on the same date
    print(get_movies_by_release_date(df, "2009-12-10"))
    #return all movies with that particular genre
    print(get_movies_by_genre(df, "Action"))
    #return all movies in that list of genres
    print(get_movies_by_list_of_genres(df, ['Action', 'Adventure']))

    print(get_movies_by_country(df, "United States"))

    print(get_movies_by_list_of_countries(df, ["United States", "GB"]))

    print(get_movies_by_language(df, "English", ln))