## Adding existing corpora

These instructions are for adding *already defined* corpora to your own environment. This means you would be working with a corpus that is already used in Textcavator or by other developers.

Documentation on creating *new* corpus definitions is in [Writing a corpus definition in Python](./Writing-a-corpus-definition-in-Python.md), or in the user manual (for creating corpora through the corpus form).

### Python corpora

Currently, all corpora that are used in production are *Python corpora*, meaning they are defined in the source code. To include these corpora in your environment, you need to add them to your local settings and create an index in Elasticsearch.

The source files of a corpus are not included in this directory; ask another developer about their availability. If you have (a sample of) the source files for a corpus, you can add the corpus your our environment as follows:

1. Add the corpus to the `CORPORA` dictionary in your local settings file. See [CORPORA settings documentation](./Django-project-settings.md#corpora).
2. Set custom settings for your corpus. Check the definition file to see which variables it expects to find in the Django settings. Some of these may be optional.
3. Activate your python virtual environment. Run the `loadcorpora` admin command (`yarn django loadcorpora`) to register the new corpus in the SQL database. Then create an ElasticSearch index from the source files by running, e.g., `yarn django index mycorpus`. See [Indexing](./Indexing-corpora.md) for more information.

### Database-only corpora

Unlike Python corpora, database corpora are normally created and used on a single server, but the corpus form does support a JSON export/import.
