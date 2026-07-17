from flask import Flask, request, jsonify, send_from_directory,make_response
import requests

import json
import uuid
import os
import time
from dotenv import load_dotenv
load_dotenv()

#for admin pw
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "a_fallback_default_password")

COMMENTS_FILE = 'comments.json'

##for the feedback/comment stuff
def load_comments():
    if os.path.exists(COMMENTS_FILE):
        with open(COMMENTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_comments(comments):
    with open(COMMENTS_FILE, 'w') as f:
        json.dump(comments, f)

app = Flask(__name__)

import os
API_KEY = os.environ.get("TMDB_API_KEY")

GENRE_MAP = {
    28: "Action", 12: "Adventure", 16: "Animation",
    35: "Comedy", 80: "Crime", 99: "Documentary",
    18: "Drama", 10751: "Family", 14: "Fantasy",
    27: "Horror", 10402: "Music", 9648: "Mystery",
    10749: "Romance", 878: "Sci-Fi", 53: "Thriller",
    10752: "War", 37: "Western"
}

def get_genres(title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
    response = requests.get(url)
    data = response.json()
    movies = data.get('results', [])
    if len(movies) == 0:
        return []
    top_result = movies[0]
    genre_ids = top_result.get('genre_ids', [])
    genres = [GENRE_MAP[gid] for gid in genre_ids if gid in GENRE_MAP]
    return genres

def get_movie_id_and_genres(title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
    response = requests.get(url)
    data = response.json()
    movies = data.get('results', [])
    if not movies:
        return None, []
    top = movies[0]
    genre_ids = top.get('genre_ids', [])
    genres = [GENRE_MAP[gid] for gid in genre_ids if gid in GENRE_MAP]
    return top.get('id'), genres

def get_recommendations_from_movies(movie_list):
    seen_ids = set()
    input_titles_lower = set(m.lower() for m in movie_list)
    candidates = []

    for title in movie_list:
        movie_id, _ = get_movie_id_and_genres(title)
        if not movie_id:
            continue
        rec_url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={API_KEY}"
        rec_response = requests.get(rec_url)
        rec_data = rec_response.json()
        for m in rec_data.get('results', []):
            mid = m.get('id')
            mtitle = m.get('title', '')
            if mid in seen_ids or mtitle.lower() in input_titles_lower:
                continue
            seen_ids.add(mid)
            candidates.append(m)

    candidates.sort(key=lambda m: m.get('vote_average', 0), reverse=True)

    recommendations = []
    for m in candidates[:5]:
        year = m['release_date'][:4] if m.get('release_date') else "N/A"
        poster_path = m.get('poster_path')
        poster_url = f"https://image.tmdb.org/t/p/w200{poster_path}" if poster_path else ""
        recommendations.append({"title": m['title'], "year": year, "poster": poster_url})
    return recommendations

@app.route('/comments', methods=['GET'])
def get_comments():
    user_token = request.cookies.get('user_token', '')
    is_admin = request.cookies.get('admin_token', '') == ADMIN_PASSWORD
    comments = load_comments()

    #process comments to declare ownership flags (dynamically)
    processed = []
    for c in comments:
        comment_copy = c.copy()
        #allows modification if they are the admin OR if their cookie matches the comment token
        comment_copy['can_modify'] = is_admin or (user_token and c.get('token') == user_token)
        processed.append(comment_copy)
    return jsonify(processed)

@app.route('/comments', methods=['POST'])
def post_comment():
    data = request.json
    text = data.get('text', '').strip()

    if not text:
        return jsonify({'error': 'empty comment'}), 400

    #admin login:check if text entry matches password
    if text == ADMIN_PASSWORD:
        resp = make_response(jsonify({'success': True, 'admin_login': True}))
        resp.set_cookie('admin_token', ADMIN_PASSWORD, max_age=31536000, httponly=True)
        return resp

    #device cookies for visitors
    user_token = request.cookies.get('user_token')
    needs_cookie = False
    if not user_token:
        user_token = str(uuid.uuid4())
        needs_cookie = True

    name = data.get('name', '').strip() or 'anonymous'
    comments = load_comments()

    new_comment = {
        'id': str(uuid.uuid4()),
        'name': name,
        'text': text,
        'token': user_token,
        'timestamp': time.time()  #records exact seconds since epoch
    }
    comments.append(new_comment)
    save_comments(comments)

    resp = make_response(jsonify({'success': True}))
    if needs_cookie:
        resp.set_cookie('user_token', user_token, max_age=31536000, httponly=True)
    return resp

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    movie_list = data['movies']

    all_genres = []
    for movie in movie_list:
        genres = get_genres(movie)
        all_genres.extend(genres)

    if len(all_genres) == 0:
        return jsonify({'error': 'Could not find your movies'})

    genre_count = {}
    for genre in all_genres:
        genre_count[genre] = genre_count.get(genre, 0) + 1

    top_genre = max(genre_count, key=genre_count.get)

    personality = {
        "Action": "The Adrenaline Chaser", "Thriller": "The Edge of Your Seat type",
        "Sci-Fi": "The Mind Bender", "Drama": "The Deep Feeler",
        "Comedy": "The Good Vibes Only", "Horror": "The Thrill Seeker",
        "Romance": "The Hopeless Romantic", "Crime": "The Dark Side Explorer",
        "Adventure": "The Wanderer", "Animation": "The Young at Heart",
        "Mystery": "The Puzzle Solver", "Fantasy": "The Dreamer"
    }

    quotes = {
        "Action": "Some men aren't looking for anything logical...",
        "Thriller": "The greatest trick the devil ever pulled...",
        "Sci-Fi": "We are just an advanced breed of monkeys...",
        "Drama": "You only begin to discover what life is when you plant your feet firmly...",
        "Comedy": "Life is what happens when you're busy making other plans.",
        "Horror": "We make up horrors to help us cope with the real ones.",
        "Romance": "I have waited for this opportunity for more than half a century.",
        "Crime": "All it takes is one bad day.",
        "Adventure": "Not all those who wander are lost.",
        "Animation": "Adventure is out there.",
        "Mystery": "The world is full of obvious things...",
        "Fantasy": "Even the smallest person can change the course of the future."
    }

    label = personality.get(top_genre, "The Eclectic Viewer")
    quote = quotes.get(top_genre, "Cinema is a mirror by which we often see ourselves.")

    recommendations = get_recommendations_from_movies(movie_list)

    return jsonify({
        'top_genre': top_genre,
        'label': label,
        'quote': quote,
        'genre_count': genre_count,
        'recommendations': recommendations
    })

@app.route('/comments/delete', methods=['POST'])
def delete_comment():
    data = request.json or {}
    cid = data.get('id')
    user_token = request.cookies.get('user_token', '')
    is_admin = request.cookies.get('admin_token', '') == ADMIN_PASSWORD

    comments = load_comments()
    updated = []
    authorized = False

    for c in comments:
        if c.get('id') == cid:
            if is_admin or c.get('token') == user_token:
                authorized = True
                continue #skips adding it back, deleting it
        updated.append(c)

    if not authorized:
        return jsonify({'error': 'Unauthorized'}), 403

    save_comments(updated)
    return jsonify({'success': True})

@app.route('/comments/edit', methods=['POST'])
def edit_comment():
    data = request.json or {}
    cid = data.get('id')
    new_text = data.get('text', '').strip()
    user_token = request.cookies.get('user_token', '')
    is_admin = request.cookies.get('admin_token', '') == ADMIN_PASSWORD

    if not new_text:
        return jsonify({'error': 'empty comment'}), 400

    comments = load_comments()
    authorized = False

    for c in comments:
        if c.get('id') == cid:
            if is_admin or c.get('token') == user_token:
                c['text'] = new_text
                authorized = True
                break

    if not authorized:
        return jsonify({'error': 'Unauthorized'}), 403

    save_comments(comments)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
