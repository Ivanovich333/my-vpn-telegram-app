// src/pages/Home.tsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Avatar,
  Stack,
  CircularProgress,
  Alert
} from '@mui/material';
import SignalWifiStatusbar4BarIcon from '@mui/icons-material/SignalWifiStatusbar4Bar';
import DataUsageIcon from '@mui/icons-material/DataUsage';

interface HomeProps {
  user: any;
  vpnStatus: string;
  trafficLeft: number;
}

const Home: React.FC<HomeProps> = ({ user, vpnStatus, trafficLeft }) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Ваш код для получения данных
        // Пример:
        // const response = await fetch('/api/vpn-status');
        // if (!response.ok) {
        //   throw new Error('Network response was not ok');
        // }
        // const data = await response.json();
        // setVpnStatus(data.status);
        // setTrafficLeft(data.trafficLeft);

        // Для демонстрации используем задержку
        await new Promise((resolve) => setTimeout(resolve, 2000));

        // После успешной загрузки данных
        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch VPN data:', err);
        setError('Failed to load VPN data.');
        // Если у вас есть функция для обновления статуса VPN, вызовите её
        // Например: setVpnStatus('Error');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 2 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Stack direction="row" spacing={2} alignItems="center">
            <Avatar alt={user?.username || user?.first_name} src={user?.photo_url} />
            <Typography variant="h6">
              {user?.username || `${user?.first_name} ${user?.last_name}`}
            </Typography>
          </Stack>
        </CardContent>
      </Card>

      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Stack direction="row" spacing={2} alignItems="center">
            <SignalWifiStatusbar4BarIcon color="primary" fontSize="large" />
            <Box>
              <Typography variant="subtitle1">VPN Status</Typography>
              <Typography variant="h6">{vpnStatus}</Typography>
            </Box>
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Stack direction="row" spacing={2} alignItems="center">
            <DataUsageIcon color="primary" fontSize="large" />
            <Box>
              <Typography variant="subtitle1">Traffic Left</Typography>
              <Typography variant="h6">{trafficLeft} GB</Typography>
            </Box>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Home;
