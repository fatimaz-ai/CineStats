import requests
import matplotlib.pyplot as plt
import os
API_KEY = os.environ.get("TMDB_API_KEY")
GENRE_MAP = {  ##tmbd has genre ids so just defining them here by a dict
    28: "Action", 12: "Adventure", 16: "Animation",
    35: "Comedy", 80: "Crime", 99: "Documentary",
    18: "Drama", 10751: "Family", 14: "Fantasy",
    27: "Horror", 10402: "Music", 9648: "Mystery",
    10749: "Romance", 878: "Sci-Fi", 53: "Thriller",
    10752: "War", 37: "Western"
}
url=f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US&page=1"
response=requests.get(url) ##requests server for popular movies
data=response.json()  ##converts data into python dict, but messy
#print(data) ##will just print messy stuff, lets do some formatting:

##a bit inefficient
# for k,v in data.items():
#     if k=='results':
#         for i in range(len(v)):
#           print(v[i])

##correct!  BUT THIS IS JUST FOR POPULAR MOVIES
# movies=data["results"]  ##directly get the key 'results' which has 1 huge list, with dict of movies inside it
# for m in movies: ##going thru that huge list ONCE
#     print(m['title'],"|", m['vote_average'], "|", m['release_date'])

##TO SEARCH FOR ANY MOVIE BUT JUST PRINTING
# def search_movie(title):
#     url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
#     response=requests.get(url)
#     data=response.json()
#     movies=data['results']
#     for m in movies:
#         print(m['title'],"|", m['vote_average'], "|", m['release_date'])
# search_movie("inception")

##MAKE 2 LISTS AND PLOTTING THEM
# def search_movie(title):
#     url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
#     response=requests.get(url)
#     data=response.json()
#     movies=data['results']
#     titles=[]
#     ratings=[]
#     for m in movies:
#         if m['vote_average']>0 and m['vote_count']>10: ##if the ratings reallly matter
#            titles.append(m['title'])
#            ratings.append(m['vote_average'])
#     paried=sorted(zip(ratings,titles), reverse=True) ##sorts highest rated first
#     ratings=[r for r, t in paried]
#     titles=[t for r, t in paried]
#     return titles,ratings
# movie_name='inception'
# titles,ratings=search_movie(movie_name)
# plt.figure(figsize=(14,6))
# plt.bar(titles,ratings)
# plt.ylim(0, 10)
# plt.title(f"Ratings for '{movie_name}' search results")
# plt.xlabel("Movie Title")
# plt.ylabel("Vote Average")
# plt.xticks(rotation=90,fontsize=8)
# plt.show()

##genre function
def get_genres(title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
    response=requests.get(url)
    data=response.json()
    movies=data['results']
    if len(movies)==0:
        return []
    top_result=movies[0]
    genre_ids=top_result['genre_ids']
    genres=[]
    for id in genre_ids:
        if id in GENRE_MAP:
            genres.append(GENRE_MAP[id])
    return genres
print(get_genres('inception'))

##personality function
def movie_personality(movie_list):
    all_genres=[]
    for movie in movie_list:
        genres=get_genres(movie)
        all_genres.extend(genres)  ##pulls items out of each list and adds them
    
    if len(all_genres)==0:
        return "We couldn't figure out your taste!"
    
    genre_count={}
    for genre in all_genres:   ##looping thru those added items and counting easily
        if genre in genre_count:
            genre_count[genre]+=1
        else:
            genre_count[genre]=1
    
    top_genre=max(genre_count, key=genre_count.get)
    
    personality = {
        "Action": "The Adrenaline Chaser",
        "Thriller": "The Edge of Your Seat type",
        "Sci-Fi": "The Mind Bender",
        "Drama": "The Deep Feeler",
        "Comedy": "The Good Vibes Only",
        "Horror": "The Thrill Seeker",
        "Romance": "The Hopeless Romantic",
        "Crime": "The Dark Side Explorer",
        "Adventure": "The Wanderer",
        "Animation": "The Young at Heart",
        "Mystery": "The Puzzle Solver",
        "Fantasy": "The Dreamer"
    }

    quotes = {
    "Action": "Some men aren't looking for anything logical. They can't be bought, bullied, or negotiated with. — The Dark Knight",
    "Thriller": "The greatest trick the devil ever pulled was convincing the world he didn't exist. — The Usual Suspects",
    "Sci-Fi": "We are just an advanced breed of monkeys on a minor planet of a very average star. — Stephen Hawking",
    "Drama": "You only begin to discover what life is when you plant your feet firmly and decide to stop running. — Atonement",
    "Comedy": "Life is what happens when you're busy making other plans. — John Lennon",
    "Horror": "We make up horrors to help us cope with the real ones. — Stephen King",
    "Romance": "I have waited for this opportunity for more than half a century. — La La Land",
    "Crime": "All it takes is one bad day. — The Killing Joke",
    "Adventure": "Not all those who wander are lost. — Tolkien",
    "Animation": "Adventure is out there. — Up",
    "Mystery": "The world is full of obvious things which nobody by any chance ever observes. — Sherlock Holmes",
    "Fantasy": "Even the smallest person can change the course of the future. — LOTR"
}

    quote = quotes.get(top_genre, "Cinema is a mirror by which we often see ourselves.")
    
    label=personality.get(top_genre, "The Eclectic Viewer")

    ##pie chart for personality
    label = personality.get(top_genre, "The Eclectic Viewer")
    quote = quotes.get(top_genre, "Cinema is a mirror by which we often see ourselves.")
    
    result = f"Your top genre is {top_genre} — you are: {label}\n\n\"{quote}\""
    
    labels = list(genre_count.keys())
    sizes = list(genre_count.values())
    plt.figure(figsize=(8,8))
    plt.pie(sizes, labels=None, autopct='%1.1f%%', startangle=140)
    plt.legend(labels, loc="best", fontsize=9)
    plt.title("Your Movie Genre Breakdown")
    plt.show()  
    
    return f"""
    ✦ ✦ ✦  YOU ARE: {label.upper()}  ✦ ✦ ✦

    Your soul gravitates toward {top_genre}.

    "{quote}"
    """
my_movies=["oppenheimer","atonement","hamnet","the shining","the house that jack built","Interstellar", "The Dark Knight"]
print(movie_personality(my_movies))
