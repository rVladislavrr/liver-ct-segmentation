import axios from 'axios';
import { toast } from 'react-toastify';

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
  try {
    const accessToken = localStorage.getItem('accessToken');
    const response = await axios.post(`${API_URL}/photos/save`, photoData, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
    toast.success('Фотография успешно сохранена!');
    return response.data;
  } catch (error) {
    const errorMessage = error.response?.data?.detail.msg + `\n(${error.response?.data?.detail.request_id})` || error.message || 'Не удалось сохранить фотографию';
    toast.error(errorMessage);
  }
};

export const deletePhoto = async (photoUuid) => {
  const accessToken = localStorage.getItem('accessToken');
  try {
    await axios.delete(`${API_URL}/photos/${photoUuid}/delete`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
    toast.success('Фотография успешно удалена!');
    return true;
  } catch (error) {
    console.error('Delete error:', error);
    const errorMessage = error.response?.data?.detail.msg + `\n(${error.response?.data?.detail?.request_id})` || error.message || 'Не удалось удалить фотографию';
    toast.error(errorMessage);
    throw error;
  }
};

export const deleteContour = async (photoUuid) => {
  const accessToken = localStorage.getItem('accessToken');
  try {
    await axios.delete(`${API_URL}/contours/${photoUuid}/delete`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
    toast.success('Фотография успешно удалена!');
    return true;
  } catch (error) {
    console.error('Delete error:', error);
    const errorMessage = error.response?.data?.detail.msg + `\n(${error.response?.data?.detail?.request_id})` || error.message || 'Не удалось удалить фотографию';
    toast.error(errorMessage);
    throw error;
  }
};
