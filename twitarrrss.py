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
    created_at = datetime.strptime(tweet['created_at'].replace('+0000','UTC'), '%a %b %d %H:%M:%S %Z %Y')
    title = "@" + username + ': ' + tweet['text']

    if 'media' in tweet['entities']:
        content += "<img src='{}'>".format(tweet['entities']['media'][0]['media_url'])

    content += "<a href='{}'>link to the tweet…</a>"
    content.format("https://twitter.com/" + username + "/status/" + tweet['id_str'])

    tweet_data = \
                 {
                     'created_at': created_at,
                     'title': title,
                     'content': content
                 }

    return tweet_data
    

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
        tweet_data = format_tweet(tweet)
        
        feed.add(tweet_data['title'],
                 tweet_data['content'],
                 content_type='html',
                 author=username,
                 updated=tweet_data['created_at'],
                 id=tweet['id'])

    return feed.get_response()

if __name__ == '__main__':
    app.run(debug=True)
