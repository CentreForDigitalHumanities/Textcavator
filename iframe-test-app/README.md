# iframe test app

This is a minimal application to test embedding Textcavator in another site using an iframe. It is essentially just a web page that embeds your Textcavator development server. You can use it to test the layout, or try out the workflow in an embedded frame.

## Usage

The test app is built using Vite. It requires Node and Yarn to run (which are also requirements for Textcavator itself.) To install dependencies, run from this directory:

```sh
yarn
```

To run, start your Texcavator development server. Then run the container app by running:

```sh
yarn dev
```

The container app will run at http://localhost:5173/

The iframe will show `/search/troonredes/`, so on your Textcavator server, the Troonredes corpus should be active and public (or you can change the source url).
