import { definePreset } from '@primeng/themes';
import Nora from '@primeng/themes/nora';

const graySurfaceScheme = {
    950: 'var(--bs-black)',
    900: 'var(--bs-gray-900)',
    800: 'var(--bs-gray-800)',
    700: 'var(--bs-gray-700)',
    600: 'var(--bs-gray-600)',
    500: 'var(--bs-gray-500)',
    400: 'var(--bs-gray-400)',
    300: 'var(--bs-gray-300)',
    200: 'var(--bs-gray-200)',
    100: 'var(--bs-gray-100)',
    50: '#fafbfc',
    0: 'var(--bs-white)',
}

/***
 * Color palette based on bulma variables
 */
export const stylePreset = definePreset(Nora, {
    semantic: {
        colorScheme: {
            light: {
                surface: graySurfaceScheme,
                text: 'var(--bs-body-color)',
                formField: {
                    background: 'var(--bs-body-bg)',
                    borderColor: 'var(--bs-border-color)',
                    disabledBackground: 'var(--bs-secondary-bg)',
                    disabledColor: 'var(--bs-secondary-color)',
                },
                content: {
                    borderColor: 'var(--bs-border-color)',
                },
                overlay: {
                    modal: {
                        color: 'var(--bs-body-color)',
                    }
                }

            },
            dark: {
                surface: graySurfaceScheme,
                text: 'var(--bs-body-color)',
                formField: {
                    background: 'var(--bs-body-bg)',
                    borderColor: 'var(--bs-border-color)',
                    disabledBackground: 'var(--bs-tertiary-bg)',
                    disabledColor: 'var(--bs-tertiary-color)',
                    placeholderColor: 'var(--bs-secondary-color)'
                },
                content: {
                    borderColor: 'var(--bs-border-color)',
                },
                overlay: {
                    modal: {
                        color: 'var(--bs-body-color)',
                    }
                }
            }
        },
        formField: {
            borderRadius: 'var(--bs-border-radius)',
        },
        content: {
            borderRadius: 'var(--bs-border-radius)',
        },
        overlay: {
            select: {
                borderRadius: 'var(--bs-border-radius)',
            },
            modal: {
                borderRadius: 'var(--bs-border-radius)',
            }
        }
    }
});
