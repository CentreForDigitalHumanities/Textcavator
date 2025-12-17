# Named Entities
Textcavator has the capacity to display named entities.

## Named entity fields
To determine whether named entities are available for a given corpus, the application checks if a given corpus contains fields ending with `:ner`.

If the main content field is called `speech`, the field containing named entity annotations should be called `speech:ner`. This field should have the following Elasticsearch mapping:
```python
{
    'type': 'text',
    'index': False,
}
```

Moreover, an enriched corpus should contain the following keyword fields:
- `person:ner-kw`
- `location:ner-kw`
- `organization:ner-kw`
- `miscellaneous:ner-kw`
These can be used to search or filter (to be implemented).

## Enriching a corpus with named entities
To enrich a corpus with named entities, we recommend using the [TextMiNER](https://github.com/CentreForDigitalHumanities/TextMiNER) library. This library will read from an existing index and a specified field name. The content of the field is analyzed with the BERT-based models for named entity recognition provided by [flair](https://github.com/flairNLP/flair). The library then adds named entities to the `annotated_text` field and the keyword fields, as outlined above.
