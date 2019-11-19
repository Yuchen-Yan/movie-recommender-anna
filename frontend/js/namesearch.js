console.log("linked");

// get search form elemnt 
const searchform = document.querySelector("#search-form");

// submit search form 
searchform.addEventListener('submit', fetchMusic);



// fetch music from api
function fetchMusic(e) {
    e.preventDefault();
    const searchtext = document.getElementById("searchtext").value; 
    const fetchMusicUrl = `https://api.themoviedb.org/3/search/movie?api_key=e3062f645fde67eecb0c4b0e2bcd7b81&query=${searchtext}&page=1`;
    fetch(fetchMusicUrl)
        .then(res => res.json())
        .then(data => showmovie(data.results))
        .catch(err => console.log(err));
}


function showmovie(movies) {

    const results = document.querySelector("#showtable");
    results.innerHTML = "";

    for(let i = 0 ; i < movies.length; i++){
        const movie = movies[i];
        
        const div = document.createElement("div");
        div.classList.add("card");
        div.innerHTML = `
        <img src="http://image.tmdb.org/t/p/w185/${movie.poster_path}" class="card-img-top" alt="hahah">
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
        </div>`;//<a href="${movie.homepage}" class="card-link">more info</a>
        results.appendChild(div);
    }
}