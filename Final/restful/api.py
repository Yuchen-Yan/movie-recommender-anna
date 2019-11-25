import json
from functools import wraps
import jwt
import datetime
import time
import os


import pandas as pd

from flask import Flask
from flask import request
from flask_restplus import Resource, Api
from flask_restplus import abort
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse
from RecommenderSystems import Recommender




pd.options.mode.chained_assignment = None

#reading csv file, assuming we are using the dataset from kaggle
def read_csv(file):
    #if the file is tmdb_5000
    if file == 'tmdb_5000_movies.csv':
        df = pd.read_csv(file)
        df = extract_tmdb_5000_Columns(df)
        
    return df


#extracting columns from tmdb 5000 csv file/ data clean 
def extract_tmdb_5000_Columns(df):

    df = df[['id','title','tagline', 'overview', 
            'release_date', 'popularity', 'genres', 'keywords',
            'spoken_languages', 'production_companies', 'production_countries',
            'vote_average', 'vote_count','homepage']]

    #preprocess and renaming variable
    df['production_countries'] = df['production_countries'].str.replace('iso_3166_1', 'abbrev')
    df['spoken_languages'] = df['spoken_languages'].str.replace('iso_639_1', 'abbrev')
    df['spoken_languages'] = df['spoken_languages'].str.replace('", "name":.*},', '"},')
    df['spoken_languages'] = df['spoken_languages'].str.replace('", "name":.*}]', '"}]')
    #data cleaning
    df['genres'] = df['genres'].str.replace("{\"id\": \d*, \"name\": ", '').replace('},'," ")
    df['genres'] = df['genres'].str.replace('\"}, \"'," | ")
    df['genres'] = df['genres'].str.replace('\"}]',"")
    df['genres'] = df['genres'].str.replace("\[\"","")
    df.reset_index()
    df.index.name="index"
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
    return df.loc[df['release_date'].str[0:4] == str(date)]

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
    if len(country) > 2:
        return df[df['production_countries'].str.contains(country)] 
    else :
        return df[df['production_countries'].str.contains('"' + country + '"')] 

#By list of countries
def get_movies_by_list_of_countries(df, countries):
    df1 = df    
    for country in countries:
        if len(country) > 2:
            df1 = df1[df1['production_countries'].str.contains(country)]
        else:
            df1 = df1[df1['production_countries'].str.contains('"' + country + '"')]
    return df1

#By company
def get_movies_by_company(df, company):
    return df[df['production_companies'].str.contains(company)]

def get_movies_by_list_of_companies(df, companies):
    df1 = df     
    for c in companies:
        df1 = df1[df1['production_companies'].str.contains(companies)]
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

#GET recommd_movies detail by COLRELETION FIlTERING RESULT
def get_recommend_movies(df, recommd_movies_list):
    result = pd.merge(recommd_movies_list, df, left_on='tmdbId', right_on='id')
    result.drop(['tmdbId'],inplace=True, axis=1)
    return result
    

###########
#API
###########


class AuthenticationToken:
    def __init__(self, secret_key, expires_in):
        self.secret_key = secret_key
        self.expires_in = expires_in

    def generate_token(self, username):
        info = {
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=self.expires_in)
        }
        return jwt.encode(info, self.secret_key, algorithm='HS256')

    def validate_token(self, token):
        info = jwt.decode(token, self.secret_key, algorithms=['HS256'])
        return info['username']


SECRET_KEY = "A SECRET KEY; USUALLY A VERY LONG RANDOM STRING"
expires_in = 600
auth = AuthenticationToken(SECRET_KEY, expires_in)

app = Flask(__name__)
api = Api(app, authorizations={
    'API-KEY': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'AUTH-TOKEN'
    }
},
        security='API-KEY',
        default = "Movies",
        title="Movie Dataset",
        description="This is the movie recommendation system")

