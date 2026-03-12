import axios, { AxiosInstance } from "axios";

export interface ApiConfig {
  baseUrl?: string;
  initData: string;
  devTelegramId?: string;
}

export const createApiClient = ({ baseUrl, initData, devTelegramId }: ApiConfig): AxiosInstance => {
  const instance = axios.create({
    baseURL: baseUrl ?? import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1"
  });

  instance.interceptors.request.use((config) => {
    config.headers = config.headers ?? {};
    if (initData) {
      config.headers["X-Telegram-Init-Data"] = initData;
    }
    if (!initData && devTelegramId) {
      config.headers["X-Dev-Telegram-Id"] = devTelegramId;
    }
    return config;
  });

  return instance;
};

