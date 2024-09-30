import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { ThemeProvider } from '@mui/material/styles';
import theme from './theme';
import { Provider } from 'react-redux';
import store from './store';
import '@twa-dev/sdk';

const { WebApp } = window.Telegram || {};

if (WebApp) {
  WebApp.ready();
} else {
  console.error('Telegram WebApp SDK not found');
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <App />
      </ThemeProvider>
    </Provider>
  </React.StrictMode>
);