import json
import os
import requests
import tweepy
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import date, timedelta

TWEETS_TO_SEARCH = 100
PREVIOUS_RESULT_NUM_TO_DISPLAY = 15
PREVIOUS_RESULT_TO_TEMP_STORE = 50
# Returns tweets that are BELOW the threshold
SENTIMENT_THRESHOLD = -0.8
DURATION = 0

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
analyzer = SentimentIntensityAnalyzer()

auth = tweepy.AppAuthHandler(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'])
api = tweepy.API(auth, wait_on_rate_limit=True)


from models import TweetO


def get_negative_tweets(search, threshold=SENTIMENT_THRESHOLD, duration=DURATION):
    results = []
    tweets = []
    # Search tweets based on given parameter for strongly opinionated ones
    for tweet in tweepy.Cursor(api.search,
                               lang="en",
                               result_type="recent",
                               q=search,
                               tweet_mode='extended',
                               until=(date.today() - timedelta(days=duration-1)).isoformat()
                               ).items(TWEETS_TO_SEARCH):
        full_text = tweet.retweeted_status.full_text if tweet.retweeted else tweet.full_text
        score = analyzer.polarity_scores(full_text)
        if score["compound"] < threshold:
            results.append((tweet.id_str, full_text, score, tweet.retweet_count, tweet.retweeted))
    # Transform results into Tweet objects
    for tweet in results:
        try:
            result = TweetO(
                url       = "https://twitter.com/twitter/statuses/" + tweet[0],
                text      = tweet[1],
                sentiment = tweet[2],
                retweets  = tweet[3]
            )
            print(json.dumps(tweet[2]), type(json.dumps(tweet[2])))
            print('hi')
            tweets.append((result, tweet[4]))
        except Exception as e:
            print(e)
            print('well hello')
    print('help me')
    return tweets


def get_previous_results():
    previous_results = []
    tweets = TweetO.query.order_by(TweetO.id.desc()).limit(PREVIOUS_RESULT_NUM_TO_DISPLAY).all()
    for tweet in tweets:
        previous_results.append((tweet.url, tweet.text, tweet.sentiment, tweet.compound))
    return previous_results

show_previous_tweets = False

previous_results = []

prev_threshold = -0.8
prev_duration = 0

@app.route('/', methods=['GET', 'POST'])
def index():
    global show_previous_tweets
    global previous_results
    global prev_threshold
    global prev_duration
    tweets = []
    errors = []
    results = []
    search = ""
    if request.method == "POST":
        show_previous_tweets = False
        try:
            search = request.form['search']
            threshold = float(request.form["threshold"])
            duration = int(request.form["duration"])
            tweets = get_negative_tweets(search, threshold, duration)
            prev_threshold = threshold
            prev_duration = duration
        except Exception as e:
            print(e)
            errors.append(
                "Unable to get search. Please make sure it's valid and try again."
            )
        if tweets:
            try:
                for tweet, retweeted in tweets:
                    db.session.add(tweet)
                    results.append((tweet.url, tweet.text, tweet.sentiment, tweet.retweets))
                    print(json.dumps(tweet.sentiment), type(json.dumps(tweet.sentiment)))
                db.session.commit()
            except Exception as e:
                print(e)
                errors.append("Unable to add item to database.")
        previous_results.extend(results)
        # if len(previous_results) > PREVIOUS_RESULT_TO_TEMP_STORE:
        #     previous_results = previous_results[:PREVIOUS_RESULT_TO_TEMP_STORE]

    prev_to_show = get_previous_results() if not previous_results else previous_results[-PREVIOUS_RESULT_NUM_TO_DISPLAY:]

    # print(previous_results)
    return render_template('index.html', errors=errors, results=results, previous_results=prev_to_show,
                           keyword=search, show_prev=show_previous_tweets, thresh=prev_threshold, dur=prev_duration)

@app.route('/button', methods=['GET'])
def button():
    global show_previous_tweets
    show_previous_tweets = not show_previous_tweets
    return redirect("/", code=302)

if __name__ == '__main__':
    app.run()
