import React from 'react';
import './App.css';
import Profile from './components/Profile';
import StatusSection from './components/StatusSection';
import ServerList from './components/ServerList';
import Stats from './components/Stats';
import ConnectButton from './components/ConnectButton';

function App() {
  return (
    <div className="app-container">
      <Profile />
      <h1>VPN Status</h1>

      <StatusSection />

      <ServerList />

      <Stats />

      <ConnectButton />
    </div>
  );
}

export default App;
