import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // Customize primary color
    },
    background: {
      default: '#fafafa',
    },
  },
  shape: {
    borderRadius: 8, // Customize global border radius
  },
});

export default theme;
