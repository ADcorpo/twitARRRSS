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
        published = datetime.strptime(tweet['created_at'].replace('+0000','UTC'), '%a %b %d %H:%M:%S %Z %Y')
        title = "@" + username + ': ' + tweet['text']

        content = tweet['text'] + '\n'

        if 'media' in tweet['entities']:
            content += "<img src='{}'>".format(tweet['entities']['media'][0]['media_url'])

        content += "<a href='{}'>link to the tweet…</a>".format("https://twitter.com/" + username + "/status/" + tweet['id_str'])
        
        feed.add(title,
                 content,
                 content_type='html',
                 author=username,
                 published=published,
                 updated=published,
                 id=tweet['id'])

    return feed.get_response()

if __name__ == '__main__':
    app.run(debug=True)
