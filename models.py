#!/usr/bin/env python

"""models.py

Udacity conference server-side Python App Engine data & ProtoRPC models


"""

__author__ = 'stevenbarnhurst@gmail.com (Steven Barnhurst)'

import httplib
import endpoints
from protorpc import messages
from google.appengine.ext import ndb

class ConflictException(endpoints.ServiceException):
    """ConflictException -- exception mapped to HTTP 409 response"""
    http_status = httplib.CONFLICT

class Profile(ndb.Model):
    """Profile -- User profile object"""
    displayName             = ndb.StringProperty()
    mainEmail               = ndb.StringProperty()
    teeShirtSize            = ndb.StringProperty(default='NOT_SPECIFIED')
    conferencesToAttend     = ndb.KeyProperty(repeated=True)
    sessionsWishlist        = ndb.KeyProperty(repeated=True)

class ProfileMiniForm(messages.Message):
    """ProfileMiniForm -- update Profile form message"""
    displayName     = messages.StringField(1)
    teeShirtSize    = messages.EnumField('TeeShirtSize', 2)

class ProfileForm(messages.Message):
    """ProfileForm -- Profile outbound form message"""
    displayName             = messages.StringField(1)
    mainEmail               = messages.StringField(2)
    teeShirtSize            = messages.EnumField('TeeShirtSize', 3)

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    data = messages.StringField(1, required=True)

class BooleanMessage(messages.Message):
    """BooleanMessage-- outbound Boolean value message"""
    data = messages.BooleanField(1)

class Conference(ndb.Model):
    """Conference -- Conference object"""
    name            = ndb.StringProperty(required=True)
    description     = ndb.StringProperty()
    organizerUserId = ndb.StringProperty(required=True)
    topics          = ndb.StringProperty(repeated=True)
    city            = ndb.StringProperty()
    startDate       = ndb.DateProperty()
    month           = ndb.IntegerProperty()  # TODO: do we need for indexing like Java?
    endDate         = ndb.DateProperty()
    maxAttendees    = ndb.IntegerProperty()
    seatsAvailable  = ndb.IntegerProperty()

class ConferenceForm(messages.Message):
    """ConferenceForm -- Conference outbound form message"""
    name            = messages.StringField(1, required=True)
    description     = messages.StringField(2)
    organizerUserId = messages.StringField(3)
    topics          = messages.StringField(4, repeated=True)
    city            = messages.StringField(5)
    startDate       = messages.StringField(6) #DateTimeField()
    month           = messages.IntegerField(7, variant=messages.Variant.INT32)
    maxAttendees    = messages.IntegerField(8, variant=messages.Variant.INT32)
    seatsAvailable  = messages.IntegerField(9, variant=messages.Variant.INT32)
    endDate         = messages.StringField(10) #DateTimeField()
    websafeKey      = messages.StringField(11)
    organizerDisplayName = messages.StringField(12)

class ConferenceForms(messages.Message):
    """ConferenceForms -- multiple Conference outbound form message"""
    items = messages.MessageField(ConferenceForm, 1, repeated=True)

class TeeShirtSize(messages.Enum):
    """TeeShirtSize -- t-shirt size enumeration value"""
    NOT_SPECIFIED = 1
    XS_M = 2
    XS_W = 3
    S_M = 4
    S_W = 5
    M_M = 6
    M_W = 7
    L_M = 8
    L_W = 9
    XL_M = 10
    XL_W = 11
    XXL_M = 12
    XXL_W = 13
    XXXL_M = 14
    XXXL_W = 15

class ConferenceQueryForm(messages.Message):
    """ConferenceQueryForm -- Conference query inbound form message"""
    field = messages.StringField(1)
    operator = messages.StringField(2)
    value = messages.StringField(3)

class ConferenceQueryForms(messages.Message):
    """ConferenceQueryForms -- multiple ConferenceQueryForm inbound form message"""
    filters = messages.MessageField(ConferenceQueryForm, 1, repeated=True)

# - - - - - - - - - - Session Models - - - - - - - - -
class Session(ndb.Model):
    """Session -- Session object"""
    name            = ndb.StringProperty(required=True)
    conferenceKey    = ndb.KeyProperty(required=True, kind='Conference')
    highlights      = ndb.StringProperty(repeated=True)
    speakerKey       = ndb.KeyProperty(kind='Speaker')
    duration        = ndb.StringProperty()
    typeOfSession   = ndb.StringProperty()
    date            = ndb.DateProperty()
    startTime       = ndb.TimeProperty()

class SessionInForm(messages.Message):
    """SessionInForm -- Session inbound form object"""
    name            = messages.StringField(1, required=True)
    websafeConferenceKey = messages.StringField(2, required=True)
    highlights      = messages.StringField(3, repeated=True)
    websafeSpeakerKey = messages.StringField(4)
    duration        = messages.StringField(5)
    typeOfSession   = messages.StringField(6)
    date            = messages.StringField(7)
    startTime       = messages.StringField(8)
    websafeKey      = messages.StringField(9)  # session websafe key

class SessionOutForm(messages.Message):
    """SessionOutForm -- Session outbound form object"""
    name            = messages.StringField(1)
    websafeConferenceKey = messages.StringField(2)
    highlights      = messages.StringField(3, repeated=True)
    websafeSpeakerKey = messages.StringField(4)
    duration        = messages.StringField(5)
    typeOfSession   = messages.StringField(6)
    date            = messages.StringField(7)
    startTime       = messages.StringField(8)
    websafeKey      = messages.StringField(9)  # session websafe key
    speakerName     = messages.StringField(10)
    speakerBio      = messages.StringField(11)
    speakerCredentials = messages.StringField(12, repeated=True)
    speakerTitle    = messages.StringField(13)
    speakerEmail    = messages.StringField(14)


class SessionForms(messages.Message):
    """SessionForms -- multiple Session outbound form message"""
    items = messages.MessageField(SessionOutForm, 1, repeated=True)


# - - - - - - - - - - Speaker Models - - - - - - - - -
class Speaker(ndb.Model):
    """Speaker -- Speaker object"""
    name            = ndb.StringProperty(required=True)
    bio             = ndb.TextProperty()
    credentials     = ndb.StringProperty(repeated=True)
    title           = ndb.StringProperty()
    email           = ndb.StringProperty()

class SpeakerForm(messages.Message):
    """SpeakerForm -- Speaker outbound form"""
    name            = messages.StringField(1, required=True)
    bio             = messages.StringField(2)
    credentials     = messages.StringField(3, repeated=True)
    title           = messages.StringField(4)
    email           = messages.StringField(5)
    websafeKey      = messages.StringField(6)


class SpeakerForms(messages.Message):
    """SpeakerForms -- multiple Speaker outbound form message"""
    items = messages.MessageField(SpeakerForm, 1, repeated=True)

