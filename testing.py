import unittest

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed

import webapp2
import webtest

class HelloWorldHandler(webapp2.RequestHandler):
   def get(self):
       # Create the handler's response "Hello World!" in plain text.
       self.response.headers['Content-Type'] = 'text/plain'
       self.response.out.write('Hello World!')


class CacheHandler(webapp2.RequestHandler):
  def post(self):
    key = self.request.get('key')
    value = self.request.get('value')
    memcache.set(key, value)

class AppTest(unittest.TestCase):
    def setUp(self):
        # Create a WSGI application.
        app = webapp2.WSGIApplication([('/', HelloWorldHandler)])
        # Wrap the app with WebTest's TestApp.
        self.testapp = webtest.TestApp(app)

    # Test the handler.
    def testHelloWorldHandler(self):
        response = self.testapp.get('/')
        self.assertEqual(response.status_int, 200)
        # self.assertEqual(response.normal_body, 'Hello World!')
        # self.assertEqual(response.content_type, 'text/plain')

    def setUp(self):
        app = webapp2.WSGIApplication([('/cache/', CacheHandler)])
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()

    def tearDown(self):
        self.testbed.deactivate()

    def testCacheHandler(self):
        # First define a key and value to be cached.
        key = 'answer'
        value = '42'
        self.testbed.init_memcache_stub()
        params = {'key': key, 'value': value}
        # Then pass those values to the handler.
        response = self.testapp.post('/cache/', params)
        # Finally verify that the passed-in values are actually stored in Memcache.
        self.assertEqual(value, memcache.get(key))
