# Deploying SCLibrary on PythonAnywhere

The live site runs on PythonAnywhere's free Beginner plan at `https://<username>.pythonanywhere.com`, using Django 5.2 and SQLite.

## 1. Get the code

Open a **Bash console** on PythonAnywhere and run:

```bash
git clone -b development https://github.com/GKFire/CS476-Group-Project.git
cd CS476-Group-Project/program
mkvirtualenv sclibrary --python=python3.12
pip install -r requirements.txt
```

## 2. Create the database

Migration files are not in git (see `.gitignore`), so they are generated on the server:

```bash
python manage.py makemigrations sclibrary
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser   # optional, for /admin
```

## 3. Create the web app

On the **Web** tab:

1. **Add a new web app**, choose **Manual configuration**, then **Python 3.12**.
2. **Source code:** `/home/<username>/CS476-Group-Project/program`
3. **Virtualenv:** `/home/<username>/.virtualenvs/sclibrary`
4. **Static files:** URL `/static/`, directory `/home/<username>/CS476-Group-Project/program/staticfiles`
5. **Security:** turn on **Force HTTPS** (login cookies are HTTPS-only when `DEBUG` is off)

## 4. Edit the WSGI file

On the Web tab, open the **WSGI configuration file**, delete everything in it, and paste:

```python
import os
import sys

path = "/home/<username>/CS476-Group-Project/program"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["DJANGO_SETTINGS_MODULE"] = "service.settings"
os.environ["DJANGO_DEBUG"] = "False"
os.environ["DJANGO_ALLOWED_HOSTS"] = "<username>.pythonanywhere.com"
os.environ["DJANGO_SECRET_KEY"] = "<paste a new random key here>"
os.environ["EMAIL_HOST_PASSWORD"] = "<Gmail app password for the SCLibrary account>"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Generate a new secret key in the Bash console and paste it in. Never commit it to git:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Click **Reload** on the Web tab and open the site.

## Updating the live site

```bash
cd ~/CS476-Group-Project/program
git pull
workon sclibrary
pip install -r requirements.txt
python manage.py makemigrations sclibrary
python manage.py migrate
python manage.py collectstatic --noinput
```

Then click **Reload** on the Web tab.

If a model change makes `migrate` fail, reset the database (this deletes all data on the live site):

```bash
rm db.sqlite3
rm sclibrary/migrations/0*.py
python manage.py makemigrations sclibrary
python manage.py migrate
```

## Keeping the site online

Free web apps expire if not renewed. Log in at least once a month and click **Run until 1 month from today** on the Web tab, especially before grading.

## Running locally

Nothing changes for development. With no environment variables set, `DEBUG` is on and only `localhost` is allowed.
To test the forgot password emails locally, set the Gmail app password first (PowerShell: `$env:EMAIL_HOST_PASSWORD="..."`).

```bash
cd program
pip install -r requirements.txt
python manage.py runserver
```
