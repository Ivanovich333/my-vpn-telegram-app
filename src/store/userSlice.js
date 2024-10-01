import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { getUserTraffic, generateAccessKey } from '../api/vpnService';

const initialState = {
  id: null,
  firstName: '',
  lastName: '',
  username: '',
  photoUrl: '',
  trafficLeft: null,
  accessKey: null,
  isAuthenticated: false,
  status: 'idle',
  error: null,
};

const userSlice = createSlice({
  name: 'user',
  initialState,
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
      Object.assign(state, initialState);
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUserTraffic.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchUserTraffic.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.trafficLeft = action.payload.trafficLeft;
      })
      .addCase(fetchUserTraffic.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message;
      })
      .addCase(generateUserAccessKey.fulfilled, (state, action) => {
        state.accessKey = action.payload.accessKey;
      });
  },
});

export const { setUserProfile, logout } = userSlice.actions;
export default userSlice.reducer;
export const fetchUserTraffic = createAsyncThunk(
  'user/fetchTraffic',
  async (_, { getState }) => {
    const userId = getState().user.id;
    const response = await getUserTraffic(userId);
    return response.data;
  }
);

export const generateUserAccessKey = createAsyncThunk(
  'user/generateAccessKey',
  async (_, { getState }) => {
    const userId = getState().user.id;
    const response = await generateAccessKey(userId);
    return response.data;
  }
);