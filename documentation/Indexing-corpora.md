# Indexing corpora

Indexing is the step to read the source data of the corpus and load it into elasticsearch. Elasticsearch creates an *index* of the data, which makes it available for efficient searching and aggregations.

This step is necessary to make a dataset available in the Textcavator interface. Note that indexing can take a significant amount of time (depending on the amount of data).

You can start indexing once you have:
- Created a definition for the corpus
- Run all migrations
- Started Elasticsearch
- If it is a Python corpus:
    - added necessary settings to your project, such as the source data directory.
    - imported the definition into the database. For Python corpora, run `yarn django loadcorpora` to do this.

The basic indexing command is:

```bash
yarn django index my-corpus
```

## Parameters

Use `yarn django index --help` to see all possible parameters. Some useful options are highlighted below.

### Development

For development environments, we usually maintain a single index per corpus, rather than creating versioned indices. New indices are also created with `number_of_replicas` set to 0 (this is to make index creation easier/lighter).

Some options that may be useful for development:

- `--delete` / `-d` deletes an existing index of this name, if there is one. Without this flag, the script will raise an error if the index already exists.
- `--start` / `-s` and `--end` / `-e` respectively give a start and end date to select source files. Note that this only works if the `sources` function in your corpus definition makes use of these options; not all corpora have this defined. (It is not always possible to infer dates from source file metadata without parsing the file.)

### Production

See [Indexing on server](documentation/Indexing-on-server.md) for more information about production-specific settings.

## Scheduling and managing index jobs

When you run `index my-corpus`, the default options will start the process immediately, and store an `IndexJob` as a record. You can use the command line or the django admin to manage index jobs. It is also possible to run jobs asynchronously.

### Using the command line

The `index` command will store an `IndexJob` in the database that represents the action, which you may use as a log. You can use the `indexjob` command to view index jobs:

```sh
python manage.py indexjob list # view a list of all index jobs
python manage.py indexjob show 42 # inspect an index job
python manage.py indexjob show 42 --verbose # include all task parameters
```

If you want to create a job to run later, you can use `--create-only` in the `index` command. After this, you can start the job from the command line using `indexjob start`:

```sh
python manage.py index my-corpus --create-only
# > Created IndexJob #42
python manage.py indexjob start 42
```

When you start an index job through the `index`, `alias`, or `indexjob` commands, you can use the `--async` flag to schedule the job via [Celery](./Celery.md) instead of running it in your terminal:

```sh
python manage.py index my-corpus --async
```

You can interrupt jobs as follows:

```sh
python manage.py indexjob stop {id}
```

If you are running a job synchronously, you can also use a keyboard interrupt in the terminal.

When a job is stopped, the indexing process will halt, but it is not reversed, so if you use the `index` command to create and populate an index, you will likely end up with a partially populated index.

### Using the admin site

You can also manage index jobs using the admin site. Here you can view, create and edit jobs. To run a job from the admin site, select the job in the overview and use the action "start selected jobs". Jobs started from the admin are always run via Celery.

You can also use the "stop selected jobs" action to interrupt queued or working jobs. (This is equivalent to `indexjob stop`, described above.)

Note that in most cases, it is easier to create jobs via the command line, which offers a more streamlined experience.
