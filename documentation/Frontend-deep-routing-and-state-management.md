# Frontend: deep routing and state management

State management in the frontend can get messy very quickly. Textcavator captures information about the state of the frontend in the query parameters in the URL. This allows users to bookmark queries, visualisations, etc., but can make state management more complicated. This document gives a broad introduction to how we approach state management and synchronising query parameter in the frontend.

## Using models

Complex state management, especially state management that uses deep routing, is preferably handled through models. A model is essentially just an abstraction of the behaviour of the application. It may contain variables, observables, functions, etc. to "model" that behaviour and keep an internal state.

At its simplest, a model is just a class that you can instantiate in a component:

```typescript
class MyModel {
    // ...
}
```

A model handles data, API calls, and the state of the user's workflow, and is kept separate from Angular components, directives, and pipes. The job of a component/directive/pipe is to translate between the user interface and the model.

This keeps components lightweight and makes them more flexible: because the core data is implemented independently, you can split a component, swap a checkbox for a dropdown, etc. without messing up the data.

## Model construction

Usually, a model is created in the highest component that needs it, by calling `new MyModel()` - either when the component is created or when the model becomes relevant. You can share an instance of a model between components by providing it as input.

If this results in cumbersome input chains, you can also use [dependency injection]((https://v16.angular.io/guide/dependency-injection)) to provide models. You can make  model `Injectable` to provide it via dependency injection; for example, the [AuthService](../frontend/src/app/services/auth.service.ts) is used to model the user's authentication, and the [DropdownService](../frontend/src/app/shared/dropdown/dropdown.service.ts) is used to model the state of a single dropdown. Alternatively, you can provide a service that exposes a model, such as the [CorpusService](../frontend/src/app/services/corpus.service.ts) which components can use to access the `Corpus` model of the active corpus.

### Dependency injection: providing services to models

More complex models may require application services to make API calls, or listen to the global state of the application.

In those cases, provide the service as a private member variable in the constructor of the model:

```typescript
class MyModel {
    constructor(
        private apiService: ApiService,
    ) {
        // ...
    }
}
```

If the model instance is not provided through dependency injection, you will need to inject the dependencies in the component that creates the model. For example:

```typescript
@Component{
    selector: 'my-component',
    templateUrl: './my-component.component.html',
}
class MyComponent {
    model: MyModel;

    constructor(
        private apiService: ApiService,,
    ) {
        model = new MyModel(apiService);
    }
}
```

## Route parameters: StoreSync

A simple model can just use internal variables to track whatever state it needs to. However, if the model is tracking some query parameters in the route, state management becomes more complex.

Many different parts of the application have *something* to do with the route and depend on each other. Binding the state of a model to the route can also create non-responsive controls or feedback loops if not handled correctly.

To handle route synchronisation, models can extend the [`StoreSync` class](/frontend/src/app/store/store-sync.ts.ts). Objects in this class connect to a `Store` that will keep track of their parameters.

A "store" is essentially an abstraction for "a place that stores information". The query parameters in the route are a type of store, but an object in memory can also function as a store. Different types of stores are explained in in more detail below. As an abstract concept, it has a few important properties:

- It is a [key-value store](https://en.wikipedia.org/wiki/Key%E2%80%93value_database). A model will always work with specific keys in the store, and ignore everything else.
- Multiple models can be connected to the same store, allowing each model to store some information in it. This describes the behaviour we want to implement: multiple parts of the application synchronising their state with the route parameters.
- Because the store construction is primarily designed for route parameters, the *values* in the store are typically short and simple. They're parameters, not data. This isn't enforced on a technical level, but it's useful in understanding how stores are used.

If two models connect to the same store but their parameters do not overlap, they will act independently. If their parameters overlap, the state of those parameters will be synchronised between the models.

### Implementation

A minimal implementation of a stored model would look something like this:

```typescript
// the type of the model's internal state
interface MyState {
    foo: string
}

class MyModel extends StoreSync<MyState> {
    keysInStore = ['foo']; // lists the keys in the store that the model connects to

    constructor(store: Store) {
        super(store); // instantiate the parent class
        this.connectToStore(); // subscribe to the store
    }

    // translates the representation in the store to the internal state of the model
    storeToState(params): MyState {
        return {
            foo: params['foo'] || ''
        };
    }

    // translates the internal state of the model to the representation in the store
    stateToStore(state: MyState) {
        return {
            foo: state.foo || null
        };
    }
}
```

As a child of the `StoreSync` class, `MyModel` will now include:
- a BehaviorSubject `state$` which tracks the latest state of the model based on the store.
- a method `setParams()` which updates some or all of the properties in the model's state by sending an update to the store.
- a method `complete()`: the model will stop observing the store and reject any further updates. It will also send an update to the store to reset its parameters.

See [store-sync.ts](/frontend/src/app/store/store-sync.ts) for the exact specification. In practice, the methods can be used like this:

```typescript
@Component{
    selector: 'my-component',
    templateUrl: './my-component.component.html',
}
class MyComponent implements OnInit, OnDestroy {
    myModel: MyModel;

    constructor(routerStoreService: RouterStoreService) { }

    ngOnInit() {
        this.myModel = newModel(this.routerStoreService);

        console.log(this.myModel.state$.value);
        // { 'foo': '' }
    }

    exampleUpdate() {
        this.myModel.setParams({foo: 'example'});
        console.log(this.myModel.state$.value);
        // { 'foo': 'example' }
    }

    ngOnDestroy() {
        this.myModel.complete();
    }
}
```

Notes:

The methods `storeToState` and `stateToStore` have to be implemented on the model class. They translate between stored strings and whatever is more convenient as an internal state. This is trivial in the example above, but often comes in handy. These functions must be each other's inverse. There should be unit tests to confirm this.

Note that the constructor of `MyModel` calls the method `connectToStore`. This initialises the `state$` observable based on the current state of the store, and creates a subscription to the store. You should call this method in the constructor. It's not called in the constructor of `StoreSync` because you may want to set some properties specific to your model before you call it (`connectToStore` uses `storeToState` to set the initial state).

`keysInStore` specifies the specific keys in the store's state that the model interacts with. The model will only listen to changes in those keys, and will reset them when it is completed.

## Stores

A store keeps track the states of one or more models. There are two store classes:
- The [`RouterStoreService`](/frontend/src/app/store/router-store.service.ts) synchronises its state with the query parameters in the route.
- The [`SimpleStore`](/frontend/src/app/store/simple-store.ts) just stores the data internally and doesn't use any backend.

Crucially, `StoreSync` models don't care which store class you use: they implement the same API. This API consists of three endpoints:

- `params$`: an observable of the stored state
- `currentParams()`: get the current state synchronously, rather than as an observable
- `paramUpdates$`: an observer to which updates are pushed

The state of a store can be represented as a key-value object. Each model class listens to a pre-defined list of keys in this object. If you set the value of a key to `null`, it will be removed.

Because the `RouterStoreService` stores data in the address bar of the browser, the value of stored keys is always a string. So if you call `store.paramUpdates$.next({a: 5})`, the `params$` observable will return the value as `{a: '5'}`. The `SimpleStore` mimicks this behaviour for consistency.

## What to store and where to store it

Keep in mind that the primary purpose of the store system is to handle route parameters, and the primary purpose of route parameters is reproducibility for researchers. Just because a model has some notion of a "state" does not mean it needs to use a `Store`.

If a model does use the route, it may make sense that the model is tracking *some* keys in the store, but also keeps some extra variables or observables to handle things that don't need to be represented in the route, and which will reset when you refresh the page.

### `RouteStoreService` and `SimpleStore`

In practice, models often use the `RouterStoreService` when they are being used in components, but in a unit test, you substitute the `SimpleStore` for an easier setup.

However, some models, like the `QueryModel`, are used with both store types during runtime. The `QueryModel` is instantiated with the `RouterStoreService` when it concerns the main query made by the user. But if we want to construct a query to generate a link, run a request with an extra filter, etc., we can instantiate a query model with the `SimpleStore`, which will not be synchronised with the route.

This is an important reason why stores are separated from models, instead of being built into them.

## Testing store-synced models

As mentioned above, `StoreSync` models are typically instantiated with the `RouterStoreService` during runtime, but you can use the `SimpleStore` during testing.  The [tests for the `SearchTabs` model](../frontend/src/app/search/search-tabs.spec.ts) are a minimal example of such tests.

Examples of tests:

- For a possible `state`, assert that `model.storeToState(model.stateToStore(state))` equals `state`.
- Initialise the model with an empty store and check the initial state.
- Initialise the model with a non-empty store and check the initial state. This simulates loading the page from a link with query parameters.
- Try calling a method of the model that should update the state, and check the effect.
- Update the store directly, and check that the model reflects it. This simulates what happens when the user uses back/forward navigation in the browser, or another model updating the same parameter. (The latter is not always applicable, but the former is.)

The purpose of these tests is to verify the model's conversion between its internal state and the store, and the ways in which the model is meant to react to changes in the parameters.

For an individual model, you do *not* need to test the core logic of the `StoreSync` and `Store` classes, such as whether the model actually ignores other keys in the store, or whether `SimpleStore` and `RouterStoreService` are compatible. (Those classes have their own unit tests; feel free to expand those, of course.)
