import { AlpacaClient } from './client';
import { Account, Order, Position, Clock, Watchlist, Asset, OrderSide, OrderType, TimeInForce } from './types';

export class TradingAPI {
  constructor(private client: AlpacaClient) {}

  // Account
  async getAccount(): Promise<Account> {
    const data = await this.client.get<any>('/v2/account');
    return this.parseAccount(data);
  }

  async getAccountConfigurations(): Promise<any> {
    return this.client.get('/v2/account/configurations');
  }

  async getBuyingPower(): Promise<number> {
    const account = await this.getAccount();
    return account.buyingPower;
  }

  // Orders
  async createOrder(params: {
    symbol: string;
    qty?: number;
    notional?: number;
    side: OrderSide | string;
    type?: OrderType | string;
    timeInForce?: TimeInForce | string;
    limitPrice?: number;
    stopPrice?: number;
    extendedHours?: boolean;
  }): Promise<Order> {
    const data = await this.client.post<any>('/v2/orders', {
      symbol: params.symbol.toUpperCase(),
      qty: params.qty?.toString(),
      notional: params.notional?.toString(),
      side: params.side,
      type: params.type || 'market',
      time_in_force: params.timeInForce || 'day',
      limit_price: params.limitPrice?.toString(),
      stop_price: params.stopPrice?.toString(),
      extended_hours: params.extendedHours,
    });
    return this.parseOrder(data);
  }

  async buy(symbol: string, qty: number): Promise<Order> {
    return this.createOrder({ symbol, qty, side: OrderSide.BUY });
  }

  async sell(symbol: string, qty: number): Promise<Order> {
    return this.createOrder({ symbol, qty, side: OrderSide.SELL });
  }

  async buyLimit(symbol: string, qty: number, limitPrice: number): Promise<Order> {
    return this.createOrder({ 
      symbol, qty, 
      side: OrderSide.BUY, 
      type: OrderType.LIMIT, 
      limitPrice,
      timeInForce: TimeInForce.GTC 
    });
  }

  async getOrders(params?: { status?: string; limit?: number }): Promise<Order[]> {
    const data = await this.client.get<any[]>('/v2/orders', params);
    return data.map(o => this.parseOrder(o));
  }

  async getOrder(orderId: string): Promise<Order> {
    const data = await this.client.get<any>(`/v2/orders/${orderId}`);
    return this.parseOrder(data);
  }

  async cancelOrder(orderId: string): Promise<void> {
    await this.client.delete(`/v2/orders/${orderId}`);
  }

  async cancelAllOrders(): Promise<void> {
    await this.client.delete('/v2/orders');
  }

  // Positions
  async getPositions(): Promise<Position[]> {
    const data = await this.client.get<any[]>('/v2/positions');
    return data.map(p => this.parsePosition(p));
  }

  async getPosition(symbol: string): Promise<Position> {
    const data = await this.client.get<any>(`/v2/positions/${symbol.toUpperCase()}`);
    return this.parsePosition(data);
  }

  async closePosition(symbol: string, params?: { qty?: number; percentage?: number }): Promise<Order> {
    const data = await this.client.delete<any>(`/v2/positions/${symbol.toUpperCase()}`, params);
    return this.parseOrder(data);
  }

  async closeAllPositions(): Promise<void> {
    await this.client.delete('/v2/positions');
  }

  // Clock & Calendar
  async getClock(): Promise<Clock> {
    const data = await this.client.get<any>('/v2/clock');
    return {
      timestamp: new Date(data.timestamp),
      isOpen: data.is_open,
      nextOpen: new Date(data.next_open),
      nextClose: new Date(data.next_close),
    };
  }

  async isMarketOpen(): Promise<boolean> {
    const clock = await this.getClock();
    return clock.isOpen;
  }

  // Watchlists
  async createWatchlist(name: string, symbols?: string[]): Promise<Watchlist> {
    const data = await this.client.post<any>('/v2/watchlists', { name, symbols });
    return this.parseWatchlist(data);
  }

  async getWatchlists(): Promise<Watchlist[]> {
    const data = await this.client.get<any[]>('/v2/watchlists');
    return data.map(w => this.parseWatchlist(w));
  }

  async deleteWatchlist(watchlistId: string): Promise<void> {
    await this.client.delete(`/v2/watchlists/${watchlistId}`);
  }

  // Assets
  async getAssets(params?: { status?: string; assetClass?: string }): Promise<Asset[]> {
    return this.client.get('/v2/assets', params);
  }

  async getAsset(symbol: string): Promise<Asset> {
    return this.client.get(`/v2/assets/${symbol.toUpperCase()}`);
  }

  // Parsers
  private parseAccount(data: any): Account {
    return {
      id: data.id,
      accountNumber: data.account_number,
      status: data.status,
      currency: data.currency,
      cash: parseFloat(data.cash),
      buyingPower: parseFloat(data.buying_power),
      portfolioValue: parseFloat(data.portfolio_value),
      equity: parseFloat(data.equity),
      lastEquity: parseFloat(data.last_equity),
      longMarketValue: parseFloat(data.long_market_value),
      shortMarketValue: parseFloat(data.short_market_value),
      initialMargin: parseFloat(data.initial_margin),
      maintenanceMargin: parseFloat(data.maintenance_margin),
      daytradeCount: data.daytrade_count,
      patternDayTrader: data.pattern_day_trader,
      tradingBlocked: data.trading_blocked,
      transfersBlocked: data.transfers_blocked,
      accountBlocked: data.account_blocked,
      createdAt: new Date(data.created_at),
    };
  }

  private parseOrder(data: any): Order {
    return {
      id: data.id,
      clientOrderId: data.client_order_id,
      createdAt: new Date(data.created_at),
      submittedAt: data.submitted_at ? new Date(data.submitted_at) : undefined,
      filledAt: data.filled_at ? new Date(data.filled_at) : undefined,
      assetId: data.asset_id,
      symbol: data.symbol,
      assetClass: data.asset_class,
      qty: data.qty ? parseFloat(data.qty) : undefined,
      filledQty: parseFloat(data.filled_qty || '0'),
      filledAvgPrice: data.filled_avg_price ? parseFloat(data.filled_avg_price) : undefined,
      orderType: data.order_type || data.type,
      type: data.type,
      side: data.side,
      timeInForce: data.time_in_force,
      limitPrice: data.limit_price ? parseFloat(data.limit_price) : undefined,
      stopPrice: data.stop_price ? parseFloat(data.stop_price) : undefined,
      status: data.status,
      extendedHours: data.extended_hours,
    };
  }

  private parsePosition(data: any): Position {
    return {
      assetId: data.asset_id,
      symbol: data.symbol,
      exchange: data.exchange,
      assetClass: data.asset_class,
      avgEntryPrice: parseFloat(data.avg_entry_price),
      qty: parseFloat(data.qty),
      side: data.side,
      marketValue: parseFloat(data.market_value),
      costBasis: parseFloat(data.cost_basis),
      unrealizedPl: parseFloat(data.unrealized_pl),
      unrealizedPlpc: parseFloat(data.unrealized_plpc),
      currentPrice: parseFloat(data.current_price),
      lastdayPrice: parseFloat(data.lastday_price),
      changeToday: parseFloat(data.change_today),
    };
  }

  private parseWatchlist(data: any): Watchlist {
    return {
      id: data.id,
      accountId: data.account_id,
      name: data.name,
      createdAt: new Date(data.created_at),
      updatedAt: new Date(data.updated_at),
      assets: data.assets,
    };
  }
}
