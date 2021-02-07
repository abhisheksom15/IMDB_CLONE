from app import db
from flask_login import UserMixin
from app import wb
if(True):
    class User(UserMixin,db.Model):
        id=db.Column(db.Integer,primary_key=True)
        username=db.Column(db.String(20),nullable=False,unique=True)
        name=db.Column(db.String(60),nullable=False)
        public_id=db.Column(db.String(60),nullable=False)
        isAdmin=db.Column(db.Boolean,default=False)
        password=db.Column(db.String(128),nullable=False)
        def __str__(self):
            return str(self.username)
    class Movies(db.Model):
        __searchable__=['name','director']
        id=db.Column(db.Integer,primary_key=True)
        name=db.Column(db.String(200),nullable=False)
        imdb_score=db.Column(db.Numeric(2,2),default=0.0)
        popularity99=db.Column(db.Numeric(2,2),default=0.0)
        director=db.Column(db.String(80),nullable=False)
        def __str__(self):
            return str(self.name)
    class MovieGenre(db.Model):
        MovieID=db.Column(db.Integer,db.ForeignKey('movies.id'),primary_key=True)
        Genre=db.Column(db.String(20),primary_key=True)
        def __str__(self):
            return str(self.GenreID+str(self.MovieID))
db.create_all()
db.session.commit()
