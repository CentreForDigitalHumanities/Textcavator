# Continuous Integration

We use Github Actions to run unit tests, and to publish a docker image which can be used for indexing in the Peace Portal project.

## Test workflow

The test workflow runs separate actions for the unit tests in the backend and the unit tests in the frontend. (See [notes for development](./Notes-for-development.md#testing) for more information about testing.)

Tests are run on PRs. Frontend tests are only run when the PR makes changes to the frontend, backend tests only when there are changes to the backend.

In addition, there is a "fallback test" workflow which contains identically named actions ("test backend" and "test frontend"), which always succeed. This is to satisfy Github branch protection rules in case the actual test is skipped.

There is no workflow for functional tests, which are intended to be run on a production server, rather than a sandbox environment. (However, the functional tests are currently  not used.)

### Docker images

There is a separate workflow to build and publish docker images for the frontend and backend, which are used in the unit test workflows. There are pushed every first of the month and whenever a tag is pushed to the repository (typically for a release). They can also be triggered manually. Test workflows always used the latest docker image.
