import os.path as op

from django.urls import reverse_lazy

import saml2
import saml2.saml
from saml2.sigver import get_xmlsec_binary

from ianalyzer.settings import *

TESTS_DIR = op.join(BASE_DIR, 'ianalyzer', 'tests')

INSTALLED_APPS.append('djangosaml2')
MIDDLEWARE.append('djangosaml2.middleware.SamlSessionMiddleware')
SAML_SESSION_COOKIE_NAME = 'saml_session'
SESSION_COOKIE_SECURE = True
LOGIN_URL = '/users/saml2/login/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SAML_CREATE_UNKNOWN_USER = True
ACS_DEFAULT_REDIRECT_URL = 'http://localhost:4200' # redirect to this url after logging in on Identity Provider
LOGOUT_REDIRECT_URL = 'http://localhost:4200'
SAML_LOGOUT_REQUEST_PREFERRED_BINDING = saml2.BINDING_HTTP_POST

SAML_ATTRIBUTE_MAPPING = {
    "uuShortID": ("username", ),
    "mail": ("email", ),
    "givenName": ("first_name", ),
    "uuPrefixSn": ("last_name", ),
    "saml": ("save_saml_login", ),
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'users.saml.CustomSaml2Backend',
)

SAML_CONFIG = {
    'xmlsec_binary': get_xmlsec_binary(['/opt/local/bin', '/usr/bin', '/usr/local']),
    # your entity id, usually your subdomain plus the url to the metadata view
    'entityid': 'http://localhost:8000/users/saml2/metadata/',

    # Permits to have attributes not configured in attribute-mappings
    # otherwise...without OID will be rejected
    'allow_unknown_attributes': True,

    # this block states what services we provide
    'service': {
        # we are just a lonely SP
        'sp' : {
            'name': 'Textcavator',
            'name_id_format': saml2.saml.NAMEID_FORMAT_TRANSIENT,
            'name_id_policy_format': saml2.saml.NAMEID_FORMAT_TRANSIENT,

            # For Okta add signed logout requests. Enable this:
            # "logout_requests_signed": True,

            'endpoints': {
                # url and binding to the assertion consumer service view
                # do not change the binding or service name
                'assertion_consumer_service': [
                    ('http://localhost:8000/users/saml2/acs/',
                     saml2.BINDING_HTTP_POST),
                    ],
                # url and binding to the single logout service view
                # do not change the binding or service name
                'single_logout_service': [
                    # Disable next two lines for HTTP_REDIRECT for IDP's that only support HTTP_POST. Ex. Okta:
                    ('http://localhost:8000/users/saml2/ls/',
                     saml2.BINDING_HTTP_REDIRECT),
                    ('http://localhost:8000/users/saml2/ls/post',
                     saml2.BINDING_HTTP_POST),
                    ],
                },

            'signing_algorithm':  saml2.xmldsig.SIG_RSA_SHA256,
            'digest_algorithm':  saml2.xmldsig.DIGEST_SHA256,

             # Mandates that the identity provider MUST authenticate the
             # presenter directly rather than rely on a previous security context.
            'force_authn': False,

             # Enable AllowCreate in NameIDPolicy.
            'name_id_format_allow_create': False,

             # attributes that this project need to identify a user
            'required_attributes': ['uushortid',
                                    'sn',
                                    'mail'],

             # attributes that may be useful to have but not required
            'optional_attributes': ['eduPersonAffiliation'],

            'want_response_signed': False,
            'authn_requests_signed': True,
            'logout_requests_signed': True,
            # Indicates that Authentication Responses to this SP must
            # be signed. If set to True, the SP will not consume
            # any SAML Responses that are not signed.
            'want_assertions_signed': True,

            'only_use_keys_in_metadata': False,

            # When set to true, the SP will consume unsolicited SAML
            # Responses, i.e. SAML Responses for which it has not sent
            # a respective SAML Authentication Request.
            'allow_unsolicited': False,

            # in this section the list of IdPs we talk to are defined
            # This is not mandatory! All the IdP available in the metadata will be considered instead.
            'idp': {
                # we do not need a WAYF service since there is
                # only an IdP defined here. This IdP should be
                # present in our metadata

                # the keys of this dictionary are entity ids
                'http://localhost:7000/saml/idp/metadata/': {
                    'single_sign_on_service': {
                        saml2.BINDING_HTTP_REDIRECT: 'http://localhost:7000/saml/idp/sso/post/',
                        },
                    'single_logout_service': {
                        saml2.BINDING_HTTP_REDIRECT: 'http://localhost:7000/saml/idp/slo/post/',
                        },
                    },
                'http://localhost:7100/saml/idp/metadata/': {
                    'single_sign_on_service': {
                        saml2.BINDING_HTTP_REDIRECT: 'http://localhost:7100/saml/idp/sso/post/',
                        },
                    'single_logout_service': {
                        saml2.BINDING_HTTP_REDIRECT: 'http://localhost:7100/saml/idp/slo/post/',
                        },
                    },
                },
            },
        },

    # where the remote metadata is stored, local, remote or mdq server.
    # One metadatastore or many ...
    'metadata': {
        'remote': [
            {
                "url": "http://localhost:7000/saml/idp/metadata/",
                "cert": "MIIERzCCAy+gAwIBAgIUbtUEUZUejbZK8Tikui/R+K9NOOwwDQYJKoZIhvcNAQELBQAwgbIxCzAJBgNVBAYTAk5MMRAwDgYDVQQIDAdVdHJlY2h0MRAwDgYDVQQHDAdVdHJlY2p0MRswGQYDVQQKDBJVdHJlY2h0IFVuaXZlcnNpdHkxDjAMBgNVBAsMBURILUlUMTMwMQYDVQQDDCpUZXN0IGNlcnRpZmljYXRlLCBETyBOT1QgVVNFIElOIFBST0RVQ1RJT04xHTAbBgkqhkiG9w0BCQEWDnQuZC5tZWVzQHV1Lm5sMB4XDTIyMDIxNTE1MzY1NloXDTMyMDIxMzE1MzY1NlowgbIxCzAJBgNVBAYTAk5MMRAwDgYDVQQIDAdVdHJlY2h0MRAwDgYDVQQHDAdVdHJlY2p0MRswGQYDVQQKDBJVdHJlY2h0IFVuaXZlcnNpdHkxDjAMBgNVBAsMBURILUlUMTMwMQYDVQQDDCpUZXN0IGNlcnRpZmljYXRlLCBETyBOT1QgVVNFIElOIFBST0RVQ1RJT04xHTAbBgkqhkiG9w0BCQEWDnQuZC5tZWVzQHV1Lm5sMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuTv14LG/Yz4icKj30aWeZidLtfNv2QRH1qObHJ5GXO4RtkyMW56t1oHsdN7e224kyazWBAPN1Cp97MTWrQRSo2e895qDqCdVL32Yr+52Irobn3mP7WFzkemqtfwsNCkniUSa6i1KfmljI/KUpc8I0lAKeHJCe5gHLxwZD/ZwPqbU913ftEeLS7EBSGRwhyigVVgDWjeVQ/GDSpmtZ/09FnjdpxT8B3B2GTOFiz+tQA//yAVqX1z8K4SUUj5ue8Vvyu4GRETx/vKZ/YCz3VPPdM33PyU60WlDjErlQjWxkMNvEhJ/dR//ctMswApL2AaIHBL4WDKcWzLilg/Cw5Zq5wIDAQABo1MwUTAdBgNVHQ4EFgQUenBSPtfdiO/xgqQLwdJzS6n5BSMwHwYDVR0jBBgwFoAUenBSPtfdiO/xgqQLwdJzS6n5BSMwDwYDVR0TAQH/BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAfUr3arSyQRSnSPROzx2awfvY7W+jxLHRd3mnzOg+7G2VjgbSaolzCATcg4ZBoRK577SSdGa7wdw/nEE+TEjqmUDSRFAE9QgZTz+zVVwhSraK7Epx+6anw6vmX3VY3W0gY43Tu+kvk72FB0k9MzRwpID3WIc6aYVQaav0NW8ZSoo6sk6CqVpv8hmpxF1mHOjsPe0Yaxi1ivd4Ij0Cy5dJiAa0JZaqyRavtn7eIzwEuZBzCSJDzljpa8Vh0j7RCPNcwnASyLQmYkvJMbcY3CtBs6uGx7sC+QBL/r5fyAQeJVkH8Glb8gi1lsV7a/EA1Tm4wvQmltIZ8tKql/8MaNi8sQ=="
            }
        ]
    },

    # set to 1 to output debugging information
    'debug': 1,

    # Signing
    'key_file': op.join(TESTS_DIR, 'saml_test_data', 'private.key'),  # private part
    'cert_file': op.join(TESTS_DIR, 'saml_test_data', 'public.pem'),  # public part

    # Encryption
    'encryption_keypairs': [{
        'key_file': op.join(TESTS_DIR, 'saml_test_data', 'private.key'),  # private part
        'cert_file': op.join(TESTS_DIR, 'saml_test_data', 'public.pem'),  # public part
    }],

    # own metadata settings
    'contact_person': [
        {'given_name': 'DH',
         'sur_name': 'Developer',
         'company': 'Research Software Lab',
         'email_address': 'dhlab@list.hum.uu.nl',
         'contact_type': 'technical'}
        ],
    # you can set multilanguage information here
    'organization': {
        'name': [('Utrecht University Centre for Digital Humanities, Research Software Lab', 'en')],
        'display_name': [('UU-CDH Research Software Lab', 'en')],
        'url': [('https://dig.hum.uu.nl', 'en')],
        },
}

SAML_GROUP_NAME = 'uu'
