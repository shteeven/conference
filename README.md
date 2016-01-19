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
 
Sessions can be looked up based on the conference they are under, speaker name, start time, and type, or types if the user selects multiple. 
 
 
## Additional Queries
There are two additional queries: getSessionsOfTypes and getSessionsByTime. 
getSessionsOfTypes function takes a list of types of sessions the user would like to see.
It then looks up the sessions and returns a list of session forms that match the criteria.
The getSessionsByTime takes in a string with the time formatted as HH:MM.
It then queries for sessions that start at or after the time specified. 
This function also returns a list of session forms.

-- getSessionsOfTypes: 
