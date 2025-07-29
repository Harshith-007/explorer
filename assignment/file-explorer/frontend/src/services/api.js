import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authenticateWithGoogle = async (token) => {
  const response = await api.post('/api/auth/google', { token });
  return response.data;
};

export const authenticateWithMicrosoft = async (token) => {
  const response = await api.post('/api/auth/microsoft', { token });
  return response.data;
};

export const getFileTree = async (path = '') => {
  const response = await api.get('/api/files/tree', { params: { path } });
  return response.data;
};

export const uploadFile = async (file, path = '') => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('path', path);
  
  const response = await api.post('/api/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const downloadFile = async (filePath) => {
  const response = await api.get('/api/files/download', {
    params: { path: filePath },
    responseType: 'blob'
  });
  
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filePath.split('/').pop());
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const deleteFile = async (filePath) => {
  const response = await api.delete('/api/files/delete', {
    data: { path: filePath }
  });
  return response.data;
};

export const createFolder = async (name, path = '') => {
  const formData = new FormData();
  formData.append('name', name);
  formData.append('path', path);
  
  const response = await api.post('/api/files/create-folder', formData);
  return response.data;
};
