# Textcavator backend

The text mining tool that obviates all others

This is a server side web application based on [Django][1] and [Django REST framework][2] (DRF). Its primary purpose is to provide a JSON API with authentication and authorization, in order to support a separate frontend application.

[1]: https://www.djangoproject.com
[2]: https://www.django-rest-framework.org


## Before you start

You need to install the following software:

 - PostgreSQL >= 10, client, server and C libraries
 - Python 3.8
 - virtualenv
 - WSGI-compatible webserver (deployment only)
 - [Visual C++ for Python][14] (Windows only)

[14]: https://wiki.python.org/moin/WindowsCompilers


## How it works

The `ianalyzer` package is our "project" in Django jargon. It contains all central administration. The `settings`, `urls` and `wsgi` modules inside this package play the same roles as in any Django project. The `settings` module contains defaults that can be immediately used in development, but should be overridden in production. The `urls` module registers DRF [viewsets][3] besides the regular Django registrations.

[3]: https://www.django-rest-framework.org/api-guide/viewsets/

The `index` module contains a special view function which is meant to facilitate a client side application. This view will attempt to find an `index.html` file in the static folders and return it as the response. In the `urls` module, this view is configured as a global fallback route. The `index.html` should launch a client side (frontend) application that handles routing.

**Note:** this backend application doesn't—and *shouldn't*—contain a root `index.html` in any of its static folders. Instead, you should add an external directory to Django's `STATICFILES_DIRS` setting which contains an `index.html` in its root, if you wish to combine this backend application with your frontend application of choice.

As in any Django application, you may add an arbitrary number of "application" (Django jargon) packages next to the `ianalyzer` package. Each "application" may contain its own `models` and `migrations`, as well as `admin`, `signals`, `validators`, `urls` etcetera. A `views` module may contain DRF [viewsets][3] instead of native Django views, in which case there should also be a [`serializers`][4] module which intermediates between the `models` and the `views`.

[4]: https://www.django-rest-framework.org/api-guide/serializers/

Unittest modules live directly next to the module they belong to. Each directory may contain a `conftest.py` with test fixtures available to all tests in the directory.


## Development

### Quickstart

Create and activate a virtualenv. Ensure your working directory is the one that contains this README. Run the following commands as yourself (i.e., not in sudo mode nor with elevated privileges). You may need to [reconfigure PostgreSQL][5] and/or pass [additional arguments to `psql`][6] (in particular, your [own][7] PostgreSQL `dbname` and `username`) in order to be able to run the first command. You need to execute this sequence of commands only once after cloning the repository.

[5]: https://www.postgresql.org/docs/10/auth-pg-hba-conf.html
[6]: https://www.postgresql.org/docs/10/app-psql.html
[7]: https://www.postgresql.org/docs/10/database-roles.html

```console
$ psql -f create_db.sql
$ pip install pip-tools
$ pip install -r requirements.txt
$ python manage.py migrate
$ python manage.py createsuperuser
```

We need to install `psycopg2` with the `--no-binary` flag [until version 2.8 of `psycopg2` is available][8]. If this were not the case, we could use `pip-sync` instead of `pip install -r`; the former currently doesn't work because of the `--no-binary` flag being present in the `requirements.txt`.

[8]: http://initd.org/psycopg/docs/install.html#disabling-wheel-packages-for-psycopg-2-7

If you are overriding the default settings, you may pass `--pythonpath` and `--settings` arguments to every invocation of `python manage.py`. `--settings` should be the name of the module (without `.py`) with your settings overrides. `--pythonpath` should be the path to the directory with your overridden settings module.


### Running the application (development server)

If you made any changes to your configured corpora, load them into the database before running the aplication.

```console
$ python manage.py loadcorpora
```

Start the development server with:

```console
$ python manage.py runserver
```

Once you see this line:

```console
Starting development server at http://127.0.0.1:8000/
```

you can visit http://localhost:8000/admin/ and http://localhost:8000/api/ in your browser of choice. If you attached an external frontend application, its main page will be at http://localhost:8000/.


### Enabling livereload

Run the following command in parallel with the development server:

```console
$ python manage.py livereload
```

This works for all Python modules, templates and static files that Django knows about. This also includes external directories that you may have added to the `STATICFILES_DIRS` setting. The `DEBUG` setting should be `True`, otherwise the livereload script is not inserted in HTML pages by the livereload middleware.


### Running the unittests

Run `pytest` to execute all tests once or `pytest --looponfail` to retest continuously as files change. Use the [pytest-django helpers][9] when writing new tests. pytest has all bells and whistles you may ever dream of; see the [documentation][10].

[9]: https://pytest-django.readthedocs.io/en/latest/helpers.html
[10]: https://docs.pytest.org/en/latest/


### Package management

When adding a new package to the requirements, it is recommended that you manually install it first and check that it works. Then, add the name of the package to the `requirements.in`. The entry should not include a version specification, unless you want to set an upper bound on the version. See the `django` entry for an example. After editing the `requirements.in`, run

```console
$ pip-compile
```

to update the `requirements.txt` with pinned versions of the package and all of its dependencies. Commit the changes to `requirements.in` and `requirements.txt` together to VCS.


## Deployment

Deployment is quite different from development. Please read the [Django documentation][11] and also the documentation of whatever webserver you are using. This section will only address some application specifics.

[11]: https://docs.djangoproject.com/en/1.11/howto/deployment/


### Overriding the settings

Make a copy of `ianalyzer/settings.py` and keep it out of reach from spying eyes. Change at least the following settings.

 - `BASE_DIR` should point to the directory containing this README.
 - `SECRET_KEY` should change to a different but equally long and random value. It is recommended that you use [`os.urandom`][12] for this.
 - `DEBUG` **must** be `False`.
 - `ALLOWED_HOSTS` should contain the hostname(s) on which you wish to serve your application. Just hostnames, e.g. `example.com` rather than `http://example.com:88`.
 - `DATABASES['default']['PASSWORD']` should change and should also be impractically hard to guess.
 - `STATIC_ROOT` should point to a directory where you want to collect all static files.

See also the [Django documentation][13].

[12]: https://docs.python.org/3/library/os.html#os.urandom
[13]: https://docs.djangoproject.com/en/1.11/ref/settings/


### Creating the database

You can follow the steps from `create_db.sql`, with two important differences:

 - The `createdb` permission is not needed in production, so you shouldn't include it.
 - The username, password and database name should be the same as the one in your settings overrides from the previous section.


### Configuring your webserver

How to configure your webserver is completely beyond the scope of this README. However, we can mention a few things to keep in mind:

 - Django will not serve static files in production mode. You need to configure the webserver to directly serve files from the `STATIC_ROOT` in your settings at the `STATIC_URL` in your settings.
 - Your webserver configuration should set environment variables or pass arguments to the WSGI application so it will use the settings overrides rather than the defaults from `ianalyzer/settings.py`.
