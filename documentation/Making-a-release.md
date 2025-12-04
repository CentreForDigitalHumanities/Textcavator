# Making a release

This is a quick checklist for developers publishing new releases. For more information about when to make releases and what to label them, see [Versioning](./Versioning.md).

> [!IMPORTANT]
> Make sure to read this *entire* document when making a release. *Every* step is required.

It's recommended that you use [git-flow to make releases](https://danielkummer.github.io/git-flow-cheatsheet/#release), but it's not technically required.

## Check if we are release-ready

Check if anything ought to be included with the new release:

- Check [open pull requests](https://github.com/CentreForDigitalHumanities/Textcavator/pulls)
- Check [issues labelled "bug"](https://github.com/CentreForDigitalHumanities/Textcavator/issues?q=is%3Aissue+is%3Aopen+label%3Abug)
- Check project boards that keep track of a release cycle. If issues or PRs are scheduled for this release, wait until they are closed or move them to the next release cycle.

Discuss open pull requests, known bugs, and scheduled issues with your fellow developers. If you agree that the develop branch is release-ready, move on to the next step.

## Make a release branch

Determine if your release is a major, minor, or patch release to figure out the version number (see [Versioning](./Versioning.md)).

Start a new branch for your releases. Use `git flow release start x.x.x` or `git flow hotfix start x.x.x`.


Use the `yarn [major|minor|patch]` command to update the version number in `package.json`. This also updates the `CITATION.cff` file with the new version number and release date.

## Check if everything works

In your local environment, start up elasticsearch and run backend tests with `yarn test-back`. Run frontend tests with `yarn test-front`.

Publish the release branch with `git flow release publish x.x.x`. Deploy on the test or acc server. Check that everything works as intended.

## Finish the release

Make a tag for your release and merge it into `develop` and `master`. You can do all this with `git flow release finish x.x.x`. Push the tag and the changes to develop and master.

## Check configuration changes

You'll need this for the following two steps: write down what needs to be changed in the configuration of a Textcavator server (development or production).

Look for changes in [settings.py](/backend/ianalyzer/settings.py) or [environment.ts](/frontend/src/environments/environment.ts). You can also look through the list of pull requests, which should note any configuration changes in their description.

## Write release notes

Create a release on the github repository based on the tag, and write release notes. (Tip: let Github auto-generate release notes and use those as a starting point.)

The release notes should include:
- A list of pull requests. Give each PR a description that is comprehensible for users or outsiders, and link the PR.
- An overview of required changes in server configuration, if any.
- A link to the diff with the last release.

## Deploy on production

Check your list of configuration changes and update the deployment configuration, if needed.

Deploy the `master` branch on the production server.
