# comp9321-ass2

19.11.2019
Front end almost finished, The index.html is main page, which gaves user two choices of input - movies name and movie feature. Moviesearch.html is movie name search page. TMDB api are used to fetch data( can be change to our api).
the other page that aims to search by features is simalarly , I will finish later.

### Movie_search Page
    input: movie name
    output : movie card , which contains movie title, release_date, overview, poster, rating average, Genre.
### feature_search Page
    input: Rating, Spoken language, Grenre (both or just one)
    output: same as Movie_search Page

TMDB api I used:
```
`https://api.themoviedb.org/3/search/movie?api_key=e3062f645fde67eecb0c4b0e2bcd7b81&query=${searchtext}&page=1`;
```
 
 change is to our Api when test backend service.
    
