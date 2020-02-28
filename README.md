# DRF Project time tracking

This project is a small rest-api application for tracking people's time on projects and tasks.

## Features:
- User authentication
- create projets
- create tasks and associate them to projects
- keep track of tasks started and time spend per task
- pause, continue and restart tasks
- keep track of projects by user and the associated tasks

## Requirements
1. virtualenvwrapper (https://virtualenvwrapper.readthedocs.io/en/latest/install.html)
2. Python 3.6 or higher.
3. PostgreSQL 10

## Installation

#### 1. Create virtualenv:
```
$ mkvirtualenv project_tracker
```
#### 2. Clone the repository:
```
$ git clone https://github.com/ChronoFrank/project_tracker.git
```
#### 3. Install dependencies:
```
$ workon project_tracker
$ pip install -r requirements.txt
```
#### 4. Migrate the database (PostgreSQL):
Create a new database in your PostgreSQL server and create a settings_loca.py file
```
 $ touch /project_tracker/settings_local.py

── project_tracker
    ├── manage.py
    ├── project_tracker
    │   ├── __init__.py
    │   ├── settings_local.py #new file created
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── project_tracking
    │   ├── admin.py
    │   ├── apps.py
    │   ├── __init__.py

```
edit the file with your database configuration.
```
 DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.postgresql_psycopg2', # '.postgresql_psycopg2', '.mysql', or '.oracle'
        'NAME': 'project_tracker',
        'USER': '<PostgresSQL--user>',
        'PASSWORD': '<PostgresSQL--password>',
        'HOST':'127.0.0.1', # Set to empty string for localhost.
        'PORT':'5432', # Set to empty string for default.
    },
}
```

Then you can sync the database.

```
$ python manage.py migrate
```

#### 5. Run tests to validate everything
```
$ python manage.py test

# if we want to get the coverage report:
coverage run ./manage.py test; coverage report
```
#### 6. Run the server:
```
$ python manage.py runserver 12001
```

### 7. create superuser to access the endpoints
```
$ python manage.py createsuperuser
```

### 8. check the API documentation and the postman collection for usage

- the api documentation is at http://localhost:12001/docs
- to use the endpoints you must get the access_token provided by /api/v1/access_token/ the token will have a
duration of 5 minutes, after that you must user the /api/v1/refresh_token/ to get a new one.
- all the endpoints must have the Authorization header with the access_token as value
- You also can import the project_tracker.postman_collection.json in postman to test the endpoints.

Happy coding :)