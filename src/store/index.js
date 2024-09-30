import { configureStore } from '@reduxjs/toolkit';
import userReducer from './userSlice';
import vpnReducer from './vpnSlice';

const store = configureStore({
  reducer: {
    user: userReducer,
    vpn: vpnReducer,
  },
});

export default store;
