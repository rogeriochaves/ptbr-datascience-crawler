from github import Github, InputFileContent
from telethon import TelegramClient
import re
import os
import base64
from newspaper import Article
import asyncio
import tweepy
loop = asyncio.get_event_loop()

# Get your own api_id and api_hash from https://my.telegram.org, under API Dev
api_id = os.environ['API_ID']
api_hash = os.environ['API_HASH']
# Get the twitter tokens from https://developer.twitter.com/apps
consumer_key = os.environ['TWITTER_CONSUMER_KEY']
consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
access_token = os.environ['TWITTER_ACCESS_TOKEN']
access_token_secret = os.environ['TWITTER_ACCESS_SECRET']


if os.environ['SESSION_DB']:
    with open("session_name.session", "wb") as file:
        file.write(base64.b64decode(os.environ['SESSION_DB']))


def get_last_id_from_tweets(tweets):
    for tweet in tweets:
        matches = re.search(r'Last Message ID: (\d+)', tweet)
        if matches:
            return int(matches[1])


def get_link_messages(client, offset):
    messages = loop.run_until_complete(client.get_messages(
        'datasciencepython', min_id=offset, limit=300, reverse=True))
    messages_with_links = filter(lambda m:
                                 m.message and
                                 re.match(r'.*https?://.*', m.message) and
                                 "t.me/datasciencepython" not in m.message,
                                 messages)

    return list(messages_with_links)


def build_tweets_list(messages):
    tweets = [m.message[0:200] + "..."
              if len(m.message) > 200
              else m.message
              for m in messages]
    last_id = messages[-1].id
    timestamp = messages[-1].date.strftime('%d/%m')
    tweets = ["Data Science Links %s (Last Message ID: %d)" % (
        timestamp, last_id)] + tweets

    return tweets


def get_twitter_client():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api


def get_last_tweets(twitter_client):
    return [status.text for status in tweepy.Cursor(twitter_client.user_timeline).items()]


if __name__ == "__main__":
    client = TelegramClient('session_name', api_id, api_hash)
    client.start()
    print("Connected to Telegram!")

    twitter_client = get_twitter_client()
    last_tweets = get_last_tweets(twitter_client)
    last_id = get_last_id_from_tweets(last_tweets) or 89569
    print("Getting messages after", last_id)

    messages = get_link_messages(client, last_id)
    print(len(messages), "links found")
    if len(messages) == 0:
        print("No links to save")
        exit(0)

    new_tweets = build_tweets_list(messages)
    print("Tweeting...")

    status = None
    for tweet in new_tweets:
        if status is None:
            status = twitter_client.update_status(status=tweet)
        else:
            status = twitter_client.update_status(
                status=tweet, in_reply_to_status_id=status.id)

    print("Done! https://twitter.com/ptbrdslinks")
