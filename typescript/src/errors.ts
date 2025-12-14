export class AlpacaError extends Error {
  statusCode?: number;
  response?: any;

  constructor(message: string, statusCode?: number, response?: any) {
    super(message);
    this.name = 'AlpacaError';
    this.statusCode = statusCode;
    this.response = response;
  }
}

export class AuthenticationError extends AlpacaError {
  constructor(message: string) {
    super(message, 401);
    this.name = 'AuthenticationError';
  }
}

export class RateLimitError extends AlpacaError {
  retryAfter?: number;

  constructor(message: string, retryAfter?: number) {
    super(message, 429);
    this.name = 'RateLimitError';
    this.retryAfter = retryAfter;
  }
}

export class NotFoundError extends AlpacaError {
  constructor(message: string) {
    super(message, 404);
    this.name = 'NotFoundError';
  }
}

export class ValidationError extends AlpacaError {
  constructor(message: string) {
    super(message, 422);
    this.name = 'ValidationError';
  }
}
