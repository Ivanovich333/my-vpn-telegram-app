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

  const initialState = {
    id: null,
    firstName: '',
    lastName: '',
    username: '',
    photoUrl: '',
    isAuthenticated: false,
  };
  
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
    reducers: {
      setUserProfile(state, action) {
        const { id, firstName, lastName, username, photoUrl } = action.payload;
        state.id = id;
        state.firstName = firstName;
        state.lastName = lastName;
        state.username = username;
        state.photoUrl = photoUrl;
        state.isAuthenticated = true;
      },
      logout(state) {
        state.id = null;
        state.firstName = '';
        state.lastName = '';
        state.username = '';
        state.photoUrl = '';
        state.isAuthenticated = false;
      },
    },
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
  
  export const { setUserProfile, logout } = userSlice.actions;
  export default userSlice.reducer;