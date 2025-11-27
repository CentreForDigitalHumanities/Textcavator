// The file contents for the current environment will overwrite these during build.
// The build system defaults to the dev environment which uses `environment.ts`, but if you do
// `ng build --env=prod` then `environment.prod.ts` will be used instead.
// The list of which env maps to which file can be found in `.angular-cli.json`.

// see /documentation/Frontend-environment-settings.md for a description of available settings
import { version } from './version';

export const environment = {
    production: false,
    appName: 'Textcavator',
    navbarBrand: {
        title: 'Textcavator',
        subtitle: undefined,
        logo: '/assets/logo.svg',
        logoAlt: undefined,
    },
    appDescription:
        `<p>
            Textcavator is a tool for exploring corpora (large collections of texts).
            You can use Textcavator to find relevant documents or visualise broader trends
            in the corpus.
        </p>

        <p>
            Designed with and for researchers in the humanities and social sciences,
            Textcavator offers an accessible interface to search a wide variety of
            corpora, such as newspaper archives, online book reviews, and
            orations. Additional corpora are available for members
            of Utrecht University.
        </p>

        <p>
            You can find out more about Textcavator on our <a href="/about">about page</a>,
            or start searching a corpus below.
    </p>`,
    aboutPage: 'ianalyzer',
    apiUrl: '/api/',
    adminUrl: '/admin/',
    samlLogoutUrl: '/users/saml2/logout/',
    showSolis: true,
    runInIFrame: false,
    directDownloadLimit: 1000,
    version,
    sourceUrl: 'https://github.com/CentreForDigitalHumanities/I-analyzer/',
    logos: undefined,
    showCorpusFilters: true,
};
