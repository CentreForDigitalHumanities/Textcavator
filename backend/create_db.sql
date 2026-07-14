CREATE user ianalyzer WITH createdb PASSWORD 'ianalyzer';
CREATE DATABASE ianalyzer;
GRANT ALL ON DATABASE ianalyzer TO ianalyzer;
GRANT ALL ON SCHEMA public TO ianalyzer;
ALTER DATABASE ianalyzer OWNER TO ianalyzer;
