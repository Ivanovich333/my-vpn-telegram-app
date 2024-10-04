import React, { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { Box, Typography, Button, Card, CardContent, Avatar } from '@mui/material';
import VpnLockIcon from '@mui/icons-material/VpnLock';
import { useSelector } from 'react-redux';
import { fetchVpnStatus } from './store/vpnSlice';
import { fetchUserTraffic, generateUserAccessKey } from './store/userSlice';
import { CircularProgress, Fade } from '@mui/material';


const MainPage = () => {
  const handleAccessKeyClick = () => {
    dispatch(generateUserAccessKey());
    // You might want to handle the response and display the access key
  };
  const pulseAnimation = {
    '@keyframes pulse': {
      '0%': {
        transform: 'scale(1)',
      },
      '50%': {
        transform: 'scale(1.05)',
      },
      '100%': {
        transform: 'scale(1)',
      },
    },
  };  
  const handleMyPlanClick = () => {
    // Navigate to the My Plan page or display plan details
    // For now, we'll just log to the console
    console.log('My Plan button clicked');
  };
  const dispatch = useDispatch();
  const user = useSelector((state) => state.user);
  const vpn = useSelector((state) => state.vpn);

  useEffect(() => {
    dispatch(fetchVpnStatus());
    dispatch(fetchUserTraffic());
  }, [dispatch]);

  return (
    <Box
      sx={{
        backgroundColor: '#fafafa',
        minHeight: '100vh',
      }}
    >
      {/* User Profile Section */}
      <Box
        sx={{
          position: 'sticky',
          top: 0,
          backgroundColor: '#fff',
          padding: 2,
          display: 'flex',
          alignItems: 'center',
          borderBottom: '1px solid #e0e0e0',
          zIndex: 1000,
        }}
      >
        <Avatar
          alt={user.name}
          src={user.avatarUrl}
          sx={{ width: 56, height: 56, mr: 2 }}
        />
        <Typography variant="h6">{user.name}</Typography>
      </Box>

      {/* Main Content */}
      <Box
        sx={{
          padding: 2,
          display: 'flex',
          flexDirection: { xs: 'column', md: 'row' },
          justifyContent: 'center',
          alignItems: 'flex-start',
          gap: 2,
          mt: 3,
        }}
      >
        {/* VPN Status */}
        <Card
          sx={{
            flex: 1,
            borderRadius: 4,
            textAlign: 'center',
          }}
        >
          <CardContent
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}
          >
            {vpn.status === 'loading' ? (
              <CircularProgress size={60} />
            ) : vpn.status === 'failed' ? (
              <Typography variant="h6" color="error">
                Error fetching VPN status
              </Typography>
            ) : (
              <Fade in={vpn.status === 'succeeded'} timeout={600}>
                <Box
                  sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                  }}
                >
                  <VpnLockIcon
                    sx={{
                      fontSize: 60,
                      color: vpn.serverStatus === 'Online' ? 'green' : 'red',
                      transition: 'color 0.5s ease',
                      animation:
                        vpn.serverStatus === 'Online' ? 'pulse 2s infinite' : 'none',
                      ...pulseAnimation,
                    }}
                  />
                  <Typography variant="h5" sx={{ mt: 1 }}>
                    {vpn.serverStatus}
                  </Typography>
                </Box>
              </Fade>
            )}
          </CardContent>
        </Card>

        {/* Traffic Left */}
        <Typography variant="h4" color="primary">
          {user.trafficLeft !== null ? `${user.trafficLeft} GB` : 'Loading...'}
        </Typography>
      </Box>

      {/* Buttons */}
      <Box
        sx={{
          padding: 2,
          display: 'flex',
          justifyContent: 'center',
          gap: 2,
          mt: 3,
        }}
      >
        <Button
          variant="contained"
          color="primary"
          sx={{ borderRadius: 2, width: '100%', maxWidth: 200 }}
          onClick={handleAccessKeyClick}
        >
          Get an Individual Access Key
        </Button>
        <Button
          variant="outlined"
          color="primary"
          sx={{ borderRadius: 2, width: '100%', maxWidth: 200 }}
          onClick={handleMyPlanClick}
        >
          My Plan
        </Button>
      </Box>
    </Box>
  );
};

export default MainPage;
