# Updating Angular

This document contains some pointers for major Angular updates in the frontend.

Before you start, check the Node requirements and make sure the server is running a compatible Node version.

Use the [Angular update guide](https://angular.dev/update-guide) to walk through the necessary steps.

Several frontend libraries are tied to specific Angular version and will need to be updated as well. This can also be done with `ng update`. For example, this command was used to update to Angular 21:

```sh
yarn ng update @angular/core@21 @angular/cli@21 primeng@21 @fortawesome/angular-fontawesome@4 ngx-cookie-service@21 ngx-matomo-client@9 ngx-quill@29
```

