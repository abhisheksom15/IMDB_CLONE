from datetime import datetime
from flask import Flask,jsonify,Blueprint,request
from models import Movies,MovieGenre
from auth import admin_token_required
from app import db
import json
API = Blueprint('API', __name__, url_prefix='/API')

@API.route('/')
def checkServer():
    return jsonify({"status":"Server is running"})

@API.route('/loadMovies',methods=["POST"])
@admin_token_required
def loadMoviesJson(current_user):
    """
    **Access to admin only**
    Will Load movies in Bulk, pass JSON with array of movies and it will load all the movies in the DB.
    Takes:JSON
    Respond: Message with whether movies are added or not
    """
    moviesListJson=request.get_data()
    MoviesList = json.loads(moviesListJson)
    Result=""
    for movie in MoviesList:
        popularity=movie["99popularity"]
        director=movie["director"]
        genres=movie["genre"]
        imdb_score=movie["imdb_score"]
        movieName=movie["name"]
        movieRecord=Movies(name=movieName,imdb_score=imdb_score,popularity99=popularity,director=director)
        db.session.add(movieRecord)
        db.session.commit()
        for genre in genres:
            movieGenre=MovieGenre(MovieID=movieRecord.id,Genre=genre)
            #print(genreRecord.id,genreRecord.Genre,movieGenre.id)
            db.session.add(movieGenre)
        db.session.commit()
        Result+=(movieName+" added successful to Database # ")
    return jsonify({"result":Result})

@API.route('/SearchMovie',methods=["GET"])
def SearchMovie():
    """
    **Access to everyone**
    Will search movies on the basis of Movies Name and director name.
    Input: query paramter in url which will perform full text based search on movie name and director name.
    Example:- search harry and it will give result like harry potter movies and director with name harry smith.
    Respond: Message with JSON with movie details
    """
    query=request.args.get('query')
    if not query:
        return {"error":401, "message":"query is missing"}
    if(len(query)<3):
        return jsonify({"error":"401","message":"Please search with 3 or more words"})
    movies=Movies.search_query(query).all()
    if not movies:
        return jsonify({"error":"401","message":"Record not found/ Search Failed"})
    result=[]
    for movie in movies:
        movieGenre=[]
        genres=MovieGenre.query.filter_by(MovieID=movie.id).all()
        for genre in genres:
            movieGenre.append(genre.Genre)
        result.append({"id":movie.id,"movie":movie.name,"director":movie.director,"imdb_score":str(movie.imdb_score),"99popularity":str(movie.popularity99),"genre":movieGenre})
    return jsonify(result)

@API.route('/Movie/<movieID>',methods=["GET"])
def getMovieByID(movieID):
    """
    **Access to everyone**
    Will search movies on the basis of Movie ID.
    Input: Movie ID in url which will perform search on movie ID.
    Example:- search mpvieID=2 and it will give result with movie ID 2.
    Respond: Message with JSON with movie details
    """
    movie=Movies.query.filter_by(id=movieID).first()
    if movie:
        return jsonify({"error":"401","message":"Record not found, enter valid movie ID"})
    movieGenre=[]
    genres=MovieGenre.query.filter_by(MovieID=movieID).all()
    for genre in genres:
        movieGenre.append(genre.Genre)
    result={"id":movie.id,"movie":movie.name,"director":movie.director,"imdb_score":str(movie.imdb_score),"99popularity":str(movie.popularity99),"genre":movieGenre}
    return jsonify(result)

@API.route('/MovieGenre/<genre>',methods=["GET"])
def getMovieByGenre(genre):
    """
    **Access to everyone**
    Will search movies on the basis of Movie ID.
    Input: Movie ID in url which will perform search on movie ID.
    Example:- search mpvieID=2 and it will give result with movie ID 2.
    Respond: Message with JSON with movie details
    """
    movieGenreRecord=MovieGenre.query.filter_by(Genre=genre).all()
    if not movieGenreRecord:
        return jsonify({"error":"401","message":"No Record found with Genre "+str(genre)})
    result=[]
    for mGenre in movieGenreRecord:
        movie=Movies.query.filter_by(id=mGenre.MovieID).first()
        movieGenre=[]
        genres=MovieGenre.query.filter_by(MovieID=mGenre.MovieID).all()
        for genre in genres:
            movieGenre.append(genre.Genre)
        result.append({"id":movie.id,"movie":movie.name,"director":movie.director,"imdb_score":str(movie.imdb_score),"99popularity":str(movie.popularity99),"genre":movieGenre})
    return jsonify(result)
@API.route('/Movie/<movieID>',methods=["DELETE"])
@admin_token_required
def deleteMovieByID(current_user,movieID):
    """
    **Access to admin only**
    Will search movies on the basis of Movie ID and delete them if it exist.
    Input: Movie ID in url which will perform deletion on movie ID.
    Respond: Message with status
    """
    movie=Movies.query.filter_by(id=movieID).first()
    if not movie:
        return jsonify({"error":"401","message":"Record not found, enter valid movie ID to Delete"})
    try:
        genres=MovieGenre.query.filter_by(MovieID=movieID).all()
        for genre in genres:
            #genreRecord=Genre.query.all()
            db.session.delete(genre)
        db.session.delete(movie)
        db.session.commit()
        result={"message":str(movieID)+" ID Record Deleted successfully!"}
    except:
        result={"message":str(movieID)+" ID Record Deletion Failed!!!"}
    return jsonify(result)

@API.route('/updateMovie/<movieID>',methods=["POST"])
@admin_token_required
def updateMovieByID(current_user,movieID):
    """
    **Access to admin only**
    Will search movies on the basis of Movie ID and update them if it exist with json passed in data.
    Input: Movie ID in url which will perform updation on movie ID.
    Respond: Message with status
    """
    data=request.get_json()
    if not data:
        return jsonify({"error":"401","message":"Please provide Data in JSON format"})
    movie=Movies.query.filter_by(id=movieID).first()
    if not movie:
        return jsonify({"error":"401","message":"Record not found, enter valid movie ID to Update"})
    try:
        try:
            name=data['name']
            movie.name=name
        except:
            pass
        try:
            popularity99=data['99popularity']
            movie.popularity99=popularity99
        except:
            pass
        try:
            director=data['director']
            movie.director=director
        except:
            pass
        try:
            imdb_score=data['imdb_score']
            movie.imdb_score=imdb_score
        except:
            pass
        try:
            genres=data['genre']
            genresDel=MovieGenre.query.filter_by(MovieID=movieID).all()
            for genre in genresDel:
                #genreRecord=Genre.query.all()
                db.session.delete(genre)
                db.session.commit()
            for genre in genres:
                movieGenre=MovieGenre(MovieID=movieID,Genre=genre)
                db.session.add(movieGenre)
        except:
            pass
        db.session.commit()
        result={"message":str(movieID)+" ID Record updated successfully!"}
    except:
        #db.session.commit()
        result={"message":str(movieID)+" ID Record updation Failed!!!"}
    return jsonify(result)
