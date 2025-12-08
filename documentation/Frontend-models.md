# Frontend: models

This document covers some of the core models that make up the frontend.

Textcavator has [a general system for route parameter management](./Frontend-deep-routing-and-state-management.md) which many of these models use.

## QueryModel

The QueryModel is an essential model to the functionality of Textcavator. In essence, a QueryModel represents a query, which defines a set of document in a corpus. Different parts of the application build on queries to represent pages results, visualisations, etc.

When the frontend creates an [API query](./Query-api.md) for a request, it typically uses a QueryModel to generate a [compound query clause](https://www.elastic.co/guide/en/elasticsearch/reference/current/compound-queries.html) that defines which documents to select.

The internal structure of the query model is based on the query interface that the application offers to users. It consists of an optional query string (using [simple query string syntax](https://www.elastic.co/guide/en/elasticsearch/reference/8.11/query-dsl-simple-query-string-query.html#simple-query-string-syntax)), a list of fields on which the query string should applied, and a list of filters. See the [elasticsearch documentation about query context and filter context](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-filter-context.html).

### Using the query model

The query model controls a lot of variables (the query string, search fields, and the setting for each filter). Modules that represent the *outcome* of a query (documents, statistics, etc.) observe the `update` subject on the query model. This is a single subject that signals when the query has changed in some way that affects the results.

If a module is representing the results of a query, it should always use the `update` subjects and not subscribe to individual parameters. That way, if we ever need to change the parameters of the query model, other modules will continue functioning as normal.

Some modules may require an adjusted version of the query. For instance, the multiple choice filter fetches the options for a keyword field, but that means it needs to ignore an active filter on the field itself. In such cases, you can use the `clone()` method of the query model to create a copy that can be adjusted without affecting the original.

In other cases, it makes sense to construct a new query model that is not based on the "main" query of the user. For instance, depending on the corpus settings, documents can include a link to their "context". To do this, you can simple create a new `QueryModel` instance and use the `toQueryParams()` method to generate a link.

(When cloning a query model or creating a new one, the new model should not use the same store as the main query, as that would synchronise the models.)

### Search filters

The query model includes an array of `filters`; each is an object that implements the `FilterInterface`. The concrete class of the filter is based on the type of data it controls.

- If a field has a filter widget, it will have a `RangeFilter`, `DateFilter`, etc. suited to the type of widget.
- Some corpus fields don't show a filter widget by default, but still support filtering on a specific value. The "document context" system makes use of this feature. These fields are also tracked in the model as `AdHocFilter`s.
- Finally, a query may also include a `TagFilter` which allows the user to sort on their assigned tags.

The route parameters will store a filter's value if it is active, and nothing if it is inactive. However, filters also have a "toggle" option, which allows the user to turn off an active filter but still retain its value.

For the route parameters, there is no distinction between deactivating a filter or resetting it: in both cases, the filter is not used, so the distinction does not matter for reproducing results. This means that the translation between the internal state of the filter and the route parameters is not exactly one-to-one.

## Results

It's a common situation that you need a model that will:

- observe a query model
- keep track of a few additional parameters
- request some data based on the query model and its own parameters

The [`Results` class](../frontend/src/app/models/results.ts) provides the basic logic to do this, so it's a suitable base for fetching search results, visualisation data, or statistics based on the query.

A typical example is the [`FrequentWordsResults` class](../frontend/src/app/models//results.ts) which fetches the most common words in a text field. This is used to generate the wordcloud visualisation.

Like any model connected to a store, a `Results` model must implement `stateToStore` and `storeToState`. This translates the model's own parameters to their representation in the store.

In addition, the model must implement a `fetch` method. This describes how to get the latest result based on the query and parameters. In a typical scenario, `fetch` makes a request to the backend and returns the response.

The `Results` class is responsible for knowing when to fetch new results, switching to the latest result, catching errors, and multicasting result observables. To keep track of the results, you can observe the `result$`, `error$` and `loading$` observables on the model.

If you subscribe to any of these observables, `fetch` will be called every time the query or parameters update. (If there are no observers, nothing is fetched.) If you want to cache results, you'll usually need to store them as class members. For instance, the [`MapDataResults` class](../frontend/src/app/models/map-data.ts) caches the coordinates for the centre of the map, so it is not refetched every time.

## Found document

The [`FoundDocument` class](../frontend/src/app/models/found-document.ts) represents a single document in the corpus. (It's not called `Document` to avoid confusion with the DOM interface.)

The core usage is just to display the values of the document, but the class also includes some methods to view and assign tags, link to the context of the document, view annotations, etc.

