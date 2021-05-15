# BFDjangoProject
Postman link: https://www.getpostman.com/collections/4a1d7ad1c8fd8c10fc6b

# Description
Social networking site is a website where users can share their thoughts and communicate with other people.
Main features: 
- User has profile, where they can add personal information, such as full name, birth year, education, etc.
- User has web page where they can make posts, in form of text or image;
- User can send friend requests to other users;
- If user accepts other user’s friend request, they will be friends;
- User’s entire page can be set to private or public;
- Individual posts can be set to private or public;
- Only friends of users can access private pages or posts;
- Everyone can access public pages or posts;
- Users may like and comment on other people’s posts if they have access;
- User can join and leave groups;
- User can create group;
- Group creator is admin;
- Group creator can make other people admin;
- Only members can post and view other members’ posts;
- Group admins can delete posts and kick members.

# Used technologies

Project is implemented by creating its backend part using Django Rest Framework which is a popular backend framework for Python users. Requests are sent to the local server using Postman.

Install required python packages using these commands (NOTE: use a separate virtual environment):
- pip install django
- pip install djangorestframework
- pip install django-filters
- pip install markdown
- pip install djangorestframework-jwt
- pip install psycopg2
- pip install psycopg2-binary
- pip install django-debug-toolbar
- pip install phonenumbers

# Run

- python manage.py makemigration
- python manage.py migrate
- python manage.py runserver