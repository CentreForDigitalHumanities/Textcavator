## Mapping

The current setting allows you to match tokens with standard/cleaned/stemmed analysis. Aggregation (e.g. most frequent tokens) can be done on the `:token` field which contains the token from the standard analyser. (Though you can omit stopwords by using an `exists` filter on the cleaned text.)

Perhaps worth considering:
- The text fields (for querying) could also contain the analysed token, and only use a `search_analyzer`.
- Different setup is required if you want to aggregate stemmed tokens, but I don't think we really need that?

The assumption right now is that the tokens for the standard analyser can also be used as tokens for the clean/stemmed analyser. Those analysers can only omit or transform tokens, but they can't merge or split them. This is valid for English/Dutch, but is it valid for all languages? And what if we want a different kind of analyser?

The other option is to store the fields separately, which I did in an earlier implementation. `content:standard`, `content:clean` and `content:stemmed` were all separate fields. For English, a single token is represented in a single document, written to all three fields. This uses a bit more storage, but it's not a massive difference.

But then if you wanted more control, you could also use separate documents that might use different segmentation.

## Threshold

You can configure a minimum frequency threshold which may limit the amount of storage used.

For some analysis, you can easily leave out all singletons, or even everything below a reasonable threshold like 20 or 50 occurrences, which you can quickly analyse in the corpus itself. Then you only use this to optimise high-frequency items.

That said, it is often simpler and more convenient if the BOW index just contains the exact data. For the troonredes corpus, leaving out singletons did not actually impact the data that much.

## Document IDs

Tag filters use the document id, so filters on `_id` should be converted to use `:doc_id`.

## Index name

The idea is that the bag-of-words index is called `{source_index}.bow`. Currently, this does not make good use of version numbers, so that needs to change.

If you have `my-corpus-1` with alias `my-corpus`, the BOW index is now called `my-corpus.bow`. Should be `my-corpus-1.bow` with alias `my-corpus.bow`.

Also, the management of index versions needs to be updated. If you want to delete an index version `my-corpus-1`, you typically also want to delete attached versions `my-corpus-1.*`.

Side note: if we do get around to storing word embeddings in ES to, this would use the same pattern, i.e. `my-corpus.wm`. Though for word embeddings, perhaps the index would not be so attached to the specific source index, but use its own numbering. So `my-corpus-1` with alias `my-corpus` as the original data, then `my-corpus.wm-1` with alias `my-corpus.wm` as the embedding data.

