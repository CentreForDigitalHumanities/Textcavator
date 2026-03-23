/** Typedef for environments; see documentation for description */
export interface Environment {
    production: boolean;
    appName: string;
    navbarBrand: {
        title: string;
        subtitle: string | undefined;
        logo: string;
        logoAlt: string | undefined;
    };
    appDescription?: string;
    aboutPage: string;
    apiUrl: string;
    adminUrl: string;
    samlLogoutUrl: string;
    showSolis: boolean;
    runInIFrame: boolean;
    directDownloadLimit: number;
    version: string;
    sourceUrl: string;
    logos?: string[];
    showCorpusFilters?: boolean;
    showNamechangeAlert?: boolean;
}
