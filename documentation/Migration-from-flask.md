# Migrating from Flask

This documentation concerns environments that were already running Textcavator with a Flask backend (version 3.x or lower).

## Install django backend

Run `yarn install-back` to install the new python requirements.

If you do not have postreSQL installed, install it now.

Set up a new database and run migrations by running these commands from the backend:

```bash
psql -f create_db.sql
yarn django migrate
```

## Migrating SQL data

You may want to to migrate the SQL data to the new django backend. (You do not need to do anything for elasticsearch data.)

The SQL database contains the user data, so migration is essential for production environments. In a development environment, you may prefer to skip this step and just create a new superuser with `yarn django createsuperuser`.

This update constitutes a switch from Flask to Django, as well as a switch from mySQL to postgreSQL. Migration consists of three steps:
- Create .txt files of the old database from mySQL.
- Move your database backup to the desired location
- Import data into the postgreSQL database using the django shell.

In a *production* environment, the first two steps will need to be carried out by the system admin.

### Exporting data from mysql

To make database exports, your mySQL database user needs to have file privileges, which may not already be the case. You can grant these privileges to your user by getting into mySQL as the root user and running

```sql
grant all privileges on {database}.* to {user}@'localhost' with grant option;
```

or just execute the following as the root user.

Next, check where you are allowed to export files. (It seems to be the standard that mySQL will only allow you to export files to a specific directory.)

Run the following:

```sql
show variables like "secure_file_priv";
```

The output will specify the directory. I will assume that this is `/var/lib/mysql-files/`. If you get a different directory, substitute it in the steps below.

Run the following to export the data.

```sql
use ianalyzer;
select * from corpus into outfile '/var/lib/mysql-files/corpus.txt';
select * from corpora_roles into outfile '/var/lib/mysql-files/corpora_roles.txt';
select * from download into outfile '/var/lib/mysql-files/download.txt';
select * from query into outfile '/var/lib/mysql-files/query.txt';
select * from role into outfile '/var/lib/mysql-files/role.txt';
select * from user into outfile '/var/lib/mysql-files/user.txt';
```

### Move exported data

You exported data are in `/var/lib/mysql-files/`, which is inconvenient and requires sudo privileges to access, so you should move the files to a more convenient folder.

### Import data in django

Activate your python environment and run `yarn django shell`. Then run:

```python
from ianalyzer.flask_data_transfer import import_and_save_all_data
directory = 'path/to/your/data'
import_and_save_all_data(directory)
```

Regarding the directory:

- In production, the location of the flask migration is stored in the django settings. Use `directory = settings.FLASK_MIGRATION_DATA`
- If `directory` does not exist or does not contain relevant files, the script will not import anything.

The script expects to run on an **empty** database, as it will also copy object IDs. This means that if the script fails halfway through, you will need to reset the database before you can re-attempt. You can do this from the command line with `yarn django flush`.

### Update object IDs

Now you need to make sure that your new database is aware of the newest object IDs, or it will attempt to create new rows with duplicate IDs. Run the following commands from the backend:

```bash
python manage.py sqlsequencereset users | python manage.py dbshell
python manage.py sqlsequencereset addcorpus | python manage.py dbshell
python manage.py sqlsequencereset api | python manage.py dbshell
python manage.py sqlsequencereset download | python manage.py dbshell
```

## Add local settings

In `backend/ianalyzer`, make a file `settings_local.py`. Transfer relevant local settings you had configured in your `config.py` file for Flask.

Note that the new `settings_local` does not need all the information you had provided in`config`. For a development environment, is is probably sufficient to simply specify the `CORPORA`, and the locations of corpus source data and word model files.

## Transfer downloads

In the flask backend, the default storage location for CSV files was `/backend/api/csv_files/`.

In a development environment, the new default location is `/backend/download/csv_files/`. (This can be configured in settings.) You will have to move the contents of your CSV directory here if you want to keep your download history.

For a production environment, the csv files need to be moved from the old flask server to the new django server, if you are also moving servers. Check the deployment settings for the new location of the downloads. (This should be outside of the repository.)
