import axios from 'axios';

// Create an axios instance
const apiClient = axios.create({
  baseURL: 'https://your-vpn-service-api.com', // Replace with your API base URL
  timeout: 10000, // Optional timeout
});

// API endpoints
export const getVpnStatus = () => apiClient.get('/vpn/status');
export const getUserTraffic = (userId) => apiClient.get(`/users/${userId}/traffic`);
export const getUserPlan = (userId) => apiClient.get(`/users/${userId}/plan`);
export const generateAccessKey = (userId) => apiClient.post(`/users/${userId}/access-key`);
