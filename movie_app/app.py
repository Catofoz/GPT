from flask import Flask, render_template_string, request
import os
import random
import string
import requests

app = Flask(__name__)

OMDB_API_KEY = os.environ.get('OMDB_API_KEY')
if not OMDB_API_KEY:
    raise RuntimeError('Please set the OMDB_API_KEY environment variable.')

TOP_MOVIES_BY_GENRE = {
    'action': [
        'Mad Max: Fury Road',
        'Die Hard',
        'The Dark Knight',
        'Gladiator',
        'The Matrix',
        'Terminator 2: Judgment Day',
        'Aliens',
        'Inception',
        'Raiders of the Lost Ark',
        'John Wick'
    ],
    'comedy': [
        'Some Like It Hot',
        'Monty Python and the Holy Grail',
        'Groundhog Day',
        'The Big Lebowski',
        'Superbad',
        'Anchorman: The Legend of Ron Burgundy',
        'Airplane!',
        'Ghostbusters',
        'The Grand Budapest Hotel',
        'Shaun of the Dead'
    ],
    'drama': [
        'The Shawshank Redemption',
        'The Godfather',
        'Forrest Gump',
        'Fight Club',
        'Schindler\'s List',
        '12 Angry Men',
        'Parasite',
        'The Green Mile',
        'Whiplash',
        'The Social Network'
    ],
    'sci-fi': [
        'Blade Runner 2049',
        'Interstellar',
        'Back to the Future',
        '2001: A Space Odyssey',
        'Star Wars: Episode IV - A New Hope',
        'Ex Machina',
        'Eternal Sunshine of the Spotless Mind',
        'Arrival',
        'Inception',
        'The Matrix'
    ]
}

INDEX_TEMPLATE = """
<!doctype html>
<title>Movie Search</title>
<h1>Movie Search</h1>
<form method="get" action="/">
    <input type="text" name="q" placeholder="Enter movie title" required>
    <input type="submit" value="Search">
</form>
<p><a href="/random">Random movie</a></p>
<p>Top Movies by Genre:</p>
<ul>
{% for g in genres %}
    <li><a href="/top/{{ g }}">{{ g.title() }}</a></li>
{% endfor %}
</ul>
{% if movie %}
    <h2>{{ movie.Title }} ({{ movie.Year }})</h2>
    <p><strong>IMDB Rating:</strong> {{ movie.imdbRating }}</p>
    <p><strong>Plot:</strong> {{ movie.Plot }}</p>
{% elif error %}
    <p style="color: red;">{{ error }}</p>
{% endif %}
"""

TOP_TEMPLATE = """
<!doctype html>
<title>Top 10 {{ genre.title() }} Movies</title>
<h1>Top 10 {{ genre.title() }} Movies</h1>
{% if error %}
<p style="color: red;">{{ error }}</p>
{% else %}
<ol>
{% for m in movies %}
    <li>{{ m.Title }} ({{ m.Year }}) - Rated {{ m.imdbRating }}</li>
{% endfor %}
</ol>
{% endif %}
<p><a href="/">Back</a></p>
"""

RANDOM_TEMPLATE = """
<!doctype html>
<title>Random Movie</title>
<h1>Random Movie</h1>
{% if movie %}
    <h2>{{ movie.Title }} ({{ movie.Year }})</h2>
    <p><strong>IMDB Rating:</strong> {{ movie.imdbRating }}</p>
    <p><strong>Plot:</strong> {{ movie.Plot }}</p>
{% elif error %}
    <p style="color: red;">{{ error }}</p>
{% endif %}
<p><a href="/">Back</a></p>
"""

@app.route('/', methods=['GET'])
def index():
    query = request.args.get('q')
    movie = None
    error = None
    if query:
        params = {
            'apikey': OMDB_API_KEY,
            't': query
        }
        try:
            resp = requests.get('http://www.omdbapi.com/', params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if data.get('Response') == 'True':
                movie = data
            else:
                error = data.get('Error', 'Movie not found.')
        except requests.RequestException:
            error = 'Error fetching data from OMDB.'
    return render_template_string(INDEX_TEMPLATE, movie=movie, error=error, genres=TOP_MOVIES_BY_GENRE.keys())

@app.route('/top/<genre>')
def top_movies(genre):
    titles = TOP_MOVIES_BY_GENRE.get(genre.lower())
    movies = []
    error = None
    if not titles:
        error = 'Genre not found.'
    else:
        for title in titles:
            params = {'apikey': OMDB_API_KEY, 't': title}
            try:
                resp = requests.get('http://www.omdbapi.com/', params=params, timeout=5)
                resp.raise_for_status()
                data = resp.json()
                if data.get('Response') == 'True':
                    movies.append(data)
            except requests.RequestException:
                error = 'Error fetching data from OMDB.'
                break
    return render_template_string(TOP_TEMPLATE, movies=movies, genre=genre, error=error)

@app.route('/random')
def random_movie():
    movie = None
    error = None
    for _ in range(5):
        letter = random.choice(string.ascii_lowercase)
        params = {'apikey': OMDB_API_KEY, 's': letter}
        try:
            resp = requests.get('http://www.omdbapi.com/', params=params, timeout=5)
            resp.raise_for_status()
            results = resp.json()
            if results.get('Search'):
                choice = random.choice(results['Search'])
                imdb_id = choice['imdbID']
                params = {'apikey': OMDB_API_KEY, 'i': imdb_id}
                resp = requests.get('http://www.omdbapi.com/', params=params, timeout=5)
                resp.raise_for_status()
                data = resp.json()
                if data.get('Response') == 'True':
                    movie = data
                    break
        except requests.RequestException:
            error = 'Error fetching data from OMDB.'
            break
    if not movie and not error:
        error = 'Could not find a random movie.'
    return render_template_string(RANDOM_TEMPLATE, movie=movie, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
