# First time setup (for developers)

These are instructions to set up an Textcavator server. If you are going to develop Textcavator, start by following these instructions.

## Prerequisites

* Python == 3.12
* PostgreSQL >= 14, client, server and C libraries
* [ElasticSearch](https://www.elastic.co/) 8. To avoid a lot of errors, choose the option: install elasticsearch with .zip or .tar.gz. ES wil install everything in one folder, and not all over your machine, which happens with other options.
* [Redis](https://www.redis.io/). Recommended installation is [installing from source](https://redis.io/docs/getting-started/installation/install-redis-from-source/)
* [Node.js](https://nodejs.org/). See [.nvmrc](/.nvmrc) for the recommended version.
* [Yarn](https://yarnpkg.com/)

The documentation includes a [recipe for installing the prerequisites on Debian 10](./documentation/Local-Debian-Textcavator-setup.md)

## First-time setup

For the SAML integration, the following libraries are required: xmlsec, python3-dev, libssl-dev and libsasl2-dev. This has been tested on Unix systems, but installation may be more difficult on Windows. As the dependencies on `xmlsec` are only called in the `settings_saml` module, however, they should not affect running the application when not explicitly using this settings module.

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

> [!NOTE]
> With Postgresql 15 later, you may need to grant privileges on the schema too. Use the `psql` command in the terminal, and run the following:
>
> ```
> \c ianalyzer
> grant all privileges on all tables in schema public to ianalyzer;
> ```
>

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


## Adding corpora

These instructions are for adding *already defined* corpora to your own environment. This means you would be working with a corpus that is already used in Textcavator or by other developers.

In a first-time setup, it is recommended that you add at least one existing corpus before creating your own. Documentation on creating new corpus definitions is in [Writing a corpus definition in Python](./Writing-a-corpus-definition-in-Python.md) / [Writing a corpus definition in JSON](./Writing-a-corpus-definition-in-JSON.md).

### Python corpora

Currently, all corpora that are used in production are *Python corpora*, meaning they are defined in the source code. To include these corpora in your environment, you need to add them to your local settings and create an index in Elasticsearch.

The source files of a corpus are not included in this directory; ask another developer about their availability. If you have (a sample of) the source files for a corpus, you can add the corpus your our environment as follows:

1. Add the corpus to the `CORPORA` dictionary in your local settings file. See [CORPORA settings documentation](/documentation/Django-project-settings.md#corpora).
2. Set configurations for your corpus. Check the definition file to see which variables it expects to find in the configuration. Some of these may be optional, but you will at least need to define the (absolute) path to your source files.
3. Activate your python virtual environment. Run the `loadcorpora` admin command (`yarn django loadcorpora`) to register the new corpus in the SQL database. Then create an ElasticSearch index from the source files by running, e.g., `yarn django index dutchannualreports`, for indexing the Dutch Annual Reports corpus in a development environment. See [Indexing](documentation/Indexing-corpora.md) for more information.

### Database-only corpora

Note: database-only corpora are still in development and not yet recommended for first-time users.

To add a database-only corpus, you will need a JSON definition of the corpus, and a directory with (a sample of) the pre-processed source data. To retrieve a JSON definition from a running Textcavator server, log in as a staff user and visit `/corpus-definitions/`. Open the corpus you want to import and click "Download JSON".

1. Start up your Textcavator server and log in as a staff user. Go to `localhost:4200/corpus-definitions/new`. Upload the JSON definition file and save.
2. Visit the admin menu (`localhost:4200/admin`). Go to "corpus configurations" and select your corpus. In the "data directory" field, add the path to your source data directory.
3. Activate your python virtual environment. Create an ElasticSearch index from the source files by running `yarn django index {corpusname}`. See [Indexing](documentation/Indexing-corpora.md) for more information.
4. Visit the admin menu again. Go to "corpora" and select te corpus. Set "active" to true and save.


## Running a dev environment

1. Start your local elasticsearch server. If you installed from .zip or .tar.gz, this can be done by running `{path your your elasticsearch folder}/bin/elasticsearch`
2. Activate your python environment. Start the backend server with `yarn start-back`. This creates an instance of the Django server at `127.0.0.1:8000`.
3. (optional) If you want to use celery, start your local redis server by running `redis-server` in a separate terminal.
4. (optional) If you want to use celery, activate your python environment. Run `yarn celery worker`. Celery is used for long downloads and the word cloud and ngrams visualisations.
5. Start the frontend by running `yarn start-front`.
