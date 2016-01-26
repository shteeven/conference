#!/usr/bin/env python

"""
conference.py -- Udacity conference server-side Python App Engine API;
    uses Google Cloud Endpoints

$Id: conference.py,v 1.25 2014/05/24 23:42:19 wesc Exp wesc $

created by wesc on 2014 apr 21

"""

__author__ = 'wesc+api@google.com (Wesley Chun)'

from datetime import datetime

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from models import ConflictException
from models import Profile
from models import ProfileMiniForm
from models import ProfileForm
from models import StringMessage
from models import BooleanMessage
from models import Conference
from models import ConferenceForm
from models import ConferenceForms
from models import ConferenceQueryForm
from models import ConferenceQueryForms
from models import TeeShirtSize
from models import Session
from models import SessionInForm
from models import SessionOutForm
from models import SessionForms
from models import Speaker
from models import SpeakerForm
from models import SpeakerForms

from settings import WEB_CLIENT_ID
from settings import ANDROID_CLIENT_ID
from settings import IOS_CLIENT_ID
from settings import ANDROID_AUDIENCE

from utils import getUserId

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
MEMCACHE_ANNOUNCEMENTS_KEY = "RECENT_ANNOUNCEMENTS"
ANNOUNCEMENT_TPL = ('Last chance to attend! The following conferences '
                    'are nearly sold out: %s')
FEATURED_SPEAKER_STR = '%s is speaking at: '
MEMCACHE_FEATURED_SPEAKER_KEY = "FEATURED_SPEAKER"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

DEFAULTS = {
    "city": "Default City",
    "maxAttendees": 0,
    "seatsAvailable": 0,
    "topics": ["Default", "Topic"],
}

SESSION_DEFAULTS = {
    "highlights": [],
    "speakerId": '',
    "duration": '1',
    "typeOfSession": "Types",
}

SESSION_TYPES = [
    'lecture',
    'workshop',
    'presentation',
    'roundtable',
    'panel',
    'think tank',
    'professional development',
    'other'
]

OPERATORS = {
    'EQ': '=',
    'GT': '>',
    'GTEQ': '>=',
    'LT': '<',
    'LTEQ': '<=',
    'NE': '!='
}

FIELDS = {
    'CITY': 'city',
    'TOPIC': 'topics',
    'MONTH': 'month',
    'MAX_ATTENDEES': 'maxAttendees',
}

# - - - - - - Request Containers - - - - - - - -

CONF_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeKey=messages.StringField(1, required=True),
)

CONF_GET_BY_TYPE_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    websafeKey=messages.StringField(1, required=True),
    type=messages.StringField(2),
)

CONF_GET_BY_TIME_TYPES_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    time=messages.StringField(1),
    types=messages.StringField(2, repeated=True),
)

CONF_GET_BY_TIME_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    time=messages.StringField(1),
    types=messages.StringField(2, repeated=True),
)

CONF_GET_BY_TYPES_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    types=messages.StringField(1, repeated=True),
)

SESS_POST_REQUEST = endpoints.ResourceContainer(
    SessionInForm,
    websafeKey=messages.StringField(1),
)

SPEAKER_GET_BY = endpoints.ResourceContainer(
    message_types.VoidMessage,
    name=messages.StringField(1),
    email=messages.StringField(2),
)


# - - - - - - - - - - Endpoints Start - - - - - - - - - - - - - - - -

@endpoints.api(name='conference', version='v1', audiences=[ANDROID_AUDIENCE],
               allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID, ANDROID_CLIENT_ID, IOS_CLIENT_ID],
               scopes=[EMAIL_SCOPE])
