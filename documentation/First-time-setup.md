# First time setup (for developers)

These are instructions to set up an Textcavator development server. If you are going to develop Textcavator, start by following these instructions.

## Prerequisites

* Python == 3.12
* PostgreSQL >= 12, client, server and C libraries
* [ElasticSearch](https://www.elastic.co/) 8. To avoid a lot of errors, choose the option: install elasticsearch with .zip or .tar.gz. ES wil install everything in one folder, and not all over your machine, which happens with other options.
* [Redis](https://www.redis.io/). Recommended installation is [installing from source](https://redis.io/docs/getting-started/installation/install-redis-from-source/)
* [Node.js](https://nodejs.org/). See [.nvmrc](/.nvmrc) for the recommended version.
* [Yarn](https://yarnpkg.com/)

The documentation includes a [recipe for installing the prerequisites in a distrobox container](./Distrobox%20development%20setup.md).

## First-time setup

To get an instance running, do all of the following inside an activated `virtualenv`:

1. Create the file `backend/ianalyzer/settings_local.py`.`ianalyzer/settings_local.py` is included in .gitignore and thus not cloned to your machine. It can be used to customise your environment. You can leave the file empty for now.
2. Install the requirements for both the backend and frontend:
```sh
yarn postinstall
```
3. For an easy setup, locate the file `config/elasticsearch.yml` in your Elasticsearch directory, and set the variable `xpack.security.enabled: false`. Alternatively, you can leave this on its default value(`true`), but this requires [additional settings](./Django-project-settings.md#api-key).
4. Set up your postgres database:
```sh
psql -f backend/create_db.sql
yarn django migrate
```
5. Make a superuser account with `yarn django createsuperuser`

## Setup with Docker
Alternatively, you can run the application via Docker:
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and start it.
2. Make an .env file next to this README, which defines the configuration for the SQL database and Redis. An example setup could look as follows:
```
SQL_HOST=db
SQL_PORT=5432
SQL_USER=myuser
SQL_DATABASE=mydb
SQL_PASSWORD=mysupersecretpassword
ES_HOST=elasticsearch
CELERY_BROKER=redis://redis
DATA_DIR=where/corpus/data/is/located/on/your/machine
```
3. Run `docker-compose up` from the directory of this README. This will pull images from the Docker registry and start containers based on these images. This will take a while to set up the first time. To stop, hit `ctrl-c`, run `docker-compose down` in another terminal, or use the Docker Desktop dashboard.
4. If you need to reinstall libraries via pip or yarn, use `docker-compose up --build`.

Note: you can also call the .env file .myenv and specify this during startup:
`docker-compose --env-file .myenv up`

## Add a test corpus

These instructions will add a tiny example corpus to your environment. Use this to verify that everything is working correctly. Open the file `/backend/ianalyzer/settings_local.py`. Copy-paste:

```py
CORPORA = {
    'example': 'corpora_test.basic.corpus.ExampleCorpus',
}
```

Save the file and close. For the next step, PostgreSQL and Elasticsearch must be running. Run in the terminal:

```sh
yarn django loadcorpora
yarn django index example
```

This will save the corpus configuration in the database and index the corpus data in Elasticsearch.

## Running a dev environment

1. Start your local elasticsearch server. If you installed from .zip or .tar.gz, this can be done by running `{path your your elasticsearch folder}/bin/elasticsearch`
2. Activate your python environment. Start the backend server with `yarn start-back`. This creates an instance of the Django server at `127.0.0.1:8000`.
3. (optional) If you want to use celery, start your local redis server by running `redis-server` in a separate terminal.
4. (optional) If you want to use celery, activate your python environment. Run `yarn celery worker`. Celery is used for long downloads and the word cloud and ngrams visualisations.
5. Start the frontend by running `yarn start-front`.

## Next steps

Now that you have a working Textcavator environment, here are some common next steps:

Configure your environment -> [Django project settings](./Django-project-settings.md) / [Frontend environment settings](./Frontend-environment-settings.md)

Add an existing corpus -> [Adding existing corpora](./Adding-existing-corpora.md)

Create a new Python corpus -> [Writing a corpus definition in Python](./Writing-a-corpus-definition-in-Python.md)

Add SAML intergration in your environment -> [SAML](./SAML.md)