# runging log
@app.before_request
def before_request():
    ip = request.remote_addr
    url = request.url
    timestamp = time.time()
    if not os.path.exists("log.csv"):
        contents= [{"IP":ip, "request_url":url, "timestamp":timestamp}]
        df = pd.DataFrame(contents, columns = ["IP","request_url","timestamp"])
        df.to_csv("log.csv", index=True)
    else:
        contents= [{"IP":ip, "request_url":url, "timestamp":timestamp}]
        df2 = pd.DataFrame(contents, columns = ["IP","request_url","timestamp"])
        df2.to_csv('log.csv', mode = 'a', header =None)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('AUTH-TOKEN')
        if not auth:
            abort(401, 'Authentication token is missing')

        try:
            user = auth.validate_token(token)
        except Exception as e:
            abort(401, e)

        return f(*args, **kwargs)

    return decorated

credential_model = api.model('credential', {
    'username': fields.String,
    'password': fields.String
})

credential_parser = reqparse.RequestParser()
credential_parser.add_argument('username', type=str)
credential_parser.add_argument('password', type=str)

@api.route('/token')
class Token(Resource):
    @api.response(200, 'Successful')
    @api.doc(description="Generates a authentication token")
    @api.expect(credential_parser, validate=True)
    def get(self):
        args = credential_parser.parse_args()

        username = args.get('username')
        password = args.get('password')

        if username == 'admin' and password == 'admin':
            return {"token": str(auth.generate_token(username), 'utf-8')}

        return {"message": "authorization has been refused for those credentials."}, 401
'''
paranum_model = api.model('paranum', {
    'rating': fields.String,
    'year': fields.String,
    'genre': fields.String

})
'''
# SEARCH BY FEATURES
paranum_parser = reqparse.RequestParser()
paranum_parser.add_argument('rating', type=int)
paranum_parser.add_argument('year', type=int)
paranum_parser.add_argument('genre', type=str)

@api.route('/movielist')
class MovieList(Resource):
    @api.response(404, 'Movie was not found')
    @api.response(200, 'Successful')
    @api.doc(description="Get all movies by features")
    @api.expect(paranum_parser, validate=True)
    @requires_auth
    def get(self):
        args = paranum_parser.parse_args()
        rating = args.get('rating')
        year = args.get('year')
        genre = args.get('genre')

        if genre != None :
            rdf = get_movies_by_genre(df, genre)
            if year != None:
                rdf = get_movies_by_release_date(rdf, year)
                if rating != None:
                    rdf = rdf[rdf['vote_average'] >= rating]
            else: #year is null 
                rdf = rdf[rdf['vote_average'] >= rating]
        else: # year and rate 
            rdf = get_movies_by_release_date(df, year)
            rdf = rdf[rdf['vote_average'] >= rating]
        
        json_str = rdf.head(20).to_json(orient='index')
        ds = json.loads(json_str)
        ret = []

        for idx in ds:
            movie = ds[idx]
            movie['index'] = int(idx)
            ret.append(movie)

        return ret



@api.route('/movies/<string:name>')
@api.param('name', 'The name of movie')
class Movie(Resource):
    @api.response(404, 'Movie was not found')
    @api.response(200, 'Successful')
    @api.doc(description="Get a Movie by its title")
    @requires_auth
    def get(self, name):
        rdf = get_movies_by_title(df, str(name))
        
        if rdf.empty:
            pass
        else:
            recommend_movies = Recommender(name)
            result = get_recommend_movies(df, recommend_movies)

            json_str = result.to_json(orient='index')

            ds = json.loads(json_str)
            ret = []

            for idx in ds:
                #print(idx)
                movie = ds[idx]
                movie['index'] = int(idx)
                ret.append(movie)
            return ret

@api.route('/visit_report')
class Visit_report(Resource):
    @api.response(200, 'Successful')
    @api.doc(description="Get the visit report")
    @requires_auth
    def get(self):
        if not os.path.exists("log.csv"):
            return {"message": "File do not exists."}, 404
            
        df_report = pd.read_csv("log.csv")
        if df_report.empty:
            pass
        else:
            json_str = df_report.to_json(orient='index')

            ds = json.loads(json_str)
            ret = []

            for idx in ds:
                content = ds[idx]
                content['index'] = int(idx)
                ret.append(content)
            return ret
   

if __name__ == "__main__":
    csv_file = "tmdb_5000_movies.csv"
    df = read_csv(csv_file)
    #dict of language abbrevation and its long form
    ln = pd.read_csv("languages.csv")

    app.run(debug=True)