class ConferenceApi(remote.Service):
    """Conference API v0.1"""

    # - - - Helpers - - - - - - - - - - - - - - - - - - - - - -
    def _validateKey(self, websafe_key):
        """Takes a websafe key and returns the entity (obj) and its key."""

        # NDB accepts trail and lead whitespaces;
        # this allows duplicates because Python sees it as different strings
        print("dsfhkashdkfjhaskjldfhkadsfhadsjklfdskhfkjadshfdhsklfds")
        print(websafe_key)
        if websafe_key:
            key = websafe_key.strip()
            try:
                key = ndb.Key(urlsafe=key)
                obj = key.get()
                print(obj)
            except:
                # except is purposely left vague; multiple types of error.
                raise endpoints.BadRequestException(
                    'The key is of an incorrect format: %s' % key)
            if not obj:
                raise endpoints.NotFoundException(
                    'No conference found with key: %s' % key)
            return obj, key
        else:
            raise endpoints.BadRequestException(
                'No websafe key was received with request.')

    def _validateUser(self):
        """Verifies user authorization and returns user obj and its id"""
        # preload necessary data items
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        user_id = getUserId(user)

        return user, user_id

    # - - - Conference objects - - - - - - - - - - - - - - - - -
    def _copyConferenceToForm(self, conf, displayName):
        """Copy relevant fields from Conference to ConferenceForm."""
        cf = ConferenceForm()
        for field in cf.all_fields():
            if hasattr(conf, field.name):
                # convert Date to date string; just copy others
                if field.name.endswith('Date'):
                    setattr(cf, field.name, str(getattr(conf, field.name)))
                else:
                    setattr(cf, field.name, getattr(conf, field.name))
            elif field.name == "websafeKey":
                setattr(cf, field.name, conf.key.urlsafe())
        if displayName:
            setattr(cf, 'organizerDisplayName', displayName)
        cf.check_initialized()
        return cf

    def _createConferenceObject(self, request):
        """Create or update Conference object, returning ConferenceForm/request."""

        user, user_id = self._validateUser()
        # this assures that a profile has been created before creating a conf;
        self._getProfileFromUser()

        if not request.name:
            raise endpoints.BadRequestException("Conference 'name' field required")

        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}
        del data['websafeKey']
        del data['organizerDisplayName']

        # add default values for those missing (both data model & outbound Message)
        for df in DEFAULTS:
            if data[df] in (None, []):
                data[df] = DEFAULTS[df]
                setattr(request, df, DEFAULTS[df])

        # convert dates from strings to Date objects; set month based on start_date
        if data['startDate']:
            data['startDate'] = datetime.strptime(data['startDate'][:10], "%Y-%m-%d").date()
            data['month'] = data['startDate'].month
        else:
            data['month'] = 0
        if data['endDate']:
            data['endDate'] = datetime.strptime(data['endDate'][:10], "%Y-%m-%d").date()

        # set seatsAvailable to be same as maxAttendees on creation
        if data["maxAttendees"] > 0:
            data["seatsAvailable"] = data["maxAttendees"]
        # generate Profile Key based on user ID and Conference
        # ID based on Profile key get Conference key from ID
        p_key = ndb.Key(Profile, user_id)
        c_id = Conference.allocate_ids(size=1, parent=p_key)[0]
        c_key = ndb.Key(Conference, c_id, parent=p_key)
        data['key'] = c_key
        data['organizerUserId'] = request.organizerUserId = user_id

        # create Conference, send email to organizer confirming
        # creation of Conference & return (modified) ConferenceForm
        Conference(**data).put()
        taskqueue.add(params={'email': user.email(), 'conferenceInfo': repr(request)},
                      url='/tasks/send_confirmation_email')
        return request

    @ndb.transactional()
    def _updateConferenceObject(self, request):

        user, user_id = self._validateUser()

        conf, c_key = self._validateKey(request.websafeKey)

        # check that user is owner
        if user_id != conf.organizerUserId:
            raise endpoints.ForbiddenException(
                'Only the owner can update the conference.')

        # Not getting all the fields, so don't create a new object; just
        # copy relevant fields from ConferenceForm to Conference object
        for field in request.all_fields():
            data = getattr(request, field.name)
            # only copy fields where we get data
            if data not in (None, []):
                # special handling for dates (convert string to Date)
                if field.name in ('startDate', 'endDate'):
                    data = datetime.strptime(data, "%Y-%m-%d").date()
                    if field.name == 'startDate':
                        conf.month = data.month
                # write to Conference object
                setattr(conf, field.name, data)
        conf.put()
        prof = ndb.Key(Profile, user_id).get()
        return self._copyConferenceToForm(conf, getattr(prof, 'displayName'))

    @endpoints.method(message_types.VoidMessage, ConferenceForms,
                      path='conference/user',
                      http_method='GET', name='conferenceGetCreated')
    def conferenceGetCreated(self, request):
        """Return conferences created by user."""
        # make sure user is authed
        user, user_id = self._validateUser()

        # create ancestor query for all key matches for this user
        confs = Conference.query(ancestor=ndb.Key(Profile, user_id))
        prof = ndb.Key(Profile, user_id).get()
        # return set of ConferenceForm objects per Conference
        return ConferenceForms(
            items=[self._copyConferenceToForm(conf, getattr(prof, 'displayName')) for conf in confs]
        )

    @endpoints.method(ConferenceForm, ConferenceForm, path='conference',
                      http_method='POST', name='conferenceCreate')
    def conferenceCreate(self, request):
        """Create new conference."""
        return self._createConferenceObject(request)

    @endpoints.method(ConferenceForm, ConferenceForm,
                      path='conference',
                      http_method='PUT', name='conferenceUpdate')
    def conferenceUpdate(self, request):
        """Update conference w/provided fields & return w/updated info."""
        return self._updateConferenceObject(request)

    @endpoints.method(CONF_GET_REQUEST, ConferenceForm,
                      path='conference',
                      http_method='GET', name='conferenceGet')
    def conferenceGet(self, request):
        """Return requested conference (by websafeKey)."""
        conf, c_id = self._validateKey(request.websafeKey)
        prof = conf.key.parent().get()
        # return ConferenceForm
        return self._copyConferenceToForm(conf, getattr(prof, 'displayName'))


    # - - - - Queries for Conf - - - - - -

    def _getQuery(self, request):
        """Return formatted query from the submitted filters."""
        q = Conference.query()
        inequality_filter, filters = self._formatFilters(request.filters)

        # If exists, sort on inequality filter first
        if not inequality_filter:
            q = q.order(Conference.name)
        else:
            q = q.order(ndb.GenericProperty(inequality_filter))
            q = q.order(Conference.name)

        for filtr in filters:
            if filtr["field"] in ["month", "maxAttendees"]:
                filtr["value"] = int(filtr["value"])
            formatted_query = ndb.query.FilterNode(filtr["field"], filtr["operator"], filtr["value"])
            q = q.filter(formatted_query)
        return q

    def _formatFilters(self, filters):
        """Parse, check validity and format user supplied filters."""
        formatted_filters = []
        inequality_field = None

        for f in filters:
            filtr = {field.name: getattr(f, field.name) for field in f.all_fields()}

            try:
                filtr["field"] = FIELDS[filtr["field"]]
                filtr["operator"] = OPERATORS[filtr["operator"]]
            except KeyError:
                raise endpoints.BadRequestException("Filter contains invalid field or operator.")

            # Every operation except "=" is an inequality
            if filtr["operator"] != "=":
                # check if inequality operation has been used in previous filters
                # disallow the filter if inequality was performed on a different field before
                # track the field on which the inequality operation is performed
                if inequality_field and inequality_field != filtr["field"]:
                    raise endpoints.BadRequestException("Inequality filter is allowed on only one field.")
                else:
                    inequality_field = filtr["field"]

            formatted_filters.append(filtr)
        return (inequality_field, formatted_filters)

    @endpoints.method(ConferenceQueryForms, ConferenceForms, path='conference/query',
                      http_method='POST', name='conferenceQuery')
    def conferenceQuery(self, request):
        """Query for conferences."""
        print('GAGAGAGAGAGA')
        conferences = self._getQuery(request)

        # need to fetch organiser displayName from profiles
        # get all keys and use get_multi for speed
        organisers = [(ndb.Key(Profile, conf.organizerUserId)) for conf in conferences]
        profiles = ndb.get_multi(organisers)

        # put display names in a dict for easier fetching
        names = {}
        for profile in profiles:
            names[profile.key.id()] = profile.displayName

        # return individual ConferenceForm object per Conference
        return ConferenceForms(
            items=[self._copyConferenceToForm(conf, names[conf.organizerUserId])
                   for conf in conferences])

    # - - - Profile objects - - - - - - - - - - - - - - - - - - -
    def _copyProfileToForm(self, prof):
        """Copy relevant fields from Profile to ProfileForm."""
        # copy relevant fields from Profile to ProfileForm
        pf = ProfileForm()
        for field in pf.all_fields():
            if hasattr(prof, field.name):
                # convert t-shirt string to Enum; just copy others
                if field.name == 'teeShirtSize':
                    setattr(pf, field.name, getattr(TeeShirtSize, getattr(prof, field.name)))
                else:
                    setattr(pf, field.name, getattr(prof, field.name))
        pf.check_initialized()
        return pf

    def _getProfileFromUser(self):
        """Return user Profile from datastore, creating new one if non-existent."""
        user, user_id = self._validateUser()

        p_key = ndb.Key(Profile, user_id)
        profile = p_key.get()
        # create new Profile if not there
        if not profile:
            profile = Profile(
                key=p_key,
                displayName=user.nickname(),
                mainEmail=user.email(),
                teeShirtSize=str(TeeShirtSize.NOT_SPECIFIED),
            )
            profile.put()

        return profile  # return Profile

    def _doProfile(self, save_request=None):
        """Get user Profile and return to user, possibly updating it first."""
        # get user Profile
        prof = self._getProfileFromUser()

        # if saveProfile(), process user-modifyable fields
        if save_request:
            for field in ('displayName', 'teeShirtSize'):
                if hasattr(save_request, field):
                    val = getattr(save_request, field)
                    if val:
                        setattr(prof, field, str(val))
                        # if field == 'teeShirtSize':
                        #    setattr(prof, field, str(val).upper())
                        # else:
                        #    setattr(prof, field, val)
                        prof.put()

        # return ProfileForm
        return self._copyProfileToForm(prof)

    @endpoints.method(message_types.VoidMessage, ProfileForm,
                      path='profile', http_method='GET', name='profileGet')
    def profileGet(self, request):
        """Return user profile."""
        return self._doProfile()

    @endpoints.method(ProfileMiniForm, ProfileForm,
                      path='profile', http_method='POST', name='profileSave')
    def profileSave(self, request):
        """Update & return user profile."""
        return self._doProfile(request)

    # - - - Announcements - - - - - - - - - - - - - - - - - - - -
    @staticmethod
    def _cacheAnnouncement():
        """Create Announcement & assign to memcache; used by
        memcache cron job & putAnnouncement().
        """
        confs = Conference.query(ndb.AND(
            Conference.seatsAvailable <= 5,
            Conference.seatsAvailable > 0)
        ).fetch(projection=[Conference.name])

        if confs:
            # If there are almost sold out conferences,
            # format announcement and set it in memcache
            announcement = ANNOUNCEMENT_TPL % (
                ', '.join(conf.name for conf in confs))
            memcache.set(MEMCACHE_ANNOUNCEMENTS_KEY, announcement)
        else:
            # If there are no sold out conferences,
            # delete the memcache announcements entry
            announcement = ""
            memcache.delete(MEMCACHE_ANNOUNCEMENTS_KEY)

        return announcement

    @endpoints.method(message_types.VoidMessage, StringMessage,
                      path='conference/announcement',
                      http_method='GET', name='announcementGet')
    def announcementGet(self, request):
        """Return Announcement from memcache."""
        return StringMessage(data=memcache.get(MEMCACHE_ANNOUNCEMENTS_KEY) or "")

    # - - - Registration - - - - - - - - - - - - - - - - - - - -
    @ndb.transactional(xg=True)
    def _registerForConference(self, request, reg=True):
        """Register or unregister user for selected conference."""

        retval = None
        prof = self._getProfileFromUser()  # get user Profile
        conf, c_id = self._validateKey(request.websafeKey)

        wsk = request.websafeKey

        # register
        if reg:
            # check if user already registered otherwise add
            if wsk in prof.conferenceKeysToAttend:
                raise ConflictException(
                    "You have already registered for this conference")

            # check if seats avail
            if conf.seatsAvailable <= 0:
                raise ConflictException(
                    "There are no seats available.")

            # register user, take away one seat
            prof.conferenceKeysToAttend.append(wsk)
            conf.seatsAvailable -= 1
            retval = True

        # unregister
        else:
            # check if user already registered
            if wsk in prof.conferenceKeysToAttend:

                # unregister user, add back one seat
                prof.conferenceKeysToAttend.remove(wsk)
                conf.seatsAvailable += 1
                retval = True
            else:
                retval = False

        # write things back to the datastore & return
        prof.put()
        conf.put()
        return BooleanMessage(data=retval)

    @endpoints.method(message_types.VoidMessage, ConferenceForms,
                      path='registration',
                      http_method='GET', name='conferenceGetToAttend')
    def conferenceGetToAttend(self, request):
        """Get list of conferences that user has registered for."""
        prof = self._getProfileFromUser()  # get user Profile
        conf_keys = [ndb.Key(urlsafe=wsck) for wsck in prof.conferenceKeysToAttend]
        conferences = ndb.get_multi(conf_keys)

        # get organizers
        organisers = [ndb.Key(Profile, conf.organizerUserId) for conf in conferences]
        profiles = ndb.get_multi(organisers)

        # put display names in a dict for easier fetching
        names = {}
        for profile in profiles:
            names[profile.key.id()] = profile.displayName

        # return set of ConferenceForm objects per Conference
        return ConferenceForms(items=[self._copyConferenceToForm(conf, names[conf.organizerUserId]) \
                                      for conf in conferences])

    @endpoints.method(CONF_GET_REQUEST, BooleanMessage,
                      path='registration',
                      http_method='POST', name='conferenceRegisterFor')
    def conferenceRegisterFor(self, request):
        """Register user for selected conference."""
        return self._registerForConference(request)

    @endpoints.method(CONF_GET_REQUEST, BooleanMessage,
                      path='registration',
                      http_method='DELETE', name='conferenceUnregisterFrom')
    def conferenceUnregisterFrom(self, request):
        """Unregister user for selected conference."""
        return self._registerForConference(request, reg=False)

    # - - - - - - - - - - - - Sessions - - - - - - - - - - - - - -
    def _copySessionToForm(self, sess):
        """Copy relevant fields from Session to SessionOutForm."""
        sf = SessionOutForm()
        if sess.speakerId:
            # Has knowledge of the SessionOutModel fields
            speaker = ndb.Key(urlsafe=sess.speakerId).get()
            sf.speakerName = speaker.name
            sf.speakerBio = speaker.bio
            sf.speakerCredentials = speaker.credentials
            sf.speakerTitle = speaker.title
            sf.speakerEmail = speaker.email
        for field in sf.all_fields():
            if hasattr(sess, field.name):
                # convert Date to date string; just copy others
                if field.name == 'date':
                    setattr(sf, field.name, str(getattr(sess, field.name)))
                elif field.name == 'startTime':
                    setattr(sf, field.name, str(getattr(sess, field.name)))
                else:
                    setattr(sf, field.name, getattr(sess, field.name))
            elif field.name == "websafeKey":
                setattr(sf, field.name, sess.key.urlsafe())
        sf.check_initialized()
        return sf

    def _createSessionObject(self, request):
        """Create or update Session object, returning SessionInForm/request."""
        # preload necessary data items
        user = endpoints.get_current_user()

        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        if request.speakerId:
            # will raise error if speaker key is invalid
            self._getSpeakerObject(request.speakerId)
        # copy ConferenceForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}

        # add default values for those missing (both data model & outbound Message)
        for df in SESSION_DEFAULTS:
            if data[df] in (None, []):
                data[df] = SESSION_DEFAULTS[df]
                setattr(request, df, SESSION_DEFAULTS[df])

        # convert dates from strings to Date objects; set month based on start_date
        if data['date']:
            data['date'] = datetime.strptime(data['date'][:10], "%Y-%m-%d").date()
        if data['startTime']:
            data['startTime'] = datetime.strptime(data['startTime'], "%H:%M").time()

        ################################################################
        # Make this section work with the key validation
        ################################################################
        # check if conf exists given websafeConfKey
        # get conference; check that it exists
        wsck = request.websafeKey
        if not wsck:
            raise endpoints.BadRequestException(
                'No conference key was received with request')
        try:
            wsck = wsck.strip()
            conf = ndb.Key(urlsafe=wsck).get()
        except:
            # except is purposely left vague; multiple types of error.
            raise endpoints.BadRequestException(
                'The key is of an incorrect format: %s' % wsck)
        if not conf:
            raise endpoints.NotFoundException(
                'No conference found with key: %s' % wsck)

        if not request.name:
            raise endpoints.BadRequestException("Session 'name' field required")

        # generate Conference Key based on user ID and Conference
        # ID based on Profile key get Conference key from ID
        wsck = request.websafeKey
        c_key = ndb.Key(urlsafe=wsck)
        if not c_key.get():
            raise endpoints.NotFoundException('No conference found with key: %s' % wsck)
        data['conferenceId'] = c_key.id()
        ################################################################
        ################################################################
        s_id = Session.allocate_ids(size=1, parent=c_key)[0]
        s_key = ndb.Key(Session, s_id, parent=c_key)
        data['key'] = s_key

        # create Session, send email to organizer confirming
        # creation of Session and return SessionForm
        del data['websafeKey']
        Session(**data).put()
        sess = s_key.get()
        if data['speakerId']:
            taskqueue.add(params={'speakerId': data['speakerId'], 'conferenceId': data['conferenceId']},
                          url='/tasks/set_featured_speaker')
        taskqueue.add(params={'email': user.email(), 'conferenceInfo': repr(request)},
                      url='/tasks/send_confirmation_email')
        return self._copySessionToForm(sess)

    @endpoints.method(CONF_GET_BY_TYPE_REQUEST, SessionForms,
                      path='session/conference/type',
                      http_method='GET', name='sessionGetByConferenceByType')
    def sessionGetByConferenceByType(self, request):
        """Return sessions under conference by type."""
        # create ancestor query for all key matches for this user
        c_sessions = Session.query(ancestor=ndb.Key(urlsafe=request.websafeKey))
        c_sessions = c_sessions.filter(Session.typeOfSession == request.type)
        # return set of ConferenceForm objects per Conference
        return SessionForms(
            items=[self._copySessionToForm(sess) for sess in c_sessions]
        )

    @endpoints.method(CONF_GET_REQUEST, SessionForms,
                      path='session/conference',
                      http_method='GET', name='sessionGetByConference')
    def sessionGetByConference(self, request):
        """Return sessions under conference."""
        # create ancestor query for all key matches for this user
        c_sessions = Session.query(ancestor=ndb.Key(urlsafe=request.websafeKey))

        return SessionForms(
            items=[self._copySessionToForm(sess) for sess in c_sessions]
        )

    @endpoints.method(CONF_GET_REQUEST, SessionForms,
                      path='session/speaker',
                      http_method='GET', name='sessionGetBySpeaker')
    def sessionGetBySpeaker(self, request):
        """Return sessions of a speaker's websafe ID."""
        # create query for all key matches for this speaker
        sessions = Session.query(Session.speakerId == request.speakerId)
        # return set of SessionOutForm objects for speaker
        return SessionForms(
            items=[self._copySessionToForm(sess) for sess in sessions]
        )

    @endpoints.method(SESS_POST_REQUEST, SessionOutForm,
                      path='session',
                      http_method='POST', name='sessionCreate')
    def sessionCreate(self, request):
        """Create new session."""
        return self._createSessionObject(request)

    # - - - - - - - - - - - - Wishlist - - - - - - - - - - - - - -
    def _editWishlist(self, request, reg=True):
        """Add or remove session from user's wishlist."""
        retval = None
        prof = self._getProfileFromUser()  # get user Profile

        # check if session exists given websafeKey
        wsk = request.websafeKey
        sess, s_id = self._validateKey(wsk)

        # register
        if reg:
            # check if session is already in wishlist
            if wsk in prof.sessionKeysInWishlist:
                raise ConflictException(
                    "This session is already in your wishlist.")

            # register user, take away one seat
            prof.sessionKeysInWishlist.append(wsk)
            retval = True

        # unregister
        else:
            # check if user already registered
            if wsk in prof.sessionKeysInWishlist:
                # unregister user, add back one seat
                prof.sessionKeysInWishlist.remove(wsk)
                retval = True
            else:
                retval = False

        # write things back to the datastore & return
        prof.put()
        return BooleanMessage(data=retval)

    @endpoints.method(message_types.VoidMessage, SessionForms,
                      path='wishlist',
                      http_method='GET', name='wishlistGetSessions')
    def wishlistGetSessions(self, request):
        """Query for all the sessions in a conference that the user is interested in"""
        prof = self._getProfileFromUser()  # get user Profile
        sess_keys = [ndb.Key(urlsafe=wsk) for wsk in prof.sessionsWishlist]
        sessions = ndb.get_multi(sess_keys)

        # return set of SessionOutForm objects per Session
        return SessionForms(items=[self._copySessionToForm(sess) for sess in sessions])

    @endpoints.method(CONF_GET_REQUEST, BooleanMessage,
                      path='wishlist',
                      http_method='POST', name='wishlistAddSession')
    def wishlistAddSession(self, request):
        """Adds the session to the user's list of sessions they are interested in attending"""
        return self._editWishlist(request)
    #
    @endpoints.method(CONF_GET_REQUEST, BooleanMessage,
                      path='wishlist',
                      http_method='DELETE', name='wishlistDeleteSession')
    def wishlistDeleteSession(self, request):
        """Delete session from user wishlist."""
        return self._editWishlist(request, reg=False)

    # - - - - - - - - - - - - Additional Queries - - - - - - - - - - - - - -
    @endpoints.method(CONF_GET_BY_TYPES_REQUEST, SessionForms, path='session/types',
                      http_method='GET', name='sessionGetOfTypes')
    def sessionGetOfTypes(self, request):
        """Return sessions for given types. """
        # create ancestor query for all key matches for this user
        sessions = Session.query()
        # can accept array
        sessions = sessions.filter(Session.typeOfSession.IN(request.types))
        # return set of ConferenceForm objects per Conference
        return SessionForms(items=[self._copySessionToForm(sess) for sess in sessions])

    @endpoints.method(CONF_GET_BY_TIME_REQUEST, SessionForms, path='getSessionsByTime',
                      http_method='POST', name='sessionGetByTime')
    def sessionGetByTime(self, request):
        """Return sessions starting at/after a certain time"""
        # create ancestor query for all key matches for this user
        sessionTime = datetime.strptime(request.time, "%H:%M").time()

        sessions = Session.query(Session.startTime >= sessionTime)
        # return set of SessionForm objects
        return SessionForms(items=[self._copySessionToForm(sess) for sess in sessions])

    @endpoints.method(CONF_GET_BY_TIME_TYPES_REQUEST, SessionForms, path='session/times/types',
                      http_method='GET', name='sessionGetByTimeByNotTypes')
    def sessionGetByTimeByNotTypes(self, request):
        """Return sessions starting at/after a certain time and by type"""
        # create ancestor query for all key matches for this user
        sessionTime = datetime.strptime(request.time, "%H:%M").time()
        types = set(SESSION_TYPES) - set(request.types)
        sessions = Session.query()
        # can accept array
        sessions = sessions.filter(Session.startTime >= sessionTime)
        sessions = sessions.filter(Session.typeOfSession.IN(types))
        # return set of ConferenceForm objects per Conference
        return SessionForms(items=[self._copySessionToForm(sess) for sess in sessions])

    # - - - Announcements - - - - - - - - - - - - - - - - - - - -
    @staticmethod
    def _cacheFeaturedSpeaker(request):
        """Create Announcement for featured speaker & assign to memcache."""
        c_id = int(request.get('conferenceId'))
        sessions = Session.query(Session.conferenceId == c_id)
        sessions = sessions.filter(Session.speaker == request.get('speakerId'))
        sessions = sessions.fetch()
        if len(sessions) >= 2:
            speaker = ndb.Key(urlsafe=request.get('speakerId')).get()
            # If there are almost sold out conferences,
            # format announcement and set it in memcache
            announcement = FEATURED_SPEAKER_STR % speaker.name
            announcement += ', '.join(sess.name for sess in sessions)
            memcache.set(MEMCACHE_FEATURED_SPEAKER_KEY, announcement)
        else:
            announcement = ''
        return announcement

    @endpoints.method(message_types.VoidMessage, StringMessage, path='speaker/get/featured',
                      http_method='GET', name='speakerGetFeatured')
    def speakerGetFeatured(self, request):
        """Return Announcement from memcache."""
        return StringMessage(data=memcache.get(MEMCACHE_FEATURED_SPEAKER_KEY) or "")

    # - - - - - - - - - - - - Speaker - - - - - - - - - - - - - -
    def _copySpeakerToForm(self, speaker):
        """Copy relevant fields from Speaker to SpeakerForm."""
        sf = SpeakerForm()
        for field in sf.all_fields():
            if hasattr(speaker, field.name):
                setattr(sf, field.name, getattr(speaker, field.name))

            elif field.name == "websafeKey":
                setattr(sf, field.name, speaker.key.urlsafe())
        sf.check_initialized()
        return sf

    def _createSpeakerObject(self, request):
        """Create or update Speaker object, returning SpeakerForm/request."""
        # ensure user auth
        user, u_id = self._validateUser()

        if not request.name:
            raise endpoints.BadRequestException("Speaker 'name' field required")

        if request.email:
            q = Speaker.query(Speaker.email == request.email)
            entity = q.get()
            if entity:
                raise endpoints.ForbiddenException('Email is already registered with a speaker.')

        # copy SpeakerForm/ProtoRPC Message into dict
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}
        del data['websafeKey']
        s_key = Speaker(**data).put()
        speaker = s_key.get()

        return self._copySpeakerToForm(speaker)

    def _getSpeakerObject(self, wsk):
        """Return speaker info."""
        speaker, s_id = self._validateKey(wsk)
        return speaker

    @endpoints.method(CONF_GET_REQUEST, SpeakerForm,
                      path='speaker/get', http_method='GET', name='speakerGet')
    def speakerGet(self, request):
        """Return speaker info for websafeKey."""
        speaker = self._getSpeakerObject(request.websafeKey)
        return self._copySpeakerToForm(speaker)

    @endpoints.method(SPEAKER_GET_BY, SpeakerForms,
                      path='speaker/query',
                      http_method='POST', name='speakerQueryBy')
    def speakerQueryBy(self, request):
        """Return speakers by email, name, or query all if no criteria specified."""
        # should only return one speaker
        if request.email:
            speakers = Speaker.query(Speaker.email == request.email)
        # can return multiple
        elif request.name:
            speakers = Speaker.query(Speaker.name == request.name)
        # returns all if no email or name specified
        else:
            speakers = Speaker.query()

        # return set of SpeakerForm objects per speaker matched
        return SpeakerForms(
            items=[self._copySpeakerToForm(speaker) for speaker in speakers]
        )

    @endpoints.method(SpeakerForm, SpeakerForm,
                      path='speaker/create',
                      http_method='POST', name='speakerCreate')
    def speakerCreate(self, request):
        """Create new speaker."""
        return self._createSpeakerObject(request)

api = endpoints.api_server([ConferenceApi])  # register API
