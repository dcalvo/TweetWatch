import json
import requests
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from models import Tweet, Base

url = 'https://api.twitter.com/2/tweets/sample/stream?tweet.fields=public_metrics,lang,geo,created_at' \
      '&expansions=author_id&user.fields=public_metrics,location'
headers = {"Authorization": "Bearer " + os.environ['TWITTER_BEARER_TOKEN']}

r = requests.get(url, headers=headers, stream=True)

analyzer = SentimentIntensityAnalyzer()

rt_threshold = 1000 # configure me

engine = create_engine('sqlite:///tweets.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

num_added = 0

for i, line in enumerate(r.iter_lines()):
    if line:
        decoded_line = line.decode('utf-8')
        tweet = json.loads(decoded_line)

        if 'connection_issue' in tweet.keys():
            print(json.dumps(tweet, indent=4))
            continue

        rt_count = tweet['data']['public_metrics']['retweet_count']
        lang = tweet['data']['lang']

        if rt_count > rt_threshold and lang == 'en':
            score = analyzer.polarity_scores(tweet['data']['text'])
            if ('location' in tweet['includes']['users'][0].keys()):
                loc = tweet['includes']['users'][0]['location']
            else:
                loc = "NOT PROVIDED"
            new_tweet = Tweet(
                id            = int(tweet['data']['id']),
                text          = tweet['data']['text'],
                sentiment_p   = score['pos'],
                sentiment_l   = score['neu'],
                sentiment_n   = score['neg'],
                compound      = score['compound'],
                sent_bucket   = int(score['compound'] // 0.2),
                retweet_count = tweet['data']['public_metrics']['retweet_count'],
                reply_count   = tweet['data']['public_metrics']['reply_count'],
                like_count    = tweet['data']['public_metrics']['like_count'],
                quote_count   = tweet['data']['public_metrics']['quote_count'],
                user_id       = int(tweet['includes']['users'][0]['id']),
                user_location = loc,
                u_followers_c = tweet['includes']['users'][0]['public_metrics']['followers_count'],
                u_following_c = tweet['includes']['users'][0]['public_metrics']['following_count'],
                u_tweet_c     = tweet['includes']['users'][0]['public_metrics']['tweet_count'],
                u_listed_c    = tweet['includes']['users'][0]['public_metrics']['listed_count']
            )
            session.add(new_tweet)
            session.commit()
            num_added += 1

    else:
        print('heartbeat')
    if i % 10 == 0:
        print(i, 'tweets,', num_added, 'inserted')