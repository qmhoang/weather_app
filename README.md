# Yet Another Weather App (YAWA)

This is a dockerized app this is broken up into 4 docker packages:
* The first is a standard PostgreSQL db image
* The second contains a REST User Service.  This allows the app to create new users, ask who it is, get authentication token when supplying user/pass, allow other services to validate if a token is valid, etc
* The 3rd contains a REST service that allows people to save zipcode or cities to their account.  With this, they can then look up the weather.  Requires an authenticate token to use
* The 4th is the dockerize web app itself.

Design choices:
I initially has an ambigious plan of using both docker-machine and ReactJS because I had want this to be a good learning experience for me.  My previous experience with docker hasn't been using docker-compose (or its previous iteration) at all.   As you can tell, the docker machine worked out but I dug too deep trying to learn React (npm, bower, gulp, was just one part of trying React and the frontend stack), that I had to basically throw away most of Saturday's work.  Docker-machine worked out much better, allowing me to build small services that talk to each other.

### How to run:
Make sure docker-machine (if required) is setup properly before hand.

To start the docker containers using docker-compose
```
docker-compose up web -d
```
Then you just need to visit the correct ip address using port 8000.  The IP address depends if you are using docker-machine or not.

### How to use the web app
A user is required to logon.  There should be a button to create a new user.  Go to the settings page to add/remove locations that you will track.  The main page isn't pretty (you're getting programmer's art) but does show a few of the data.  It can easily modified to add more databindings.  

Note that when adding locations, there are 2 formats (zipcode and openweathermap's city queries.  If giving a string, openweathermap will try its best to match to a city_id.
