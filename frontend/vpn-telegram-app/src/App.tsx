// src/App.tsx
import React, { useEffect, useState } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Box, Typography, BottomNavigation, BottomNavigationAction } from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import Home from './pages/Home';
import MyKeys from './pages/MyKeys';
import RenewSubscription from './pages/RenewSubscription';


const App: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const [vpnStatus, setVpnStatus] = useState<string>('Loading...');
  const [trafficLeft, setTrafficLeft] = useState<number>(0);
  const [navValue, setNavValue] = useState<string>('home');
  const location = useLocation();

  useEffect(() => {
    const path = location.pathname.substring(1) || 'home';
    setNavValue(path);
    const tg = window.Telegram.WebApp;
    tg.ready();

    const initDataUnsafe = tg.initDataUnsafe;
    setUser(initDataUnsafe?.user);

    const fetchVpnData = async (userId: number) => {
      try {
        const response = await fetch(`https://yourapi.com/vpn-status?userId=${userId}`);
        const data = await response.json();
        setVpnStatus(data.status);
        setTrafficLeft(data.trafficLeft);
      } catch (error) {
        console.error('Failed to fetch VPN data:', error);
        setVpnStatus('Error');
      }
    };

    if (initDataUnsafe?.user) {
      fetchVpnData(initDataUnsafe.user.id);
    }
  }, [location]);

  const navigate = useNavigate();

  const handleNavChange = (event: React.ChangeEvent<{}>, newValue: string) => {
    setNavValue(newValue);
    navigate(`/${newValue}`);
  };

  return (
    <>
      <Routes>
        <Route path="/" element={<Home user={user} vpnStatus={vpnStatus} trafficLeft={trafficLeft} />} />
        <Route path="/home" element={<Home user={user} vpnStatus={vpnStatus} trafficLeft={trafficLeft} />} />
        <Route path="/keys" element={<MyKeys />} />
        <Route path="/renew" element={<RenewSubscription />} />
      </Routes>

      {/* Navigation */}
      <Box sx={{ position: 'fixed', bottom: 0, left: 0, right: 0 }}>
        <BottomNavigation value={navValue} onChange={handleNavChange}>
          <BottomNavigationAction label="Home" value="home" icon={<HomeIcon />} />
          <BottomNavigationAction label="My Keys" value="keys" icon={<VpnKeyIcon />} />
          <BottomNavigationAction label="Renew Subscription" value="renew" icon={<AutorenewIcon />} />
        </BottomNavigation>
      </Box>
    </>
  );
};

export default App;
