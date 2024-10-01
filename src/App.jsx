import React from 'react';
import { useSelector } from 'react-redux';
import MainPage from './MainPage';
import useTelegramUser from './hooks/useTelegramUser';

function App() {
  useTelegramUser();
  const isAuthenticated = useSelector((state) => state.user.isAuthenticated);

  if (!isAuthenticated) {
    return <div>Loading...</div>;
  }

  return <MainPage />;
}

export default App;
