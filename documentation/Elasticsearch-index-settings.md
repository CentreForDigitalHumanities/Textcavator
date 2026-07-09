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

The names of multifields are standardised in the application, and come with expectations about what that multifield does. If you add a multifield with these names that does not contain the expected type of data, some functionality may break. Do not do this.

(Adding extra multifields is generally safe, but it can create transparency problems for the user if these fields are searchable.)

Multifields are never required, but they enable certain features in visualisations and the search interface.

For *text* fields, multifields are used to enable different analysers. See [text analyzes](./Text%20analysis.md) for more details.

For *keyword* fields, a `text` multifield can be added to support full-text search.

