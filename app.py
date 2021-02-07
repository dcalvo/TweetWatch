import os
import requests
#import tweepy
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
analyzer = SentimentIntensityAnalyzer()

from models import Tweet


@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = []
    if request.method == "POST":
        # get url that the user has entered
        try:
            url = request.form['url']
            score = analyzer.polarity_scores(url)
            #r = requests.get(url)
            #print(r.text)
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
        if score:
            try:
                result = Tweet(
                    url=None,
                    text=url,
                    sentiment=score
                )
                db.session.add(result)
                db.session.commit()
            except:
                errors.append("Unable to add item to database.")
    tweets = Tweet.query.order_by(Tweet.id.desc()).limit(15).all()
    for tweet in tweets:
        results.append((tweet.url, tweet.text, tweet.sentiment, tweet.compound))
    return render_template('index.html', errors=errors, results=results)



if __name__ == '__main__':
    app.run()