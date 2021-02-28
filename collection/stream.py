import json
import requests
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from models import Tweet, Base

url = 'https://api.twitter.com/2/tweets/sample/stream' \
      '?tweet.fields=public_metrics,lang,geo,created_at,referenced_tweets' \
      '&expansions=author_id,referenced_tweets.id,referenced_tweets.id.author_id' \
      '&user.fields=public_metrics,location'
headers = {"Authorization": "Bearer " + os.environ['TWITTER_BEARER_TOKEN']}

r = requests.get(url, headers=headers, stream=True)

analyzer = SentimentIntensityAnalyzer()

rt_threshold = 1000 # configure me

engine = create_engine('sqlite:///tweets2.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

num_added = 0

def add_tweet(tw, user, sc):
    global num_added
    if 'location' in user.keys():
        loc = user['location']
    else:
        loc = "NOT PROVIDED"
    new_tweet = Tweet(
        id            = int(tw['id']),
        text          = tw['text'],
        sentiment_p   = sc['pos'],
        sentiment_l   = sc['neu'],
        sentiment_n   = sc['neg'],
        compound      = sc['compound'],
        sent_bucket   = int(sc['compound'] // 0.2),
        retweet_count = tw['public_metrics']['retweet_count'],
        reply_count   = tw['public_metrics']['reply_count'],
        like_count    = tw['public_metrics']['like_count'],
        quote_count   = tw['public_metrics']['quote_count'],
        user_id       = int(user['id']),
        user_location = loc,
        u_followers_c = user['public_metrics']['followers_count'],
        u_following_c = user['public_metrics']['following_count'],
        u_tweet_c     = user['public_metrics']['tweet_count'],
        u_listed_c    = user['public_metrics']['listed_count']
    )
    session.add(new_tweet)
    session.commit()
    num_added += 1

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
            print(tweet['data']['public_metrics'])
            print(tweet['data']['referenced_tweets'])
            print(tweet['includes']['tweets'])
            print(tweet['includes']['users'])
            if 'referenced_tweets' in tweet['data'].keys() and len(tweet['data']['referenced_tweets']) > 0:
                for ref_tw in tweet['data']['referenced_tweets']:
                    if ref_tw['type'] == 'retweeted':
                        ref_tw_details = next((tw for tw in tweet['includes']['tweets'] if tw['id'] == ref_tw['id'])
                                              , None)
                        if ref_tw_details is not None:
                            ref_tw_user_details = next(
                                (ur for ur in tweet['includes']['users'] if ur['id'] == ref_tw_details['author_id'])
                                , None)
                            score = analyzer.polarity_scores(tweet['data']['text'])
                            add_tweet(ref_tw_details, ref_tw_user_details, score)

            else:
                score = analyzer.polarity_scores(tweet['data']['text'])
                add_tweet(tweet['data'], tweet['includes']['users'][0], score)

    else:
        print('heartbeat')
    if i % 10 == 0:
        print(i, 'tweets,', num_added, 'inserted')