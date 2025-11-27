import { version } from './version';

export const environment = {
    production: true,
    appName: 'Something completely different',
    navbarBrand: {
        title: 'Textcavator',
        subtitle: undefined,
        logo: '/assets/logo.png',
        logoAlt: undefined,
    },
    aboutPage: 'people-parliament.md',
    apiUrl: '/api',
    adminUrl: '/admin',
    samlLogoutUrl: '/users/saml2/logout/',
    showSolis: true,
    runInIFrame: false,
    directDownloadLimit: 1000,
    version,
    sourceUrl: 'https://github.com/CentreForDigitalHumanities/I-analyzer/',
    logos: undefined,
};
