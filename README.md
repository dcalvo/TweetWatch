# dangertweet

## What is it?

Finds Tweets that are more likely to be false information.

## Setting it up

1. `git clone https://github.com/dcalvo/dangertweet.git dangertweet && cd dangertweet`
2. `python3 -m venv env`
3. Create a `.env` file in the root directory. Add the following:
```
source env/bin/activate
export APP_SETTINGS="config.DevelopmentConfig"
export DATABASE_URL="postgresql:///dangertweet_dev"
export CONSUMER_KEY="<consumer_key>"
export CONSUMER_SECRET="<consumer_secret>"
```
4. `python -m pip install autoenv`
5. ```echo "source `which activate.sh`" >> ~/.bashrc && source ~/.bashrc```
6. `cd .. && cd dangertweet`
7. Allow the script to run. Whenever you `cd` into this directory, you'll automatically enter your virtual python environment.
8. Install [PostgreSQL](https://www.postgresql.org/download/).
9. `python -m pip install -r requirements.txt`
10. `sudo -u postgres psql -c "create database dangertweet_dev" && sudo -u postgres createuser $USER`
11. `python manage.py db upgrade`
12. `python manage.py runserver`

### Notes
- Many of the steps above could go wrong. Troubleshoot as you go.
- Run `deactivate` to leave the venv.
- Run `psql dangertweet_dev` to get into the Postgres CLI for the DB.
- Run `python manage.py runserver` to run the localhost server at [127.0.0.1:5000](http://127.0.0.1:5000)
- Run `python manage.py db migrate` after changing models.py to save the changes.
- Run `python manage.py db upgrade` to commit the changes to the DB.
- Run `python manage.py db downgrade` if your changes break the DB.

### TODO
- Add heroku config section