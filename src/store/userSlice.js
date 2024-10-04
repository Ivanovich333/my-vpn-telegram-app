import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { getUserTraffic, generateAccessKey } from '../api/vpnService';
import { initDataUnsafe } from '@twa-dev/sdk';

const user = (initDataUnsafe && initDataUnsafe.user) || {};

export const fetchUserTraffic = createAsyncThunk('user/fetchTraffic', async () => {
    const response = await getUserTraffic(user.id);
    return response.data;
  });
  
  export const generateUserAccessKey = createAsyncThunk('user/generateAccessKey', async () => {
    const response = await generateAccessKey(user.id);
    return response.data;
  });
  
  const userSlice = createSlice({
    name: 'user',
    initialState: {
      id: user.id,
      name: `${user.first_name || 'User'} ${user.last_name || ''}`.trim(),
      avatarUrl: user.photo_url || '',
      trafficLeft: null,
      accessKey: null,
      status: 'idle',
      error: null,
    },
    reducers: {},
    extraReducers: (builder) => {
      builder
        .addCase(fetchUserTraffic.fulfilled, (state, action) => {
          state.trafficLeft = action.payload.trafficLeft;
        })
        .addCase(generateUserAccessKey.fulfilled, (state, action) => {
          state.accessKey = action.payload.accessKey;
        });
    },
  });
  
  export default userSlice.reducer;