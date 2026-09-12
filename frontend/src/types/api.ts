export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  database: string;
  redis: string;
  version: string;
  providers: {
    ai: string;
    weather: string;
    ocr: string;
    storage: string;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ErrorResponse {
  detail: string;
  error_code?: string;
}

export interface SuccessResponse<T = unknown> {
  message: string;
  data?: T;
}
