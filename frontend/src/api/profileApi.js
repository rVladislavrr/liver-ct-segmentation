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

export const savePhotoToProfile = async (photoData) => {
  const accessToken = localStorage.getItem('accessToken');
  const response = await axios.post(`${API_URL}/photos/save`, photoData, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
  return response.data;
};

export const deletePhoto = async (photoUuid) => {
  try {
    await axios.delete(`${API_URL}/photos/${photoUuid}/delete`);
    return true;
  } catch (error) {
    console.error('Delete error:', error);
    throw error;
  }
};
