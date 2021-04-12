import json

from app import db
# from sqlalchemy.dialects.postgresql import JSON


class Tweet(db.Model):
    __tablename__ = 'tweets'

    id            = db.Column(db.Integer, primary_key=True)
    text          = db.Column(db.String())
    sentiment_p   = db.Column(db.Float)
    sentiment_l   = db.Column(db.Float)
    sentiment_n   = db.Column(db.Float)
    compound      = db.Column(db.Float)
    sent_bucket   = db.Column(db.Integer)
    retweet_count = db.Column(db.Integer)
    reply_count   = db.Column(db.Integer)
    like_count    = db.Column(db.Integer)
    quote_count   = db.Column(db.Integer)
    user_id       = db.Column(db.Integer)
    user_location = db.Column(db.String())
    u_followers_c = db.Column(db.Integer)
    u_following_c = db.Column(db.Integer)
    u_tweet_c     = db.Column(db.Integer)
    u_listed_c    = db.Column(db.Integer)
    time_created  = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    time_updated  = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

    def __init__(self, tweet, score):

        self.id            = int(tweet['data']['id'])
        self.text          = tweet['data']['text']
        self.sentiment_p   = score['pos']
        self.sentiment_l   = score['neu']
        self.sentiment_n   = score['neg']
        self.compound      = score['compound']
        self.sent_bucket   = int(score['compound'] // 0.2)
        self.retweet_count = tweet['data']['public_metrics']['retweet_count']
        self.reply_count   = tweet['data']['public_metrics']['reply_count']
        self.like_count    = tweet['data']['public_metrics']['like_count']
        self.quote_count   = tweet['data']['public_metrics']['quote_count']
        self.user_id       = int(tweet['data']['includes']['users'][0]['id'])
        self.user_location = tweet['data']['includes']['users'][0]['location']
        self.u_followers_c = tweet['data']['includes']['users'][0]['public_metrics']['followers_count']
        self.u_following_c = tweet['data']['includes']['users'][0]['public_metrics']['following_count']
        self.u_tweet_c     = tweet['data']['includes']['users'][0]['public_metrics']['tweet_count']
        self.u_listed_c    = tweet['data']['includes']['users'][0]['public_metrics']['listed_count']
        self.time_created  = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
        self.time_updated  = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

    def __repr__(self):
        return '<id {}>'.format(self.id)


class TweetO(db.Model):
    __tablename__ = 'tweets_o'

    id        = db.Column(db.Integer, primary_key=True)
    url       = db.Column(db.String())
    text      = db.Column(db.String())
    sentiment = db.Column(db.String())
    compound  = db.Column(db.Float)
    retweets  = db.Column(db.Integer)

    def __init__(self, url, text, sentiment, retweets):
        self.text = text
        self.url = url
        self.sentiment = json.dumps(sentiment)
        self.compound = sentiment["compound"]
        self.retweets = retweets

    def __repr__(self):
        return '<id {}>'.format(self.id)


db.Model.metadata.create_all(db.engine)