import json
import requests
import os

from enum import Enum
from csv import reader
from datetime import datetime
from sqlalchemy import create_engine, select, insert
from sqlalchemy.orm import sessionmaker

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from models import QueryPolicy, Tweet, Base, DatabaseUrl

url = 'https://api.twitter.com/2/tweets/sample/stream' \
      '?tweet.fields=public_metrics,lang,geo,created_at,referenced_tweets' \
      '&expansions=author_id,referenced_tweets.id,referenced_tweets.id.author_id' \
      '&user.fields=public_metrics,location'
headers = {"Authorization": "Bearer " + os.environ['TWITTER_BEARER_TOKEN']}

r = requests.get(url, headers=headers, stream=True)

analyzer = SentimentIntensityAnalyzer()

# rt_threshold = 1000 # configure me
TWEET_MAX = 3000

engine = create_engine(DatabaseUrl)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

Policies = [
    {'policy_name': 'default',  'languages': 'en', 'rt_threshold': 1000},
    {'policy_name': 'lowest',   'languages': 'en', 'rt_threshold': 0},
    {'policy_name': 'very_low', 'languages': 'en', 'rt_threshold': 5}
]

session.execute(insert(QueryPolicy).values(Policies).prefix_with('OR IGNORE'))

PolicyNames = Enum('Policies', [policy['policy_name'] for policy in Policies])


def choose_policy(policy: PolicyNames):
    return next((result for result in session.execute(
        select([
            QueryPolicy.languages,
            QueryPolicy.rt_threshold
        ]).where(QueryPolicy.policy_name == policy.name)
    )), None)


active_policy = PolicyNames['very_low']

active_p_info = choose_policy(active_policy)

[active_languages] = list(reader([active_p_info.languages]))

active_rt_thld = active_p_info.rt_threshold

num_added = 0


def add_tweet(tw, user, reacted_id = 0, time_reacted = None):
    global num_added
    sc = analyzer.polarity_scores(tw['text'])
    if 'location' in user.keys():
        loc = user['location']
    else:
        loc = "NOT PROVIDED"
    new_tweet = Tweet(
        id            = int(tw['id']),
        reacted_id    = int(reacted_id),
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
        u_listed_c    = user['public_metrics']['listed_count'],
        time_tweeted  = datetime.fromisoformat(tw['created_at'].replace('Z', '+00:00')),
        time_reacted  = datetime.fromtimestamp(1) if time_reacted is None
                   else datetime.fromisoformat(time_reacted.replace('Z', '+00:00')),
        policy        = active_policy.name
    )
    session.add(new_tweet)
    session.commit()
    num_added += 1


for i, line in enumerate(r.iter_lines()):
    if line:
        is_retweet = False
        decoded_line = line.decode('utf-8')
        tweet = json.loads(decoded_line)

        if 'connection_issue' in tweet.keys():
            print(json.dumps(tweet, indent=4))
            continue

        rt_count = tweet['data']['public_metrics']['retweet_count']
        lang = tweet['data']['lang']
        if rt_count > active_rt_thld and any(lang == al for al in active_languages):
            # print(tweet['data']['public_metrics'])
            # print(tweet['data']['referenced_tweets'])
            # print(tweet['includes']['tweets'])
            # print(tweet['includes']['users'])
            if 'referenced_tweets' in tweet['data'].keys() and len(tweet['data']['referenced_tweets']) > 0:
                for ref_tw in tweet['data']['referenced_tweets']:
                    if ref_tw['type'] == 'retweeted':
                        is_retweet = True
                    ref_tw_details = next((tw for tw in tweet['includes']['tweets'] if tw['id'] == ref_tw['id']),
                                          None)
                    if ref_tw_details is not None:
                        ref_tw_user_details = next(
                            (ur for ur in tweet['includes']['users'] if ur['id'] == ref_tw_details['author_id']),
                            None)
                        add_tweet(ref_tw_details, ref_tw_user_details, tweet['data']['id'], tweet['data']['created_at'])

            if not is_retweet:
                score = analyzer.polarity_scores(tweet['data']['text'])
                add_tweet(tweet['data'], tweet['includes']['users'][0])

    else:
        print('heartbeat')
    if i % 10 == 0:
        print(i, 'tweets,', num_added, 'inserted')
        if num_added >= TWEET_MAX:
            break
