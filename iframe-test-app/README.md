# iframe test app

This is a minimal setup to test embedding Textcavator in another site using an iframe. It serves a web page that embeds your Textcavator development server. You can use it to test the layout, or try out the workflow in an embedded frame.

## Usage

The test app is run using `server.py`. It requires Python to use, no dependencies.

To run, start your Texcavator development server. Then run the container app by running:

```sh
python server.py
```

The container app will run at http://localhost:9000/. Use ctrl + C to quit.

The iframe will show `/search/troonredes/`, so on your Textcavator server, the Troonredes corpus should be active and public (or you can change the source url in `index.html`).
