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
The Session model is a child of Conference. 
The conferenceId and name are the only two fields that are required. 
The date and startTime properties are formatted as YYYY-MM-DD and HH:mm respectively, with the date property able to take in a dateTime format and splice it to the appropriate size.
Speaker field should be populated by a Speaker entity websafeKey.
Sessions can be looked up based on the conference they are under, speaker name, start time, and type, or types if the user selects multiple. 
 
Speaker entities provide a websafe key in their forms to be inserted in Session entities. 
name and email fields are both required, with the email being unique to that speaker. 
The idea behind this design is that as a session is being created by the user, a separate component on the front-end will allow the user to look up speakers and select the one that is speaking at the session.
The data from the speaker object selected is passed to the function or controller that will be submitting the createSession request.
There is nothing to assert that the speaker key is removed from the session entity if the speaker entity is deleted.
This functionality can be implemented in a deleteSpeaker function if created.

To populate a session page with complete information (speaker and session data), two requests are required:
getSpeaker and a getSession____. It can be in one with modification or creation of a session form.
 
## Additional Queries
There are two additional queries: getSessionsOfTypes and getSessionsByTime. 
getSessionsOfTypes function takes a list of types of sessions the user would like to see.
It then looks up the sessions and returns a list of session forms that match the criteria.
The getSessionsByTime takes in a string with the time formatted as HH:mm.
It then queries for sessions that start at or after the time specified. 
This function also returns a list of session forms.

## Query Related Problem
The problem with having the time and exclusion of a type of session is that NDB does not allow inequalities on two different fields.
My solution to have a constant list of possible session types and remove those types the user has selected to exclude.
With the remaining list of types, the query is then filtered with Session.typesOfSession.IN(types); types being the list of remaining types that the user has not excluded.
This solution can be done with a single or list value. My implementation takes in a list of values.

## Musts
Profile must exist for Conference functions to work properly.
Conference must exist in order for Session to be created.
Speaker must exist in order to populate Session.speaker.
Session must exist in order to populate Profile.wishlist.
Conference must exist in order to populate Profile.conferenceToAttend.

## Side Notes
The path of the api are very inconsistent. 
They work, but there is a much better way of doing; I'm just too busy to deal with it.


## Formatting
LINES --
Python files in this project do not adhere to the PEP 80 characters/line
maximum. For the sake of readability in the authors dev environment, the lines 
have a max length of 120 characters.
FUNCTION NAMES --
In order to increase readability when scanning the API Explorer and to 
help with understanding the purpose of the function, the names of functions will 
follow one of these structures: 

-- For APIs:
 'entityAction'
 'entityActionWhat'

-- For class functions:
 '_actionEntity'
 '_actionEntityWhat'
 '_actionWhat'
 
Where entity is the 'entity', or object, the function is designed for; 
'action' is the primary action that will be executed; 
and 'What' is the extraneous objects or the 'by', 'to', 'for', or 'from' followed by an object.



## URL Usages By Function
This is a reference to help organize paths and void conflicts
Convention is 'entityCategory', 'entityCategory/:key', 
'entityCategory/action', 'entityCategory/(by, in or for)' or 'entityCategory/action/:key'



- GETs:

(conference)
'conference' - 
'conference/{websafeKey}' - 
'conference' - 
'conference/announcement' - 
'conference/attending' - 

(profile)
'profile' - profileGet - VoidMessage

(session)
'



- POSTs:

(conference)
'conference' - conferenceCreate - ConferenceForm
'conference/query' - conferenceQuery - ConferenceQueryForms
'conference/register/{websafeKey}' - conferenceRegisterFor - CONF_GET_REQUEST

(profile)
'profile' - profileSave - PofileMiniForm

(session)
'session' - sessionGetBySpeaker - CONF_GET_REQUEST
'session/{websafeKey}' - sessionGetByConference - CONF_GET_REQUEST



- DELETEs:

(conference)
'conference/register/{websafeKey}' - conferenceUnregisterFrom - CONF_GET_REQUEST


- PUTs:

(conference)
'conference/{websafeKey}' - 'conferenceUpdate' - CONF_POST_REQUEST























