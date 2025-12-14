import axios, { AxiosInstance, AxiosError } from 'axios';
import { AlpacaError, AuthenticationError, RateLimitError, NotFoundError, ValidationError } from './errors';

export interface AlpacaClientOptions {
  apiKey: string;
  apiSecret: string;
  paper?: boolean;
  timeout?: number;
}

export class AlpacaClient {
  private client: AxiosInstance;
  private apiKey: string;
  private apiSecret: string;
  paper: boolean;

  static readonly TRADING_LIVE = 'https://api.alpaca.markets';
  static readonly TRADING_PAPER = 'https://paper-api.alpaca.markets';
  static readonly MARKET_DATA = 'https://data.alpaca.markets';

  constructor(options: AlpacaClientOptions) {
    this.apiKey = options.apiKey;
    this.apiSecret = options.apiSecret;
    this.paper = options.paper ?? true;

    const baseURL = this.paper ? AlpacaClient.TRADING_PAPER : AlpacaClient.TRADING_LIVE;

    this.client = axios.create({
      baseURL,
      timeout: options.timeout ?? 30000,
      headers: {
        'APCA-API-KEY-ID': this.apiKey,
        'APCA-API-SECRET-KEY': this.apiSecret,
        'Content-Type': 'application/json',
      },
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => this.handleError(error)
    );
  }

  private handleError(error: AxiosError): never {
    const status = error.response?.status;
    const data = error.response?.data as any;
    const message = data?.message || error.message;

    switch (status) {
      case 401:
        throw new AuthenticationError(message);
      case 404:
        throw new NotFoundError(message);
      case 422:
        throw new ValidationError(message);
      case 429:
        const retryAfter = error.response?.headers['retry-after'];
        throw new RateLimitError(message, retryAfter ? parseInt(retryAfter) : undefined);
      default:
        throw new AlpacaError(message, status, data);
    }
  }

  async get<T>(endpoint: string, params?: any, baseURL?: string): Promise<T> {
    const response = await this.client.get<T>(endpoint, { 
      params,
      baseURL: baseURL || this.client.defaults.baseURL 
    });
    return response.data;
  }

  async post<T>(endpoint: string, data?: any, baseURL?: string): Promise<T> {
    const response = await this.client.post<T>(endpoint, data, {
      baseURL: baseURL || this.client.defaults.baseURL
    });
    return response.data;
  }

  async patch<T>(endpoint: string, data?: any): Promise<T> {
    const response = await this.client.patch<T>(endpoint, data);
    return response.data;
  }

  async delete<T>(endpoint: string, params?: any): Promise<T> {
    const response = await this.client.delete<T>(endpoint, { params });
    return response.data;
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    const response = await this.client.put<T>(endpoint, data);
    return response.data;
  }
}
