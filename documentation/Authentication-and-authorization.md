# Authentication and authorization

> **This documentation is not up to date with version 4.x**

**Authentication** is the process of logging in the user, this can be done by logging in directly on the user database or using a Solis account. **Authorization** is the process of determining what that logged in user is allowed to do: e.g. go to the admin environment and search certain corpora. Both of these are modeled on the front end by the [`User class`](https://github.com/CentreForDigitalHumanities/Textcavator/blob/aee207f1a4e1a6fd2521f05f3f34839ab902247c/web-ui/src/app/models/user.ts) and handled by the [`User service`](https://github.com/CentreForDigitalHumanities/Textcavator/blob/aee207f1a4e1a6fd2521f05f3f34839ab902247c/web-ui/src/app/services/user.service.ts).

A user needs to be logged into both the Flask server (back end) and the Angular user interface (front end). The back end authentication and authorization is essential for the actual security: relying only on front end security would allow accessing the data through manually sending requests. Providing this security on the user interface is mostly for the usability of the application: show only corpora which can actually be queried, display the currently logged on user (or that the user isn't logged on yet) and what other parts of the application might actually be accessible. Ideally both the back end and front end would be in perfect harmony about the user's session status. This is however complicated because sessions are temporary: both the front-end and back-end can separately decide to cancel sessions. Generally because they expire, but it could also happen if a server is reset, the user logs off or the user decides to throw away cookies.

# Situations

## Logging on

A user logs in through the front end, this information is send to the back end if successful the user is logged on there and send back to the front end with information about the user. The user is then marked as logged on.

## Logging off

This can happen in the admin environment, in which case the front end also needs to be marked as logged off. If the user logs off from the front end, the back end needs to be notified and have its session destroyed as well: this is important to prevent someone else from maliciously accessing the data.

## Fallback to guest

It is possible to add a "guest" user in the admin without a password. If this is the case, a user can either be logged on as someone, or be logged on as the guest user. Because of this the `UserService` will attempt to log on as a guest user when the session is expired or non existent (logging off a user, session expired, opening the application for the first time).

## Session expires

Flask, like most back end frameworks, will expire a session after a certain period of inactivity. To prevent this from happening when the interface is open the `UserService` will periodically check the session on the server. If it is expired it will fallback to guest or be redirected to the login page. This can also happen if the user logged of from another tab.

## Check before querying

The [`ApiRetryService.requireLogin`](https://github.com/CentreForDigitalHumanities/Textcavator/blob/aee207f1a4e1a6fd2521f05f3f34839ab902247c/web-ui/src/app/services/api-retry.service.ts#L18) method is used by the query service to confirm that the session is still active before querying the server. If the user isn't logged on, it will fallback to "guest" or mark the session as expired.

## Page opened in new tab/page

When opening the front end on a new page, nothing is known yet about any active session. To allow the user to work in multiple tabs the current user is stored in the [local storage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage) and retrieved from there.

## Navigating

To check the authorization on (manual) navigation a [`LoggedOnGuard`](https://github.com/CentreForDigitalHumanities/Textcavator/blob/aee207f1a4e1a6fd2521f05f3f34839ab902247c/web-ui/src/app/logged-on.guard.ts) and [`CorpusGuard`](https://github.com/CentreForDigitalHumanities/Textcavator/blob/aee207f1a4e1a6fd2521f05f3f34839ab902247c/web-ui/src/app/corpus.guard.ts) exist. Both can (depending on the route) check the rights and if necessary redirect to the log on page detailing the lack of authorization.
