import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/', // Base URL is the same as the app's origin
});

export const getVpnStatus = () => apiClient.get('/.netlify/functions/getServerStatus');
// For Vercel, use '/api/getServerStatus' instead
export const getUserTraffic = (userId) => apiClient.get(`/users/${userId}/traffic`);
export const getUserPlan = (userId) => apiClient.get(`/users/${userId}/plan`);
export const generateAccessKey = (userId) => apiClient.post(`/users/${userId}/access-key`);
