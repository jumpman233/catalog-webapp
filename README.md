# Catalog webapp
## Description
An application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.
## Requirements
- python 2.7
- flask
- sqlalchemy
- requests
## Start
1. Run `python additems.py` to create database and add datas.
2. **If you are using virtual machine, ignore this one.**
    Edit the host from 0.0.0.0 to 127.0.0.1 at last row in server.py.
3. Run `python server.py` to start server
4. Open http://localhost:5000 (or maybe you change the port) in browser.
## Database Structure
    Table category,
    id(Integer) as primary_key,
    name(String) as not null

    Table item,
    id(Integer) as primary_key,
    name(String) as not null,
    category_id(Integer) as foreign key(category.id)
    time(Integer)
## Authentication
Because of the GFW in China, I can not get Google service with my server.
So I just use the github oauth authentication. Besides, It's a pity that I cannot find a api to disconnect from github oauth authentication.
## CRUD
1. Create: 
    You can build a item with a name, description and choose a category.
    You cannot create a new Item when a item has the same name and category.
2. Edit:
    You can edit a item's name, description and choose a category.
    You cannot create a new Item when a item has the same name and category.
3. Delete:
    You can just delete item.
4. Read:
    Click item in page to look through.
## API Endpoints
Get the all JSON data with [this link](http://localhost:5000/catelog/JSON).
    