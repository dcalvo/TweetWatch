from app import db
from sqlalchemy.dialects.postgresql import JSON


class Tweet(db.Model):
    __tablename__ = 'tweets'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String())
    text = db.Column(db.String())
    sentiment = db.Column(JSON)
    compound = db.Column(db.Float)
    
    def __init__(self, url, text, sentiment):
        self.url = url
        self.text = text
        self.sentiment = sentiment
        self.compound = sentiment["compound"]

    def __repr__(self):
        return '<id {}>'.format(self.id)