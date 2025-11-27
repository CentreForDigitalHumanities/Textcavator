# SAML

In order to login with Solis ID, Textcavator has SAML integration with ITS. For this, it uses the [djangosaml2 library](https://djangosaml2.readthedocs.io/). More information on working with SAML, setting up a local environment to test the SAML integration, etc. can be found [here](https://github.com/UUDigitalHumanitieslab/dh-info/blob/master/SAML.md)

The urls exposed by DjangoSaml2 are included as part of our `users` application, e.g., `<hostname>/users/saml2/login`. DjangoSaml2 takes care of consuming the response from the Identity Provider and logging in the user. The `SAML_ATTRIBUTE_MAPPING` variable contains a dictionary of the data coming in from the identity provider, e.g., `uushortid`, and translating that to the corresponding column in the user table, e.g., `username`. Moreover, the setting `SAML_CREATE_UNKNOWN_USER = True` makes sure that we create a user in our database if it's not present yet.

The only tweaks added on top of the DjangoSaml2 package are:
- the logic to set the `saml` column to `True` for a user logging in with SAML. The `CustomSaml2Backend` overrides DjangoSaml2's `get_or_create_user` function to take care of this. Note that in the future, we could also turn this field into a `CharField` to keep track of multiple identity providers here.
- overriding DjangoSaml2's `LogoutView` to make its `post` method `csrf_exempt`. The response from the ITS Identity Provider does not send the csrf cookie in a way that it can be consumed by Django at the moment.

### Authorisation

The setting [SAML_GROUP_NAME](/documentation/Django-project-settings.md#saml_group_name) can be used to control permissions for SAML users.
