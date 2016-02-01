# import webtest
# import logging
# import unittest
# from google.appengine.ext import testbed
# from protorpc.remote import protojson
# import endpoints
#
# from conference import ConferenceApi
# from models import ConferenceForm
# from models import ConferenceForms
# from models import ConferenceQueryForm
# from models import ConferenceQueryForms

# def init_stubs(tb):
#     tb.init_urlfetch_stub()
#     tb.init_app_identity_stub()
#     tb.init_blobstore_stub()
#     tb.init_capability_stub()
#     tb.init_channel_stub()
#     tb.init_datastore_v3_stub()
#     tb.init_files_stub()
#     tb.init_mail_stub()
#     tb.init_memcache_stub()
#     tb.init_taskqueue_stub()
#     tb.init_user_stub()
#     tb.init_xmpp_stub()
#     return tb
#
#
# class AppTest(unittest.TestCase):
#     def setUp(self):
#         logging.getLogger().setLevel(logging.DEBUG)
#
#         tb = testbed.Testbed()
#         tb.setup_env(current_version_id='testbed.version')
#         tb.activate()
#         self.testbed = init_stubs(tb)
#
#
#     def tearDown(self):
#         self.testbed.deactivate()
#
#
#
#     def test_endpoint_testApi(self):
#         application = endpoints.api_server([ConferenceApi], restricted=False)
#
#         testapp = webtest.TestApp(application)
#
#         # # # # Test init query (empty) # # # #
#         req = ConferenceQueryForms()
#         response = testapp.post('/_ah/spi/' + ConferenceApi.__name__ + '.' + ConferenceApi.conferenceQuery.__name__,
#                                 protojson.encode_message(req),
#                                 content_type='application/json')
#
#         res = protojson.decode_message(ConferenceForms, response.body)
#         self.assertEqual(res.items, [])
#
#         # # # # Insert Item into Conference # # # #
#         req = ConferenceForm(name='Hey')
#         response = testapp.post('/_ah/spi/' + ConferenceApi.__name__ + '.' + ConferenceApi.conferenceCreate.__name__,
#                                 protojson.encode_message(req),
#                                 content_type='application/json')
#         res = protojson.decode_message(ConferenceForms, response.body)
#         self.assertEqual(len(res.item), 1)
#
#
#
#
# if __name__ == '__main__':
#     unittest.main()


# from google.appengine.ext import testbed
# import webtest
# import endpoints
#
#
# def init_stubs(tb):
#     tb.init_all_stubs()
#
# def setUp(self):
#     tb = testbed.Testbed()
#     tb.setup_env(current_version_id='testbed.version') #needed because endpoints expects a . in this value
#     tb.activate()
#     tb.init_all_stubs()
#     self.testbed = tb
#
# def tearDown(self):
#     self.testbed.deactivate()
#
# def test_endpoint_insert(self):
#     app = endpoints.api_server([TestEndpoint], restricted=False)
#     testapp = webtest.TestApp(app)
#     msg = {...} # a dict representing the message object expected by insert
#                 # To be serialised to JSON by webtest
#     resp = testapp.post_json('/_ah/spi/TestEndpoint.insert', msg)
#
#     self.assertEqual(resp.json, {'expected': 'json response msg as dict'})


