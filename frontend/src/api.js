import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

let authInterceptorId = null;

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

export const login = async (email, password) => {
  try {
    const response = await axios.post(
      `${API_URL}/auth/login/`,
      { email, password },
      {
        _skipAuth: true,
      }
    );
    const { access } = response.data;
    localStorage.setItem('accessToken', access);
    setupAuthInterceptor(access);
    return { success: true, data: response.data };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.detail || error.response?.data?.message || 'Ошибка сервера. Попробуйте позже.',
    };
  }
};

axios.interceptors.request.use(config => {
  if (config._skipAuth) {
    delete config._skipAuth;
    return config;
  }
  return config;
});

export const refreshToken = async () => {
  try {
    const response = await axios.post(
      `${API_URL}/auth/refresh/`,
      {},
      {
        withCredentials: true,
      }
    );

    const { access } = response.data;
    localStorage.setItem('accessToken', access);
    return access;
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
        `${API_URL}/auth/logout/`,
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
    if (!preventRedirect) window.location.href = '/login';
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
