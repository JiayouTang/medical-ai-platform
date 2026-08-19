import { createTheme } from '@mui/material/styles';

// Adapted from Microsoft Data Formulator's MUI workbench direction and
// palette/token approach; not copied wholesale.
export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#0f6cbd' },
    secondary: { main: '#008060' },
    warning: { main: '#b7791f' },
    error: { main: '#b42318' },
    background: {
      default: '#f6f7f9',
      paper: '#ffffff',
    },
    text: {
      primary: '#172033',
      secondary: '#667085',
    },
  },
  shape: {
    borderRadius: 8,
  },
  typography: {
    fontFamily: [
      'Roboto',
      'Inter',
      'ui-sans-serif',
      'system-ui',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'sans-serif',
    ].join(','),
    h1: { fontSize: 20, fontWeight: 700, letterSpacing: 0 },
    h2: { fontSize: 15, fontWeight: 700, letterSpacing: 0 },
    body2: { letterSpacing: 0 },
    button: { textTransform: 'none', letterSpacing: 0, fontWeight: 700 },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          border: '1px solid rgba(16, 24, 40, 0.12)',
          boxShadow: '0 1px 3px rgba(16, 24, 40, 0.08)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          minHeight: 34,
        },
      },
    },
  },
});
