import json
import requests
import os

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from models import Tweet

url = 'https://api.twitter.com/2/tweets/sample/stream?tweet.fields=public_metrics,lang,geo,created_at' \
      '&expansions=author_id&user.fields=public_metrics,location'
headers = {"Authorization": "Bearer " + os.environ['TWITTER_BEARER_TOKEN']}

r = requests.get(url, headers=headers, stream=True)

rt_threshold = 1000

analyzer = SentimentIntensityAnalyzer()

for line in r.iter_lines():
    if line:
        decoded_line = line.decode('utf-8')
        tweet = json.loads(decoded_line)

        if 'connection_issue' in tweet.keys():
            print(json.dumps(tweet, indent=4))
            continue

        rt_count = tweet['data']['public_metrics']['retweet_count']
        lang = tweet['data']['lang']

        if rt_count > rt_threshold and lang == 'en':
            print(json.dumps(tweet, indent=4))
            score = analyzer.polarity_scores(tweet['data']['text'])
            print(score)
            tweet_popo = Tweet(tweet, score)
            print(tweet_popo)
    else:
        print('heartbeat')
