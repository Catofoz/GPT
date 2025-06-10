# Movie Search Web App

This simple Flask app lets you search for movies using the [OMDB API](https://www.omdbapi.com/).
It returns the movie title, IMDB rating, and plot summary.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Obtain an API key from [OMDB](https://www.omdbapi.com/) and set it as an environment variable:
   ```bash
   export OMDB_API_KEY=your_key_here
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Visit `http://localhost:5000` in your browser and search for a movie title.

5. Use the "Random movie" link on the home page to get a random suggestion.
6. Choose one of the listed genres to see the top 10 movies for that genre.
