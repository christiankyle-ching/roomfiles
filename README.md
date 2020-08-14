# RoomFiles
RoomFiles is a web-application made with the [Django](https://www.djangoproject.com/) framework. It's core functions are:
 1. Create virtual rooms with other users.
	 - To join rooms, users should have the room's secret code (UUID).
	 - Room's secret codes can be shared through QR codes, and plain text.
 2. These rooms are places where you can upload files and post announcements for other users to see and collaborate with.
 3. Room creator's can manage the people joining in their room. They can ban any users they don't want inside their room.

## Technologies Used & Dependencies
 1.  [Django Framework](https://www.djangoproject.com/)
 2. [Django Google Drive Storage](https://github.com/torre76/django-googledrive-storage)
 3. [Django REST Framework](https://www.django-rest-framework.org/) (Handling AJAX requests)
 4. [Bootstrap Material Design](https://fezvrasta.github.io/bootstrap-material-design/)
 5. [QRCode.js](https://github.com/davidshimjs/qrcodejs) (QR Code generator)
 6. [js-cookie](https://github.com/js-cookie/js-cookie) (For [easier csrf_token fetching](https://docs.djangoproject.com/en/3.1/ref/csrf/#acquiring-the-token-if-csrf-use-sessions-and-csrf-cookie-httponly-are-false))
 7. [waypoints](https://github.com/imakewebthings/waypoints) (For infinite scrolling)
 8. [django_heroku](https://github.com/heroku/django-heroku) (For seamless Heroku deployment)

## Local Development Setup

### Project Setup
To setup a local development server of this app:
 1. Clone this repository.
 2. Set up a Python virtual environment (I used [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/))
	- Make a virtual environment:
`mkvirtualenv ENV_NAME`
	- Activate the venv:
`workon ENV_NAME`
	- Install the dependencies in ./requirements.txt. Open a terminal in the project folder then run:
`pip install -r ./requirements.txt`
 3. Download and install [PostgreSQL](https://www.postgresql.org/).
	 - After installation, create a new database for the app.
	 - Modify the database settings in ./roomfiles/settings.py file. (`roomfiles.settings.DATABASES.default`)
 4. Reset the migrations, because these includes custom migrations I made that involves data migrations to preserve data I had already by other users. But for a new setup, this is irrelevant.
	 - Delete all files inside `./rooms/migrations/` and `./users/migrations/` folders, EXCEPT `__init__.py` files.
	 - Run initial migration:
		```
		python manage.py makemigrations
		python manage.py migrate
		```
 5. Import static images for Avatars and Room Backgrounds using:
	```
	python manage.py import_avatars
	python manage.py import_roombg
	```

### Settings Setup
 1. Change other variables in the settings file:
	 - Change DEBUG to True:
		```python
		DEBUG = True
		```
    - Generate a new SECRET_KEY by:
		 - Opening a shell:
			```
			python manage.py shell
			```
		 - Then running these commands:
			```python
			>>> from django.core.management.utils import get_random_secret_key
			>>> print(get_random_secret_key())
			copy_this_secret_key
			```
	 - Set the newly generated secret key to your settings:
		```python
    	SECRET_KEY = 'paste_secret_here'
    	```
 2. *Optional*: To get the reset password feature to work, you need to add a [Google App Password](https://myaccount.google.com/apppasswords) with your google account (preferably **not using your personal account**). Then change these settings variables:
```python
EMAIL_HOST_USER = 'your_email_here@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password_here'
```

At this point, you can run the local development server, **but uploading files won't work** because it uses `django-googledrive-storage` as the media storage for file uploads.
To set this up, follow the documentation at [django-googledrive-storage](https://django-googledrive-storage.readthedocs.io/en/latest/). For the general steps, you need to:
 1. Set up a project and application in a Google Developer Console.
 2. Enable the Google Drive API from the Console.
 3. Obtain the JSON private key file. Copy the contents of the file to an environment variable with the name `GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE_CONTENTS`.
	 -  Alternatively, you can just copy the path where the JSON file is stored, then assign it to the settings variable `roomfiles.settings.GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE`.

After all those steps, you are ready to run the local dev. server! Just make sure to activate your venv then run:
```
python manage.py runserver
```

## Licenses
Avatars are made by [Freepik](https://www.freepik.com/) from [www.flaticon.com](https://www.flaticon.com/). See *LICENSES* folder.<br>
Rooms' background artworks made by  [Freepik](https://www.freepik.com/)