import { definePreset } from '@primeng/themes';
import Nora from '@primeng/themes/nora';

const bulmaPrimaryScheme = {
    50: 'var(--bulma-primary-95)',
    100: 'var(--bulma-primary-90)',
    200: 'var(--bulma-primary-80)',
    300: 'var(--bulma-primary-70)',
    400: 'var(--bulma-primary-60)',
    500: 'var(--bulma-primary-50)',
    600: 'var(--bulma-primary-40)',
    700: 'var(--bulma-primary-30)',
    800: 'var(--bulma-primary-20)',
    900: 'var(--bulma-primary-10)',
    950: 'var(--bulma-primary-05)',
}

const graySurfaceScheme = {
    950: 'var(--bulma-black)',
    900: 'var(--bulma-black-bis)',
    800: 'var(--bulma-black-ter)',
    700: 'var(--bulma-grey-darker)',
    600: 'var(--bulma-grey-dark)',
    500: 'var(--bulma-grey)',
    400: 'var(--bulma-grey)',
    300: 'var(--bulma-grey-light)',
    200: 'var(--bulma-grey-lighter)',
    100: 'var(--bulma-white-ter)',
    50: 'var(--bulma-white-bis)',
    0: 'var(--bulma-white)',
}

/***
 * Color palette based on bulma variables
 */
export const stylePreset = definePreset(Nora, {
    semantic: {
        primary: bulmaPrimaryScheme,
        colorScheme: {
            light: {
                surface: graySurfaceScheme,
                text: 'var(--bulma-text)',
                formField: {
                    background: 'var(--bulma-scheme-main)',
                    borderColor: 'var(--bulma-border)',
                    disabledBackground: 'var(--bulma-white-ter)',
                    disabledColor: 'var(--bulma-grey)',
                },
                content: {
                    borderColor: 'var(--bulma-border)',
                },
                overlay: {
                    modal: {
                        color: 'var(--bulma-text)',
                    }
                }

            },
            dark: {
                surface: graySurfaceScheme,
                text: 'var(--bulma-text)',
                formField: {
                    background: 'var(--bulma-scheme-main)',
                    borderColor: 'var(--bulma-border)',
                    disabledBackground: 'var(--bulma-black-ter)',
                    disabledColor: 'var(--bulma-grey)',
                    placeholderColor: 'var(--bulma-text-weak)'
                },
                content: {
                    borderColor: 'var(--bulma-border)',
                },
                overlay: {
                    modal: {
                        color: 'var(--bulma-text)',
                    }
                }
            }
        },
        formField: {
            borderRadius: 'var(--bulma-radius)',
            paddingY: 'calc(0.5em - var(--bulma-control-border-width))',
        },
        content: {
            borderRadius: 'var(--bulma-radius)',
        },
        overlay: {
            select: {
                borderRadius: 'var(--bulma-radius)',
            },
            modal: {
                borderRadius: 'var(--bulma-radius)',
            }
        }
    }
});
