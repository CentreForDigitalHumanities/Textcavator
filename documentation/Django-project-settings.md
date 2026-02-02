# Django project settings

This file describes how to configure project settings in Django.

## Different settings files

We keep different settings files to handle different environments.

`settings.py` is the default settings file in a development setting. The version in the repository is replaced in our deployment setup. This means that what you write here will affect all development environments, but not production environments. Developers can override settings in their own environment using `settings_local`, but this is a good place for sensible defaults.

`common_settings.py` is intended for "universal" project settings that apply in both production and development servers. It is imported by `settings.py` on both development and production.

`settings_local.py` is ignored in version control, but the development configuration `settings.py` will attempt to import it. This file can be used for sensitive information, or configurations that are unique to your setup, such as which corpora you're using. You can also use this to override any existing settings.

`settings_test.py` is used during unit tests. It imports everything configured in `settings.py`, but can add or override some settings. Note that you can also adjust settings for individual tests.

`settings_saml.py` can be used used during development, to enable signing in using the CDH Development Identity Provider. It imports `settings.py` and adds extra configurations. See [SAML](./SAML.md).

### Using a different settings module

Django supports using a different settings module ([more about settings in Django](https://docs.djangoproject.com/en/5.0/topics/settings/)).

However, the Celery configuration depends on `settings.py`, so when you run a command like `celery -A ianalyzer worker`, Celery will use the `settings.py` in `/backend/ianalyzer`.

This mean that you cannot simply point to an alternative settings module if you also need a celery worker; you should overwrite the `settings.py` file in `/backend/ianalyzer` before starting the worker.

## Project settings

For project settings supported by external libraries, see:

- [Django settings reference](https://docs.djangoproject.com/en/5.0/ref/settings/)
- [configuration for Django REST framework](https://www.django-rest-framework.org/api-guide/settings/)
- [configuration for dj-rest-auth](https://dj-rest-auth.readthedocs.io/en/latest/configuration.html)
- [configuration for djangosaml2](https://djangosaml2.readthedocs.io/contents/setup.html#configuration)
- [configuration for Celery](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html)

In addition, Textcavator adds the following settings.

### `SERVERS`

Configuration of elasticsearch servers. This is a dictionary. The keys are the (internal) names you give to each server. (You can connnect more than one server, though in most cases, you only need one.)

The values in the dictionary give specifications.

- `'host'` and `'port'` specify the address where you access the server
- `'chunk_size'`: Maximum number of documents sent during ES bulk operation
- `'max_chunk_bytes'`: Maximum size of ES chunk during bulk operation
- `'bulk_timeout'`: Timeout of ES bulk operation
- `'scroll_timeout'`: Time before scroll results time out
- `'scroll_page_size'`: Number of results per scroll page
- `'index_prefix'` (optional): For database-only corpora, this setting can be used to add a prefix to the names of indices created on this server. For example, you can set this to `'ianalyzer'` to generate index names like `'ianalyzer-times'`, `'ianalyzer-dutchnewspapers'`, etc. Does not affect corpora with Python definitions.

### API key

By default, an elasticsearch server will have security features enabled; you can turn this off for a local development server (see [first-time setup](./First-time-setup.md)). Otherwise, the server configuration must specify an API key.

To create an API key for the server, see [creating an API key](https://www.elastic.co/guide/en/elasticsearch/reference/current/security-api-create-api-key.html). Note down the `'id'` and `'api_key'` values of the response. Add the following values to the configuration:

- `'certs_location'`: Fill in the following path: `{your_elasticsearch_directory}/config/certs/http_ca.crt`
- `'api_id'`: the ID of the API key
- `'api_key'`: the generated API key


#### Setting a default server

If you name one of the servers `'default'`, it will act as the default for all corpora. This is especially recommended if you have only one server.

If you don't assign a default server this way, the server for each corpus must be configured explicitly in `CORPUS_SERVER_NAMES` (see below).

Unit tests for the backend will assume that there is a default server configured and use that one. Unit tests can create tests indices (always named `test-*`), which will be deleted during teardown.

### `CORPORA`

A dictionary that specifies Python corpus definitions that should be imported in your project.

Each key must be the import path to a corpus class (see [Django module loading](https://docs.djangoproject.com/en/5.2/ref/utils/#module-django.utils.module_loading)). For example:

```python
CORPORA = {
    'times': 'corpora.times.times.Times',
}
```

### `CORPUS_SERVER_NAMES`

A dictionary that specifies which elasticsearch server should be used for which corpus.

Each key in the dictionary should be the name for a corpus, i.e. one of the keys in the `CORPORA` setting. Each value should be the name for an elasticsearch server, i.e. one of the keys in the `SERVERS` setting.

You do not need to include corpora which use the `'default'` server.

### `LOGO_LINK`

URL of the logo of your organisation. This is used in emails sent to users.

### `NLTK_DATA_PATH`

Some functionality on Textcavator will download the stopwords corpus from [NLTK](https://nltk.readthedocs.io/en/latest/). This setting controls the directory where data downloaded from NLTK can be stored.

### `CSV_FILES_PATH`

Path to the directory where prepared download files for users should be stored.

### `WORDCLOUD_LIMIT`

The maximum number of documents that is analysed in the wordcloud (a.k.a. "most frequent words") visualisation.

### `BASE_URL`

The base URL for the application. This URL can be used to generate links to the frontend in emails and citation templates.

### `SAML_GROUP_NAME`

Optional, should be a string.

If you define a `SAML_GROUP_NAME` in settings, SAML users will always be added to a group with that name when they create an account. (The group will be created if it does not exist.) This can be used to give permissions to SAML users. The group is not used to handle authentication, so you can add non-SAML users to it as well.

### `DEFAULT_CORPUS_IMAGE`

A path (string) to an image file.

Corpora can include an image to use in the interface (e.g. in the corpus selection menu); if the corpus has no image, this one will be used instead.

### Settings for individual corpora

Python corpus definitions typically rely on the Django settings, to avoid hard-coding properties that depend on the server. When you include a corpus definition in your settings, read the source file to see the related settings. Some of these settings may be optional.
