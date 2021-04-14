# PaaS Backend
## Getting Started

First clone the repository from Github and switch to the new directory.

Install the virtualenv manager & activate the virtualenv for your project:

```
python3 -m pip install pipenv
pipenv install
pipenv shell
```

Then simply apply the migrations:

```
python manage.py migrate
```

You can now run the development server:

```
python manage.py runserver
```
