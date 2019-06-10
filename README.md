Item Catalog Application
The application provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users have the ability to post, edit and delete their own items.

### Run the project ###
* Add Google ClientID and Secret Key to the following files:
    * client_secret.json in auth.py
* Run the project.py file: python project.py

### Screenshot ###
DashboardAfterLogin.png
DashboardAfterLogout.png

API END points and JSON response
Examples:

http://localhost:8000/catalog.json/
[
  {
    "id": 1, 
    "items": [
      {
        "cat_id": 1, 
        "description": "Shinguards", 
        "id": 1, 
        "name": "Shinguards"
      }
    ], 
    "name": "Soccer"
  }, 
  {
    "id": 2, 
    "items": [], 
    "name": "Basketball"
  }, 
  {
    "id": 3, 
    "items": [], 
    "name": "Baseball"
  }, 
  {
    "id": 4, 
    "items": [], 
    "name": "Frisbee"
  }, 
  {
    "id": 5, 
    "items": [
      {
        "cat_id": 5, 
        "description": "", 
        "id": 2, 
        "name": "Goggles"
      }
    ], 
    "name": "Snowboarding"
  }, 
  {
    "id": 6, 
    "items": [], 
    "name": "RockClimbing"
  }
]
