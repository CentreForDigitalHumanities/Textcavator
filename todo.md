## Mapping

The current setting allows you to match tokens with standard/cleaned/stemmed analysis. Aggregation (e.g. most frequent tokens) can be done on the `:token` field which contains the token from the standard analyser. (Though you can omit stopwords by using an `exists` filter on the cleaned text.)

Perhaps worth considering:
- The text fields (for querying) could also contain the analysed token, and only use a `search_analyzer`. Might make the initial processing faster?
- Different setup is required if you want to aggregate stemmed tokens, but I don't think we really need that?

The assumption right now is that the tokens for the standard analyser can also be used as tokens for the clean/stemmed analyser. Those analysers can only omit or transform tokens, but they can't merge or split them. This is valid for English/Dutch, but is it valid for all languages? And what if we want a different kind of analyser?

The alternative is to store the fields separately, which I did in an earlier implementation. `content:standard`, `content:clean` and `content:stemmed` were all separate fields. For English, a single token is represented in a single document, written to all three fields. This uses a bit more storage, but it's not a massive difference.

But then if you wanted more control, you could also use separate documents that might use different segmentation.

## Threshold

You can configure a minimum frequency threshold which may limit the amount of storage used.

This depends a bit on the purpose of the analysis. In many cases, you can easily leave out all singletons. If you're starting from a source document and encounter a singleton in the term_vectors, you already have all the information you need. If you're doing something like suggesting related queries for a search term, filtering all singletons is fine, and probalby something you would do anyway.

In some cases, the threshold could be even higher (like 20, 50, or even 10,000) because for anything below, you can just analyse on the corpus itself. The optimisation (which also means no sampling) is mostly useful for high-frequency items.

That said, you obviously have more options if the BOW index just contains the exact data.

## Document IDs

Tag filters use the document id, so filters on `_id` should be converted to use `:doc_id`.

## Index name

The idea is that the bag-of-words index is called `{source_index}.bow`. Currently, this does not make good use of version numbers, so that needs to change.

I think the most consistent, future-proof way would be to use separate version numbers for the BOW index but store the source index in the metadata.

Also, the management of index versions needs to be updated. If you want to delete an index version `my-corpus-1`, you typically also want to delete attached versions `my-corpus-1.*`.

Side note: if we do get around to storing word embeddings in ES to, this would use the same pattern, i.e. `my-corpus.wm`. Though for word embeddings, perhaps the index would not be directly related to the specific source index. So `my-corpus-1` with alias `my-corpus` as the original data, then `my-corpus.wm-1` with alias `my-corpus.wm` as the embedding data.

## Nested fields

Use a nested field to present the tokens as an array of nested documents. This avoids duplicating the metadata.
