from os import environ

from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()


class QueryPolicy(Base):
    __tablename__ = 'policies'

    id           = Column(Integer, primary_key=True)
    policy_name  = Column(String(32), unique=True)
    languages    = Column(String(32))
    rt_threshold = Column(Integer)


class Tweet(Base):
    __tablename__ = 'tweets'

    id            = Column(Integer, primary_key=True)
    reacted_id    = Column(Integer, primary_key=True)
    text          = Column(String(300))
    sentiment_p   = Column(Float)
    sentiment_l   = Column(Float)
    sentiment_n   = Column(Float)
    compound      = Column(Float)
    sent_bucket   = Column(Integer)
    retweet_count = Column(Integer, primary_key=True)
    reply_count   = Column(Integer)
    like_count    = Column(Integer)
    quote_count   = Column(Integer)
    user_id       = Column(Integer)
    user_location = Column(String(300))
    u_followers_c = Column(Integer)
    u_following_c = Column(Integer)
    u_tweet_c     = Column(Integer)
    u_listed_c    = Column(Integer)
    time_tweeted  = Column(DateTime(timezone=True))
    time_reacted  = Column(DateTime(timezone=True))
    time_created  = Column(DateTime(timezone=True), server_default=func.now())
    time_updated  = Column(DateTime(timezone=True), onupdate=func.now())
    policy        = Column(String(32), ForeignKey('policies.policy_name'))


DatabaseUrl = environ['SQLITE_URL']

engine = create_engine(DatabaseUrl)
Base.metadata.create_all(engine)
