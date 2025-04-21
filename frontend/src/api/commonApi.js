import axios from 'axios';
import { toast } from 'react-toastify';

const API_URL = process.env.REACT_APP_API_URL;

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

let authInterceptorId = null;

export const uploadFile = async (file) => {
  const accessToken = localStorage.getItem('accessToken');
  const headers = {};
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }
  const formData = new FormData();
  formData.append('file', file);
  try {
    const response = await axios.post(`${API_URL}/upload`, formData, { headers: headers });
    toast.success('Файл успешно загружен!');
    return response.data;
  } catch (error) {
    console.error('error', error);
    const errorMessage = error.response?.data?.detail.msg + `\n(${error.response?.data?.detail?.request_id})` || 'Ошибка при загрузке';
    toast.error(errorMessage);
    throw error;
  }
};

export const sendPhotoId = async (uuid_file, num_images) => {
  const accessToken = localStorage.getItem('accessToken');
  const headers = {
    'Content-Type': 'application/json',
  };
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }
  try {
    const response = await axios.post(
      `${API_URL}/predict`,
      {
        uuid_file,
        num_images,
      },
      {
        headers: headers,
        responseType: 'blob',
      }
    );
    return response.data;
  } catch (error) {
    console.error('error while sending id', error);
    throw error;
  }
};

export const login = async (email, password) => {
  try {
    const response = await axios.post(
      `${API_URL}/auth/login`,
      { email, password },
      {
        _skipAuth: true,
      }
    );
    const { accessToken } = response.data;
    console.log(accessToken);
    localStorage.setItem('accessToken', accessToken);
    setupAuthInterceptor(accessToken);
    toast.success('Вход выполнен!');
    return { success: true, data: response.data };
  } catch (error) {
    const errorMessage = error.response?.data?.detail.msg + `\n(${error.response?.data?.detail?.request_id})` || error.message || 'Ошибка при попытке входа';
    toast.error(errorMessage);
  }
};

export const register = async (name, email, password) => {
  try {
    const response = await axios.post(
      `${API_URL}/auth/registration`,
      { name, email, password },
      {
        _skipAuth: true,
      }
    );

    if (response.data.access) {
      const { accessToken } = response.data;
      localStorage.setItem('accessToken', accessToken);
      setupAuthInterceptor(accessToken);
      toast.success('Вы успешно зарегистрировались!');
    }

    return { success: true, data: response.data };
  } catch (error) {
    const errorMessage = error.response?.data?.detail.msg + `\n(${error.response?.data?.detail?.request_id})` || error.message || 'Ошибка при регистрации';
    toast.error(errorMessage);
  }
};

axios.interceptors.request.use((config) => {
  if (config._skipAuth) {
    delete config._skipAuth;
    return config;
  }
  return config;
});

export const refreshToken = async () => {
  try {
    const response = await axios.post(
      `${API_URL}/auth/refresh`,
      {},
      {
        withCredentials: true,
      }
    );

    const { accessToken } = response.data;
    localStorage.setItem('accessToken', accessToken);
    return accessToken;
  } catch (error) {
    console.error('Refresh token error:', error);
    throw error;
  }
};

export const logout = async (preventRedirect = false) => {
  try {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    delete axios.defaults.headers.common['Authorization'];

    await axios
      .post(
        `${API_URL}/auth/logout`,
        {},
        {
          withCredentials: true,
          timeout: 3000,
        }
      )
      .catch((e) => console.log('Logout cleanup error:', e));
  } finally {
    localStorage.removeItem('accessToken');
    clearAuthInterceptor();
    delete api.defaults.headers.common.Authorization;
    if (!preventRedirect) window.location.href = '/';
  }
};

const setupAuthInterceptor = (token) => {
  if (authInterceptorId !== null) {
    api.interceptors.response.eject(authInterceptorId);
  }

  authInterceptorId = api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      if (originalRequest.url.includes('/auth/')) {
        return Promise.reject(error);
      }

      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          const newToken = await refreshToken();
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return api(originalRequest);
        } catch (refreshError) {
          await logout(true);
          return Promise.reject(refreshError);
        }
      }

      return Promise.reject(error);
    }
  );

  api.defaults.headers.common.Authorization = `Bearer ${token}`;
};

const clearAuthInterceptor = () => {
  if (authInterceptorId !== null) {
    api.interceptors.response.eject(authInterceptorId);
    authInterceptorId = null;
  }
};

export default axios;
