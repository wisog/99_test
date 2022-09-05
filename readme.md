# Description
MVP test project for the backend position at 99minutos.

Created with Python/Flask Stack.

### Installation:
It's recommended to use a virtual environment.

use `pip3 install -r requirements.txt`  to install needed libraries

### Usage:
It should be run with the command `python3 app.py`

In order to use the api a token is needed, you can get one for the admin using
`curl --location --request POST 'http://127.0.0.1:5000/' 
--form 'username="admin"' --form 'password="admin"'`

### Notes:
In order to have a easier testing we're using SQLite as the BD engine, we can change that
setting a BD Connection URI on `DATABASE_URI` env variable.

If DB file doesn't exist we need to generate the DB schema using:

>flask shell
> 
>from app import db
>
>db.create_all()

and then we can generate rows or query data Using the ORM Layer. 
To generate the first users (1 admin & 1 general user) we'll use:


> from handlers.users.models import User

> admin_user = User('admin', 'admin')
> 
> admin_user.is_admin = True
> 
> admin_user.save()
 
> user = User('client', 'clientpwd')
> 
> user.save()
---
 You'll need to revist **99minutos_test.postman_collection.json** for requests examples.