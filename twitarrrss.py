from datetime import datetime, timezone

from flask import Flask, request, render_template
from werkzeug.contrib.atom import AtomFeed

from twitter import *
from credentials import credentials

api = Twitter(auth=OAuth(credentials['token'],
                         credentials['token_key'],
                         credentials['consumer_secret'],
                         credentials['consumer_key']))

app = Flask(__name__)

def format_tweet(tweet):
    tweet['created_at'] = datetime.strptime(tweet['created_at'].replace('+0000','UTC'), '%a %b %d %H:%M:%S %Z %Y')
    tweet['title'] = "@" + tweet['user']['name'] + ': ' + tweet['text']

    if 'media' in tweet['entities']:
        tweet['text'] += "<img src='{}'>".format(tweet['entities']['media'][0]['media_url'])

    tweet_link = "https://twitter.com/" + tweet['user']['name'] + "/status/" + tweet['id_str']
    tweet['text'] += "\n<a href='" + tweet_link + "'>link to the tweet…</a>"

    return tweet
    

@app.route('/timeline/<username>')
def get_user_timeline(username):
    feed = AtomFeed(username + "'s timeline",
                    feed_url = request.url,
                    url = request.url_root)
    
    #Getting the latest tweets, formatting data
    timeline = api.statuses.user_timeline(screen_name=username,
                                          count=200,
                                          exclude_replies=True)

    for tweet in timeline:
        tweet = format_tweet(tweet)
        
        feed.add(tweet['title'],
                 tweet['text'],
                 content_type='html',
                 author=tweet['user']['name'],
                 updated=tweet['created_at'],
                 id=tweet['id'])

    return feed.get_response()

@app.route('/search/<query>')
@app.route('/search/<query>/<result_type>')
def search(query, result_type='mixed'):
    feed = AtomFeed("Search: " + query,
                    feed_url = request.url,
                    url = request.url_root)

    search = api.search.tweets(q=query, result_type=result_type)['statuses']

    for tweet in search:
        tweet = format_tweet(tweet)

        feed.add(tweet['title'],
                 tweet['text'],
                 content_type='html',
                 author=tweet['user']['name'],
                 updated=tweet['created_at'],
                 id=tweet['id'])

    return feed.get_response()

if __name__ == '__main__':
    app.run(debug=True)
