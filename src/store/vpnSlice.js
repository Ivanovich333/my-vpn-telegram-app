import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { getVpnStatus } from '../api/vpnService';

export const fetchVpnStatus = createAsyncThunk('vpn/fetchStatus', async () => {
  const response = await getVpnStatus();
  return response.data;
});

const vpnSlice = createSlice({
  name: 'vpn',
  initialState: {
    status: 'idle',
    serverStatus: '',
    error: null,
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchVpnStatus.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchVpnStatus.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.serverStatus = action.payload.status;
      })
      .addCase(fetchVpnStatus.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message;
        state.serverStatus = null; // Ensure serverStatus is null on error
      });
      
  },
  
});

export default vpnSlice.reducer;
