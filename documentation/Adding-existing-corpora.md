## Adding existing corpora

These instructions are for adding *already defined* corpora to your own environment. This means you would be working with a corpus that is already used in Textcavator or by other developers.

Documentation on creating *new* corpus definitions is in [Writing a corpus definition in Python](./Writing-a-corpus-definition-in-Python.md) / [Writing a corpus definition in JSON](./Writing-a-corpus-definition-in-JSON.md).

### Python corpora

Currently, all corpora that are used in production are *Python corpora*, meaning they are defined in the source code. To include these corpora in your environment, you need to add them to your local settings and create an index in Elasticsearch.

The source files of a corpus are not included in this directory; ask another developer about their availability. If you have (a sample of) the source files for a corpus, you can add the corpus your our environment as follows:

1. Add the corpus to the `CORPORA` dictionary in your local settings file. See [CORPORA settings documentation](/documentation/Django-project-settings.md#corpora).
2. Set configurations for your corpus. Check the definition file to see which variables it expects to find in the configuration. Some of these may be optional, but you will at least need to define the (absolute) path to your source files.
3. Activate your python virtual environment. Run the `loadcorpora` admin command (`yarn django loadcorpora`) to register the new corpus in the SQL database. Then create an ElasticSearch index from the source files by running, e.g., `yarn django index dutchannualreports`, for indexing the Dutch Annual Reports corpus in a development environment. See [Indexing](documentation/Indexing-corpora.md) for more information.

### Database-only corpora

Note: database-only corpora are still in development.

To add a database-only corpus, you will need a JSON definition of the corpus, and a CSV file with the source data. To retrieve a JSON definition from a running Textcavator server, log in as a staff user and visit `/corpus-definitions/`. Open the corpus you want to import and click "Download JSON".

1. Start up your Textcavator server and log in as a superuser. Go to `localhost:4200/corpus-definitions/new`. Upload the JSON definition file and save.
2. Open the editing form for the corpus. In step 1, you can upload an image, but this is optional. In step 2, upload your source data and save.
3. Continue to step 4 of the form and index the corpus. When indexing is complete, click "activate".
4. Visit the admin site at `/admin`. Go to "corpora" and select te corpus. Set "active" to true and save.

