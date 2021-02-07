import os
import requests
#import tweepy
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

TWEETS_TO_SEARCH = 5
PREVIOUS_RESULT_NUM_TO_DISPLAY = 15


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
analyzer = SentimentIntensityAnalyzer()

# auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
# api = tweepy.API(auth)

from models import Tweet

def get_negative_tweets(url, num):
    # for tweet in tweepy.Cursor(api.search, q='tweepy').items(10):
    #     print(tweet.text)
    score = analyzer.polarity_scores(url)
    results = []
    for i in range(num):
        result = Tweet(
            url=None,
            text=url,
            sentiment=score
        )
        results.append(result)
    return results

def get_previous_results(num):
    previous_results = []
    tweets = Tweet.query.order_by(Tweet.id.desc()).limit(num).all()
    for tweet in tweets:
        previous_results.append((tweet.url, tweet.text, tweet.sentiment, tweet.compound))
    return previous_results

@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = []
    previous_results = get_previous_results(PREVIOUS_RESULT_NUM_TO_DISPLAY)
    if request.method == "POST":
        try:
            url = request.form['url']
            tweets = get_negative_tweets(url, TWEETS_TO_SEARCH)
            print(results)
        except:
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