# Functional test suite
Functional tests are located in the folder `functional-tests`.

To run functional tests, make sure you have Selenium and Seleniumbase installed (from `functional-tests` requirements). Also, create a `selenium.ini` file in the `functional-tests` folder, which should have the following setup:
```
[credentials]
    username = {your_username}
    password = {your_password}

[corpus]
    name = {name_of_corpus_your_user_can_access}
    field = {multiple_choice_filter_field_name}
    first_option = {first_option_of_that_field}
    query = {query_term}
```

Note that some tests may be skipped based on the test corpus: e.g., if there are no word models, the corresponding tests will be skipped.

To run tests, navigate to the `functional-tests` folder and run `pytest --rs`. `--rs` stands for "reuse session" so after the view that tests logging in, the browser stays logged in. Other potential arguments:
```
--headless
--firefox
--safari
--edge
```
