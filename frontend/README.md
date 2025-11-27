# WebUi

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 10.2.3
This version of Angular uses Node 12.22.10.

# Prerequisites

Run `yarn` to install the dependencies. In `src/environments`, create a file `environment.private.ts` with the following settings:
```
privateEnvironment = {
    appName: Textcavator,
    aboutPage: ianalyzer
}
```
Alternatively, you can choose a different app name, or a different about page, if it exists in `/src/assets/about`.

## Development server

Run `npm start` for a dev server. Make sure the back-end (see `../README.md`) is running. Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

## Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory. Use the `-prod` flag for a production build.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).


## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI README](https://github.com/angular/angular-cli/blob/master/README.md).
