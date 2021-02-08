import os
import requests
import tweepy
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

TWEETS_TO_SEARCH = 100
PREVIOUS_RESULT_NUM_TO_DISPLAY = 15
# Returns tweets that are BELOW the threshold
SENTIMENT_THRESHOLD = -0.8


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
analyzer = SentimentIntensityAnalyzer()

auth = tweepy.AppAuthHandler(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'])
api = tweepy.API(auth, wait_on_rate_limit=True)

from models import Tweet

def get_negative_tweets(search):
    results = []
    tweets = []
    for tweet in tweepy.Cursor(api.search, lang="en", result_type="recent", q=search).items(TWEETS_TO_SEARCH):
        score = analyzer.polarity_scores(tweet.text)
        if score["compound"] < SENTIMENT_THRESHOLD:
            results.append((tweet.id_str, tweet.text, score))
    for tweet in results:
        result = Tweet(
            url="https://twitter.com/twitter/statuses/" + tweet[0],
            text=tweet[1],
            sentiment=tweet[2]
        )
        tweets.append(result)
    return tweets

def get_previous_results(num):
    previous_results = []
    tweets = Tweet.query.order_by(Tweet.id.desc()).limit(num).all()
    for tweet in tweets:
        previous_results.append((tweet.url, tweet.text, tweet.sentiment, tweet.compound))
    return previous_results

@app.route('/', methods=['GET', 'POST'])
def index():
    tweets = []
    errors = []
    results = []
    previous_results = get_previous_results(PREVIOUS_RESULT_NUM_TO_DISPLAY)
    if request.method == "POST":
        try:
            search = request.form['search']
            tweets = get_negative_tweets(search)
        except Exception as e:
            print(e)
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
        if tweets:
            try:
                for tweet in tweets:
                    db.session.add(tweet)
                    results.append((tweet.url, tweet.text, tweet.sentiment, tweet.compound))
                db.session.commit()
            except:
                errors.append("Unable to add item to database.")

    return render_template('index.html', errors=errors, results=results, previous_results=previous_results)



if __name__ == '__main__':
    app.run()