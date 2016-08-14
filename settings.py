#!/usr/bin/env python

"""settings.py

Udacity conference server-side Python App Engine app user settings

$Id$

created/forked from conference.py by wesc on 2014 may 24

"""

# Replace the following lines with client IDs obtained from the APIs
# Console or Cloud Console.
WEB_CLIENT_ID = '907267896781-3n64hr9uc78uro0f6htonp12aoaqbaks.apps.googleusercontent.com'
ANDROID_CLIENT_ID = '995892868409-llckl401s3po8339d9pgku9v2n0objm7.apps.googleusercontent.com'
IOS_CLIENT_ID = '995892868409-dipqemio37n1bglpsshijpgo6ajhlsbv.apps.googleusercontent.com'
ANDROID_AUDIENCE = WEB_CLIENT_ID

import json
import random


# @app.route('/')
# def hello_world():
#     return 'Hello World!'
#
# @app.route('/rolldice')
def roll_dice():
    num = int(random.random() * 6 + 1) + int(random.random() * 6 + 1)
    return json.dumps({'result': num})

print(roll_dice())
# if __name__ == '__main__':
#     app.debug = True
#     app.run()