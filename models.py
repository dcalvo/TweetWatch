from app import db
from sqlalchemy.dialects.postgresql import JSON


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    tweet = db.Column(db.String())
    sentiment = db.Column(JSON)
    
    def __init__(self, tweet, sentiment):
        self.tweet = tweet
        self.sentiment = sentiment

    def __repr__(self):
        return '<id {}>'.format(self.id)