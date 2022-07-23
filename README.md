# Personal Belongings Organizer

## Overview

Personal Belongings Organizer (pbo) is a web-based tool to organize all your personal belongings.

It allows you to do the following:
- Register yourself as a user
- Login / Logout
- Change your password
- Add / edit / delete items you possess
- Optionally add details such as a description or model
- Maintain a list of manufacturers you can assign to items
- Maintain a list of categories you can assign to items
- Maintain a list of rooms you can assign to items
- Up- / download user manuals for your items
- See a line chart showing the total items in the database over time
- See a pie chart showing the items in the database per manufacturer
- See a pie chart showing the items in the database per category
- See a pie chart showing the items in the database per room

## Technologies used
- HTML
- CSS
- JavaScript
- Bootstrap
- Python
- Flask
- SQLite
- Chart.js

## Initialization and startup

### Initializing the database

Before using the app for the first time, the database must be initialized. This can be done from the root directory of the app as follows:
```
export FLASK_APP=pbo
export FLASK_ENV=development
flask init-db
```

The code to initialize the database is maintained in the file **db.py** and the database schema is defined in the file **schema.sql**.

### Running the app

In order to run the app, run the following commands from the root directory of the app:
```
export FLASK_APP=pbo
export FLASK_ENV=development
flask run
```

The code to initialize the app is maintained in the file **\__init__.py**.

The base HTML template is maintained in the file **base.html**.

Static files for the app such as pictures and the CSS file are stored in the folder **static**.

## Description

### Registering and changing your password

The first action you'll do is registering yourself as a user. All you need to do in order to register is to provide a username and a password. If that username is already taken you'll be notified and can register again with another username. Your user will be stored in the table user in the database. The corresponding password will be stored as a hash alongside your username in that table.

Once you're registered, you can log in or log out anytime. Each time you log in, your password will be checked against the password hash in the database. A session cookie will ensure that the user stays logged in throughout the browser session.

You can always change your password as a registered user by clicking on "Settings" at the top right of the page and then clicking on "Change your password".

The code for the actions above is maintained in the file **auth.py** and the corresponding HTML template files are:
- templates/auth/register.html
- templates/auth/registrationsuccess.html
- templates/auth/login.html
- templates/auth/changepassword.html
- templates/auth/passwordchangesuccess.html
- templates/index/settings.html

### Adding / editing / removing an item

In order to add an item, simply click on "Add item". This will present a form where you can enter the name and other details of the item. The fields "Category", "Room" and "Manufacturer" can be selected using drop-down lists. In order to maintain those list, just click on "Settings" at the top right of the page and then click on either "Edit manufacturers", "Edit categories" or "Edit rooms".

If you want to edit an item, click on "Edit" on the line of the item on the main page.

If you want to delete an item, click on "Delete" on the line of the item on the main page. Upon clicking the "Delete" button, a notification shows up asking if you are sure you want to delete the item. This functionality is implemented by using Bootstrap's JavaScript modal plugin.

Items will be stored in the table items in the database. Manufacturers, categories and rooms are stored in their own tables.

The code for the actions above is maintained in the files:
- index.py
- manufacturers.py
- categories.py
- rooms.py

The corresponding HTML template files are:
- templates/index/index.html
- templates/index/create.html
- templates/index/update.html
- templates/manufacturers/index.html
- templates/manufacturers/create.html
- templates/manufacturers/update.html
- templates/categories/index.html
- templates/categories/create.html
- templates/categories/update.html
- templates/rooms/index.html
- templates/rooms/create.html
- templates/rooms/update.html

### Up- / downloading / removing a user manual

You can either upload a user manual during the creation of a new item or if the item already exists, you can click on "Upload" on the line of the item on the main page.

To download a user manual, simply click on "Download" on the line of the item.

To remove a manual, click on "Remove" instead of "Download". Before an item gets removed, a notification shows up asking if you are sure you want to delete the user manual. This notification uses Bootstrap's JavaSript modal plugin the same ways as when attempting to delete an item.

The Up- / downloading functionality is implemented by using the File Uploads capability of Flask-WTF, which is a simple integration of Flask and WTForms. WTForms is a forms validation and rendering library for Python web development.

The code for the actions above is maintained in the file **index.py** and the corresponding HTML template file for up- / downloading / removing user manuals are: 
- templates/index/uploadmanual.html
- templates/index/index.html
- templates/index/update.html

### Charts

To get a visual picture of your belongings, click on "Settings" at the top right of the page.

The first graph on that page is a line chart showing how many items you have in the database in total at any date where you added items. This allows you to track how you accumulate things.

The second graph is a pie chart showing how many items you have per manufacturer.

The third graph is a pie chart showing how many items you have per category.

The fourth graph is a pie chart showing how many items you have per room.

The charts are generated by using the Chart.js JavaScript library. The colorization of the pie chart pieces are randomly created using a JavaScript for-loop and the Math.random() function.

The code for the actions above is maintained in the file **index.py** and the correspoding HTML template file for displaying the charts is: **templates/index/charts.html**.