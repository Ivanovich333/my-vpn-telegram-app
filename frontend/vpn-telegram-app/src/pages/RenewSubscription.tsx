// src/pages/RenewSubscription.tsx
import React, { useState } from 'react';
import { Box, Typography, Slider, Button } from '@mui/material';

const RenewSubscription: React.FC = () => {
  const [trafficAmount, setTrafficAmount] = useState<number>(50); // Default to 50 GB

  const handleSliderChange = (event: Event, newValue: number | number[]) => {
    setTrafficAmount(newValue as number);
  };

  const handleRenew = () => {
    // TODO: Implement renew logic
  };

  const calculatePrice = (amount: number) => {
    const pricePerGB = 0.5; // Example price per GB
    return (amount * pricePerGB).toFixed(2);
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h5" gutterBottom>
        Extend Subscription
      </Typography>
      <Typography variant="body1">Select the amount of traffic you need:</Typography>
      <Slider
        value={trafficAmount}
        onChange={handleSliderChange}
        aria-labelledby="traffic-slider"
        valueLabelDisplay="on"
        step={10}
        marks
        min={10}
        max={200}
        sx={{ mt: 4 }}
      />
      <Typography variant="body1" sx={{ mt: 2 }}>
        Selected Traffic: <strong>{trafficAmount} GB</strong>
      </Typography>
      <Typography variant="body1" sx={{ mb: 2 }}>
        Total Price: <strong>${calculatePrice(trafficAmount)}</strong>
      </Typography>
      <Button variant="contained" color="primary" onClick={handleRenew} fullWidth>
        Purchase
      </Button>
    </Box>
  );
};

export default RenewSubscription;
