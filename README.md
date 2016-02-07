App Engine application for the Udacity training course.

## Products
- [App Engine][1]

## Language
- [Python][2]

## APIs
- [Google Cloud Endpoints][3]

## Setup Instructions
1. Update the value of `application` in `app.yaml` to the app ID you
   have registered in the App Engine admin console and would like to use to host
   your instance of this sample.
1. Update the values at the top of `settings.py` to
   reflect the respective client IDs you have registered in the
   [Developer Console][4].
1. Update the value of CLIENT_ID in `static/js/app.js` to the Web client ID
1. (Optional) Mark the configuration files as unchanged as follows:
   `$ git update-index --assume-unchanged app.yaml settings.py static/js/app.js`
1. Run the app with the devserver using `dev_appserver.py DIR`, and ensure it's running by visiting your local server's address (by default [localhost:8080][5].)
1. (Optional) Generate your client library(ies) with [the endpoints tool][6].
1. Deploy your application.


[1]: https://developers.google.com/appengine
[2]: http://python.org
[3]: https://developers.google.com/appengine/docs/python/endpoints/
[4]: https://console.developers.google.com/
[5]: https://localhost:8080/
[6]: https://developers.google.com/appengine/docs/python/endpoints/endpoints_tool

## Design Decisions -- Session and Speaker Models
The Session model is a child of Conference. `conferenceKey` and `name` 
are the only two fields that are required. `speakerKey` property will be 
populated if `websafeSpeakerKey` field is sent with the SessionInForm. `date` 
and `startTime` fields are formatted as `YYYY-MM-DD` and `HH:mm` respectively, 
with `date` field able to take in a `dateTime` format and splice it to 
the appropriate size. Sessions can be looked up based on the conference they 
are under, speaker name, start time, and type, or types if the user selects 
multiple. 

Under Sessions, `highlights` property is a list of `StringProperties`. This is 
a choice based on the assumption that the highlights will be short and 
displayed as lists, rather than paragraphs. 
 
Speaker entities provide a websafe key in their forms to be inserted in 
SessionInForm. `name` field is required. 


## Additional Queries
There are two additional queries: `sessionGetOfTypes` and `sessionGetByTime`. 
`sessionGetOfTypes` function takes a list of types of sessions the user would 
like to see. It then looks up the sessions and returns a list of session 
forms that match the criteria. `sessionGetByTime` takes in a string with 
the time formatted as `HH:mm`. It then queries for sessions that start at or 
after the time specified. This function also returns a list of session forms.

## Query Related Problem
The problem with having the time, and exclusion of a type of session, is that 
NDB does not allow inequalities on two different fields. My solution is to have 
a constant list of possible session types and remove those types the user 
has selected to exclude. With the remaining list of types, the query is then 
filtered with `Session.typesOfSession.IN(types)`; types being the list of 
remaining types that the user has not excluded. This solution can be done 
with a single or list of values. My implementation takes in a list of values.


## Formatting
### LINES --
Python files in this project do not adhere to the PEP-8 80 characters/line
maximum. For the sake of readability in the author's dev environment, the lines 
have a max length of 120 characters.

### FUNCTION NAMES --
In order to increase readability when scanning the API Explorer and to 
help with understanding the purpose of the function, the names of functions 
will follow one of these structures: 

##### -- For APIs:
- 'entityAction'
- 'entityActionWhat'

##### -- For class functions:
- '_actionEntity'
- '_actionEntityWhat'
- '_actionWhat'
 
Where entity is the 'entity', or object, the function is designed for; 
'action' is the primary action that will be executed; and 'What' is the 
extraneous objects/fields or the 'by', 'to', 'for', or 'from' followed by 
an object/field.

### WEBSAFE KEYS --
All websafe keys in forms are a reference to the object/form itself unless 
the key specifies another entity.
For example:
- 'websafeKey' - refence to self
- 'websafeSessionKey' - reference to Session entity

## URL Usages By Function
This is a reference to help organize paths and avoid conflicts. Entity 
is the primary object being dealt with, and the noun is the portion of 
the function name that is usually preceded by a verb or preposition. For 
example, 'sessionGetByConference' would have a path of 
'session/conference'. Use of websafe keys in url paths is intentionally 
avoided; this helps to reduce chances of key and sub-path recognition 
conflicts.

Convention for this app is 'entity', 'entity/{key}', 'entity/noun' 
or 'entity/noun/{key}'

##### -- GETs:

(conference)
- 'conference/user' - conferenceGetCreated - VoidMessage
- 'conference/announcement' - announcementGet - VoidMessage
- 'conference/{websafeKey}' - conferenceGet - CONF_GET_REQUEST
- 'conference/registration' - conferenceGetToAttend - VoidMessage
- 'conference' - conferenceQuery - ConferenceQueryForms

(profile)
- 'profile' - profileGet - VoidMessage

(session)
- 'session/conference/type' - sessionGetByConferenceByType - CONF_GET_BY_TYPE_REQUEST
- 'session/conference' - sessionGetByConference - CONF_GET_REQUEST
- 'session/speaker' - sessionGetBySpeaker - CONF_GET_REQUEST
- 'session/wishlist' - sessionsGetFromWishlist - VoidMessage
- 'session/types' - sessionGetOfTypes - CONF_GET_BY_TYPES_REQUEST
- 'session/time' - sessionGetByTime - CONF_GET_BY_TIME_REQUEST
- 'session/time/types' - sessionGetByTimeByNotTypes - CONF_GET_BY_TIME_TYPES_REQUEST

(speaker)
- 'speaker/featured' - speakerGetFeatured - VoidMessage
- 'speaker/{websafeKey}' - speakerGet - CONF_GET_REQUEST
- 'speaker' - speakerQuery - SPEAKER_GET_BY


##### -- POSTs:

(conference)
- 'conference' - conferenceCreate - ConferenceForm
- 'conference/registration' - conferenceRegisterFor - CONF_GET_REQUEST

(profile)
- 'profile' - profileSave - PofileMiniForm

(session)
- 'session' - sessionCreate - SessionInForm
- 'session/wishlist' - sessionAddToWishlist - CONF_GET_REQUEST

(speaker)
- 'speaker' - speakerCreate - SpeakerForm

##### -- DELETEs:

(conference)
- 'conference/registration' - conferenceUnregisterFrom - CONF_GET_REQUEST

(session)
- 'session/wishlist' - sessionDeleteFromWishlist - CONF_GET_REQUEST

##### -- PUTs:

(conference)
- 'conference' - 'conferenceUpdate' - ConferenceForm



