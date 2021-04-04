Select * FROM tweets;

SELECT sent_bucket, COUNT(*) AS count
FROM tweets
GROUP BY sent_bucket;

SELECT id, text, group_concat(retweet_count), sent_bucket, COUNT(*) AS count
FROM tweets
GROUP BY id;

Select * FROM tweets WHERE time_reacted IS NOT NULL;

WITH bucketed_tweets AS (
    SELECT sent_bucket,
           COUNT(*) as num_tweet_bin,
           SUM(max_retweet_count) as max_retweet_bin,
           SUM(min_retweet_count) as min_retweet_bin
    FROM (
        SELECT sent_bucket,
               MAX(retweet_count) as max_retweet_count,
               MIN(retweet_count) as min_retweet_count
        FROM tweets
        GROUP BY id
        )
    GROUP BY sent_bucket
)

SELECT sent_bucket     as `Sentiment Bucket`,
       num_tweet_bin   as `# Unique Tweets in Bucket`,
       max_retweet_bin as `# Retweets in Bucket (Max)`,
       min_retweet_bin as `# Retweets in Bucket (Min)`,
       max_retweet_bin /
       num_tweet_bin   as `Ratio`
FROM bucketed_tweets;


SELECT id, reacted_id, group_concat(retweet_count), COUNT(*) as count
FROM tweets
GROUP BY id, reacted_id
HAVING COUNT(*) > 1;

WITH const AS (SELECT 'very_low' AS active_policy)

SELECT id, reacted_id, text,
       sentiment_p, sentiment_l, sentiment_n, compound, sent_bucket,
       MAX(retweet_count) as max_retweet_count,
       MIN(retweet_count) as min_retweet_count,
       MAX(reply_count)   as max_reply_count,
       MIN(reply_count)   as min_reply_count,
       MAX(like_count)    as max_like_count,
       MIN(like_count)    as min_like_count,
       MAX(quote_count)   as max_quote_count,
       MIN(quote_count)   as min_quote_count,
       user_id, user_location,
       MAX(u_followers_c) as max_u_flr_count,
       MAX(u_following_c) as max_u_flg_count,
       MAX(u_tweet_c)     as max_u_twt_count,
       MAX(u_listed_c)    as max_u_lst_count,
       group_concat(time_created)  as all_time_created,
       group_concat(time_reacted)  as all_time_reacted,
       time_tweeted, policy
FROM tweets, const
WHERE policy = const.active_policy
GROUP BY id;

WITH const AS (SELECT 'very_low' AS active_policy)

SELECT id, reacted_id, text,
       sentiment_p, sentiment_l, sentiment_n, compound, sent_bucket,
       retweet_count, reply_count, like_count, quote_count,
       user_id, user_location,
       u_followers_c, u_following_c, u_tweet_c, u_listed_c,
       time_created, time_reacted, time_tweeted, policy
FROM tweets, const
WHERE policy = const.active_policy;

