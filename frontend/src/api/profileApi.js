import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

export const fetchUserProfile = async () => {
  const accessToken = localStorage.getItem('accessToken');
  const headers = {};
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }
  const response = await axios.get(`${API_URL}/photos`, { headers: headers });
  return response.data;
};
