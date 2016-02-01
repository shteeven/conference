import unittest
import urllib
import logging

from google.appengine.ext import testbed
from google.appengine.api import urlfetch
from conference import ConferenceApi
from models import ConferenceForm
from models import ConferenceForms
from models import ConferenceQueryForm
from models import ConferenceQueryForms
from protorpc.remote import protojson

def init_stubs(tb):
    tb.init_urlfetch_stub()
    tb.init_app_identity_stub()
    tb.init_blobstore_stub()
    tb.init_capability_stub()
    tb.init_channel_stub()
    tb.init_datastore_v3_stub()
    tb.init_files_stub()
    # tb.init_mail_stub()
    tb.init_memcache_stub()
    tb.init_taskqueue_stub(root_path='tests/resources')
    tb.init_user_stub()
    tb.init_xmpp_stub()
    return tb


class AppEngineAPITest(unittest.TestCase):

    def setUp(self):
        logging.getLogger().setLevel(logging.DEBUG)

        tb = testbed.Testbed()
        tb.setup_env(current_version_id='testbed.version')
        tb.activate()
        self.testbed = init_stubs(tb)
    
    def testUrlfetch(self):
        # response = urlfetch.fetch('http://www.google.com')
        url = 'http://localhost:9000/_ah/api/conference/v1/conference'
        # form_fields = {
        #     "name": "Albert"
        # }
        form_fields = ConferenceForm(name='steven')
        form_data = protojson.encode_message(form_fields)
        # form_data = urllib.urlencode(form_fields)
        response = urlfetch.fetch(url=url, payload=form_data, method=urlfetch.POST,
                                  headers={'Content-Type': 'application/json'})
        print(dir(response))
        print(response.content)
        self.assertEquals(200, response.status_code)


