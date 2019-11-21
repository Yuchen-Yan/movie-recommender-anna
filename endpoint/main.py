import pandas as pd
from flask import Flask
from flask_restplus import Resource, Api
import json

app = Flask(__name__)
api = Api(app)


@api.route('/movies/<title>')
class Movies(Resource):
    def get(self, title):
        if title not in df.index:
            api.abort(404, "Movie {} doesn't exist".format(title))
        print(type(df.loc[title]))
        book = dict(df.loc[title])
        return book


if __name__ == '__main__':
    columns_to_drop = ['budget',
                       'popularity',
                       'production_companies',
                       'release_date',
                       'revenue',
                       'status',
                       'tagline',
                       ]
    csv_file = "tmdb_5000_movies.csv"
    df = pd.read_csv(csv_file)

    # drop unnecessary columns
    df.drop(columns_to_drop, inplace=True, axis=1)

    df.set_index('title', inplace=True)
    #print(df.to_string)
    # run the application
    app.run(debug=True)
    print(json.dumps(book))
    #print(book)