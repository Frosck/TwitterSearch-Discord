import discord
import asyncio
import json
import unicodedata

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream


ACCESS_TOKEN = ''
ACCESS_SECRET = ''
CONSUMER_KEY = ''
CONSUMER_SECRET = ''

DISCORD_TOKEN = ''

CHANNEL_ID = ''

interesting_words = [""]
hashtags = [""]

client = discord.Client()


def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')


async def send_message_discord(tweet, username):
    global CHANNEL_ID
    channel = discord.Object(id=CHANNEL_ID)
    em = discord.Embed(title=username, description=tweet, colour=0x3498db)
    await client.send_message(channel, embed=em)
    return


class listener(StreamListener):

    def __init__(self, loop, interesting_words):
        self.loop = loop
        self.interesting_words = interesting_words
        
    def on_data(self, data):
        all_data = json.loads(data)
        if 'text' in all_data:
            tweet         = all_data["text"]
            #created_at    = all_data["created_at"]
            retweeted     = all_data["retweeted"]
            username      = all_data["user"]["screen_name"]
            #user_tz       = all_data["user"]["time_zone"]
            #user_location = all_data["user"]["location"]
            #user_coordinates   = all_data["coordinates"]

            print(username, tweet)
            if any(strip_accents(word) in strip_accents(tweet) for word in self.interesting_words) and not retweeted:
                asyncio.run_coroutine_threadsafe(send_message_discord(tweet, username), self.loop)

    def on_error(self, status):
        print(status)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


if __name__ == '__main__':
    try:
        with open('config.json') as json_data:
            data = json.load(json_data)
            ACCESS_TOKEN = data["access_token"]
            ACCESS_SECRET = data["access_secret"]
            CONSUMER_KEY = data["consumer_key"]
            CONSUMER_SECRET = data["consumer_secret"]
            DISCORD_TOKEN = data["discord_token"]
            CHANNEL_ID = data["channel_id"]

            interesting_words = data["interesting_words"]
            hashtags = data["hashtags"]
    except Exception as e:
        raise Exception(e)

    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

    twitterStream = Stream(auth, listener(client.loop, interesting_words))
    kwargs = {"track": hashtags, "async": True}
    twitterStream.filter(**kwargs)

    client.run(DISCORD_TOKEN)
