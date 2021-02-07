from app import db
from sqlalchemy.dialects.postgresql import JSON


class Tweet(db.Model):
    __tablename__ = 'tweets'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String())
    sentiment = db.Column(JSON)
    
    def __init__(self, text, sentiment):
        self.text = text
        self.sentiment = sentiment

    def __repr__(self):
        return '<id {}>'.format(self.id)