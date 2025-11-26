# Elasticsearch index settings

This document details how elasticsearch indices for Textcavator corpora are configured.

## Field mappings

Each corpus field passes a _mapping_ to elasticsearch that determines how the field is indexed - which affects what kind of queries it supports. See the [elasticsearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html) to read more about mappings in general.

Textcavator supports a limited number of mapping types, namely:

- text
- keyword
- integer
- float
- boolean
- date
- date range
- geo point

Field definitions use the constructor functions defined in [es_mappings.py](../backend/addcorpus/es_mappings.py), so mappings are not normally defined directly in a corpus definition.

### Multifields

Elasticsearch supports specifying a `fields` parameter to a field, which allows the same value to function with multiple mappings. This allows the application to offer multiple options for a field that would otherwise be incompatible. For example, a field can be treated as categorical (e.g. support a histogram visualisation), while still allowing full-text search.

The names of multifields are standardised in the application, and come with expectations about what that multifield does.If you add a multifield with these names that does not contain the expected type of data, some functionality may break. Do not do this.

Multifields are never required, but they enable certain features in visualisations and the search interface.

For *text* fields, multifields are used to enable different analysers. Normally, the main analyser for a field will only perform basic tokenisation and lowercasing. Multifields are used for more extensive language analysis:

- `*.clean_{language_string}`: uses a language-specific analyser to filter stopwords. It has a suffix indicating the language this analyser is for, e.g., `*.clean_en` for English.
- `*.stemmed_{language_string}`: uses a language-specific analyser to filter stopwords and stem words. It has a suffix indicating the language this analyser is for, e.g., `*.stemmed_en` for English.
- `*.length`: specifies the token count of the text, which is useful for aggregations.

For *keyword* fields, a multifield can be added to support full-text search:

- `*.text`: uses a text mapping to support full-text search in the field.

## Analysers

If the field mappings include fields with `clean*`, `stemmed*`, or `length` multifields, the elasticsearch settings for the corpus must define the appropriate analysers. The module [es_settings.py](/backend/addcorpus/es_settings.py) contains a function `es_settings` to generate the settings.

See [elasticsearch documentation about language analysers](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-overview.html).

The `clean*` and `stemmed*` analysers specify a stopword list, which is based on the stopwords corpus from [NLTK](https://www.nltk.org/). This analysis also includes a character filter to remove numbers.


