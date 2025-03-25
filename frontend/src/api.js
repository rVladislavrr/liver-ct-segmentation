import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  try {
    const response = await axios.post(`${API_URL}/upload/`, formData, {});
    return response.data;
  } catch (error) {
    console.error('error', error);
    throw error;
  }
};

export const sendPhotoId = async (uuid_file, num_images) => {
  try {
    const response = await axios.post(
      `${API_URL}/predict/`,
      {
        uuid_file,
        num_images,
      },
      {
        headers: {
          'Content-Type': 'application/json',
        },
        responseType: 'blob',
      }
    );
    return response.data;
  } catch (error) {
    console.error('error while sending id', error);
    throw error;
  }

};

export default axios;
