import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

export const getProductData = async (id: number) => {
  const response = await axios.get(`${API_BASE_URL}/get_product_data`, {
    params: { id },
  });
  return response.data;
};

export const getProductImage = async (id: number) => {
  const response = await axios.get(`${API_BASE_URL}/get_product_image`, {
    params: { id },
  });
  return response.data;
};