// Enums
export enum OrderSide {
  BUY = 'buy',
  SELL = 'sell'
}

export enum OrderType {
  MARKET = 'market',
  LIMIT = 'limit',
  STOP = 'stop',
  STOP_LIMIT = 'stop_limit',
  TRAILING_STOP = 'trailing_stop'
}

export enum TimeInForce {
  DAY = 'day',
  GTC = 'gtc',
  OPG = 'opg',
  CLS = 'cls',
  IOC = 'ioc',
  FOK = 'fok'
}

export enum OrderStatus {
  NEW = 'new',
  PARTIALLY_FILLED = 'partially_filled',
  FILLED = 'filled',
  DONE_FOR_DAY = 'done_for_day',
  CANCELED = 'canceled',
  EXPIRED = 'expired',
  REPLACED = 'replaced',
  PENDING_CANCEL = 'pending_cancel',
  PENDING_REPLACE = 'pending_replace',
  ACCEPTED = 'accepted',
  REJECTED = 'rejected'
}

// Interfaces
export interface Account {
  id: string;
  accountNumber: string;
  status: string;
  currency: string;
  cash: number;
  buyingPower: number;
  portfolioValue: number;
  equity: number;
  lastEquity: number;
  longMarketValue: number;
  shortMarketValue: number;
  initialMargin: number;
  maintenanceMargin: number;
  daytradeCount: number;
  patternDayTrader: boolean;
  tradingBlocked: boolean;
  transfersBlocked: boolean;
  accountBlocked: boolean;
  createdAt: Date;
}

export interface Order {
  id: string;
  clientOrderId: string;
  createdAt: Date;
  submittedAt?: Date;
  filledAt?: Date;
  expiredAt?: Date;
  canceledAt?: Date;
  assetId: string;
  symbol: string;
  assetClass: string;
  qty?: number;
  filledQty: number;
  filledAvgPrice?: number;
  orderType: string;
  type: string;
  side: string;
  timeInForce: string;
  limitPrice?: number;
  stopPrice?: number;
  status: string;
  extendedHours: boolean;
}

export interface Position {
  assetId: string;
  symbol: string;
  exchange: string;
  assetClass: string;
  avgEntryPrice: number;
  qty: number;
  side: string;
  marketValue: number;
  costBasis: number;
  unrealizedPl: number;
  unrealizedPlpc: number;
  currentPrice: number;
  lastdayPrice: number;
  changeToday: number;
}

export interface Bar {
  timestamp: Date;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  tradeCount?: number;
  vwap?: number;
}

export interface Trade {
  timestamp: Date;
  price: number;
  size: number;
  exchange?: string;
  id?: number;
  conditions?: string[];
}

export interface Quote {
  timestamp: Date;
  askPrice: number;
  askSize: number;
  bidPrice: number;
  bidSize: number;
  askExchange?: string;
  bidExchange?: string;
}

export interface Clock {
  timestamp: Date;
  isOpen: boolean;
  nextOpen: Date;
  nextClose: Date;
}

export interface Watchlist {
  id: string;
  accountId: string;
  name: string;
  createdAt: Date;
  updatedAt: Date;
  assets?: Asset[];
}

export interface Asset {
  id: string;
  class: string;
  exchange: string;
  symbol: string;
  name: string;
  status: string;
  tradable: boolean;
  marginable: boolean;
  shortable: boolean;
  easyToBorrow: boolean;
  fractionable: boolean;
}
