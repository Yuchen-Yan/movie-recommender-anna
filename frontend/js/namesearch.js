const genres ={"Action":28, "Adventure":12, "Animation":16,"Comedy": 35, "Crime":80, "Documentary":99,"Drama":18,"Family":10751,"Fantasy":14,"History":36,"Horror":27
,"Music":10402,"Mystery":9648, "Romance":10749,"Science Fiction":878,"TV Movie":10770,"Thriller":53,"War":10752,"Western": 37};

myapi = `https://api.themoviedb.org/3/search/movie?api_key=e3062f645fde67eecb0c4b0e2bcd7b81`;
myapi2 = `https://api.themoviedb.org/3/discover/movie?api_key=e3062f645fde67eecb0c4b0e2bcd7b81`;

// get search form elemnt 
const searchform = document.querySelector("#search-form");

// submit search form 
searchform.addEventListener('submit', fetchMovie);



// fetch movie from api
function fetchMovie(e) {
    e.preventDefault();
    const searchtext = document.getElementById("searchtext").value;
    var fetchMovieUrl ; 
    if(searchtext.indexOf(",") == -1){
        //var fetchMovieUrl = myapi +`&query=${searchtext}&page=1`;
        var fetchMovieUrl = `http://127.0.0.1:5000/movies/${searchtext}`
    }else{
        const features = searchtext.split(",");
        // rating year genre
        if(features.length == 3){
            const rate = parseInt(features[0]);
            const year = parseInt(features[1]);
            const genre = genres[features[2]];
            var fetchMovieUrl = myapi2+`&sort_by=popularity.desc&page=1&year=${year}&vote_average.gte=${rate}&with_genres=${genre}`;
        }else{
            if (features[0].length < 4){ //rating
                const rate = parseInt(features[0]);
                if(!isNaN(Number(features[1]))){ // year
                    const year = parseInt(features[1]);
                    var fetchMovieUrl = myapi2 + `&sort_by=popularity.desc&page=1&year=${year}&vote_average.gte=${rate}`;  
                }else{

                    const genre = genres[features[1]];
                    var fetchMovieUrl = myapi2 + `&sort_by=popularity.desc&page=1&vote_average.gte=${rate}&with_genres=${genre}`;

                    }
            }else{
                const year = parseInt(features[0]);
                const genre = genres[features[1]];
                var fetchMovieUrl = myapi2 + `&sort_by=popularity.desc&page=1&year=${year}&with_genres=${genre}`;
                }
        }
    }
    console.log(fetchMovieUrl);
    fetch(fetchMovieUrl)
        .then(res => res.json())
        .then(data => showmovie(data))
        .catch(err => console.log(err));
}




function showmovie(movies) {

    const results = document.querySelector("#showtable");
    results.innerHTML = "";


    // test
    const movie = movies[0];
    
    //get review 
    //const fetchreviewUrl =`https://api.themoviedb.org/3/movie/${id}/reviews?api_key=e3062f645fde67eecb0c4b0e2bcd7b81&language=en-US&page=1`
    //fetch(fetchreviewUrl)
        //.then(res => res.json())
        //.then(data => console.log(data.results))

    const div = document.createElement("div");
    div.classList.add("card");
    div.innerHTML = `
    <img src="#" class="card-img-top" alt="no picture">
    <div class="card-body">
        <h5 class="card-title">${movie.title} (${movie.release_date.split('-', 1)})</h5>
        <p class="card-text">${movie.overview}
    </div>
    <ul class="list-group list-group-flush">
        <li class="list-group-item">Rating: ${movie.vote_average}</li>
        <li class="list-group-item">Genres: </li>
        <li class="list-group-item"></li>
    </ul>
    <div class="card-body">    
        
    </div>`;//<a href="${movie.homepage}" class="card-link">view review</a>
    results.appendChild(div);


    /// test end 
    /*
    for(let i = 0 ; i < movies.length; i++){
        const movie = movies[i];
        const id = movie.id;
        
        //get review 
        //const fetchreviewUrl =`https://api.themoviedb.org/3/movie/${id}/reviews?api_key=e3062f645fde67eecb0c4b0e2bcd7b81&language=en-US&page=1`
        //fetch(fetchreviewUrl)
            //.then(res => res.json())
            //.then(data => console.log(data.results))

        const div = document.createElement("div");
        div.classList.add("card");
        div.innerHTML = `
        <img src="http://image.tmdb.org/t/p/w185/${movie.poster_path}" class="card-img-top" alt="no picture">
        <div class="card-body">
            <h5 class="card-title">${movie.title} (${movie.release_date.split('-', 1)})</h5>
            <p class="card-text">${movie.overview}
        </div>
        <ul class="list-group list-group-flush">
            <li class="list-group-item">Rating: ${movie.vote_average}</li>
            <li class="list-group-item">Genres: </li>
            <li class="list-group-item"></li>
        </ul>
        <div class="card-body">    
            
        </div>`;//<a href="${movie.homepage}" class="card-link">view review</a>
        results.appendChild(div);
        */
    //}
}