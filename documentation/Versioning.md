# Versioning

This document describes how versions are labelled, when we bring out new versions of Textcavator, and what you can expect when updating to a new version.

If you're a developer, you can use this document to determine what the label should be for your new version. After that, walk through the checklist in [Making a release](./Making-a-release.md) to publish the new version.

## Release labelling

Textcavator versions are based on [semantic versioning](https://semver.org/), so we distinguish between _major_, _minor_, and _patch_ releases. However, note that Textcavator is primarily a user application and does not offer a public API, so it does _not_ conform to semantic versioning.

Since Textcavator is not centered on an API, it's not always obvious what is considered "breaking" change. The lists below gives a more detailed breakdown of what can be included in a patch, minor, or major release.

A _patch_ release can include:

- Fixes to bugs
- Performance improvements
- Changes to the backend API
- Changes to the python or npm dependencies
- Database migrations
- Code quality improvements
- Documentation improvements

However, patch release cannot make meaningful changes to the frontend behaviour, deep routing in the frontend, or require updates in the server configuration.

A _minor_ release can include:

- Everything listed for patch releases
- New functionality in the frontend
- Layout changes to the frontend that don't remove functionality
- Backwards compatible changes to routing in the frontend. A change is backwards compatible if URLs from older versions will still direct to the same content.
- New corpus definitions
- Changes to the format for JSON corpus definitions where an older definition will continue to function as before.
- Changes to the format for Python corpus definitions, which may require older definitions to be updated.
- Changes that require minor updates to the server configuration that are backwards compatible, such as a new Django setting or environment variable.

A _major_ release can include:

- Everything listed for minor releases
- Removing functionality in the frontend
- Backwards incompatible changes to routing in the frontend: URLs from older versions will no longer direct to the same content
- Changes to the format for JSON corpus definitions that require updates to existing definitions.
- Changes that require updating the server configuration in a way that is _not_ backwards compatible

## When to make a release

Textcavator brings out regular releases every month. These are usually _minor_ releases that introduce a few new features and some bug fixes. For urgent bug fixes, we can also make _patch_ releases before the end of the month.

## Updating to a new version

If you're running an instance of Textcavator and a new version is released:

Updating after _patch_ releases is always recommended and should be straightforward. Make sure to:

- Pull the latest version of the source code
- Run `yarn postinstall` to update dependencies
- Run `yarn django migrate` to run migrations

On our own servers, the deployment script (`deploy.py`) takes care of all these steps.

For _minor_ and _major_ releases, make sure to check the release notes to see if they require changes to the server configuration. If you are adding your own Python corpus definitions (that are not in the Textcavator repository), check for updates in the format.

Note that for major releases, these changes may require significant work or make your server incompatible with older versions of Textcavator.
