import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  async (error) => {
    const orig = error.config;
    if (error.response?.status === 401 && !orig._retry) {
      orig._retry = true;
      const rt = localStorage.getItem('refresh_token');
      if (rt) {
        try {
          const res = await axios.post('/api/v1/auth/refresh', { refresh_token: rt });
          const { access_token, refresh_token: nrt } = res.data.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', nrt);
          orig.headers.Authorization = `Bearer ${access_token}`;
          return api(orig);
        } catch {
          localStorage.clear();
          window.location.href = '/login';
        }
      } else {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  },
);

export default api;
