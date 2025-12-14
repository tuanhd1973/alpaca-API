import { AlpacaClient } from './client';
import { Bar, Trade, Quote } from './types';

export class MarketDataAPI {
  private baseURL = AlpacaClient.MARKET_DATA;

  constructor(private client: AlpacaClient) {}

  // Stock Bars
  async getStockBars(
    symbols: string | string[],
    timeframe: string = '1Day',
    params?: { start?: string; end?: string; limit?: number }
  ): Promise<{ bars: Record<string, Bar[]>; nextPageToken?: string }> {
    const symbolList = Array.isArray(symbols) ? symbols : [symbols];
    const data = await this.client.get<any>('/v2/stocks/bars', {
      symbols: symbolList.join(','),
      timeframe,
      ...params,
    }, this.baseURL);

    const bars: Record<string, Bar[]> = {};
    for (const [symbol, barList] of Object.entries(data.bars || {})) {
      bars[symbol] = (barList as any[]).map(b => this.parseBar(b));
    }
    return { bars, nextPageToken: data.next_page_token };
  }

  // Stock Trades
  async getStockTrades(
    symbols: string | string[],
    params?: { start?: string; end?: string; limit?: number }
  ): Promise<{ trades: Record<string, Trade[]>; nextPageToken?: string }> {
    const symbolList = Array.isArray(symbols) ? symbols : [symbols];
    const data = await this.client.get<any>('/v2/stocks/trades', {
      symbols: symbolList.join(','),
      ...params,
    }, this.baseURL);

    const trades: Record<string, Trade[]> = {};
    for (const [symbol, tradeList] of Object.entries(data.trades || {})) {
      trades[symbol] = (tradeList as any[]).map(t => this.parseTrade(t));
    }
    return { trades, nextPageToken: data.next_page_token };
  }

  // Stock Quotes
  async getStockQuotes(
    symbols: string | string[],
    params?: { start?: string; end?: string; limit?: number }
  ): Promise<{ quotes: Record<string, Quote[]>; nextPageToken?: string }> {
    const symbolList = Array.isArray(symbols) ? symbols : [symbols];
    const data = await this.client.get<any>('/v2/stocks/quotes', {
      symbols: symbolList.join(','),
      ...params,
    }, this.baseURL);

    const quotes: Record<string, Quote[]> = {};
    for (const [symbol, quoteList] of Object.entries(data.quotes || {})) {
      quotes[symbol] = (quoteList as any[]).map(q => this.parseQuote(q));
    }
    return { quotes, nextPageToken: data.next_page_token };
  }

  // Stock Snapshots
  async getStockSnapshots(symbols: string | string[]): Promise<Record<string, any>> {
    const symbolList = Array.isArray(symbols) ? symbols : [symbols];
    return this.client.get('/v2/stocks/snapshots', {
      symbols: symbolList.join(','),
    }, this.baseURL);
  }

  async getStockSnapshot(symbol: string): Promise<any> {
    return this.client.get(`/v2/stocks/${symbol.toUpperCase()}/snapshot`, {}, this.baseURL);
  }

  async getCurrentPrice(symbol: string): Promise<number> {
    const snapshot = await this.getStockSnapshot(symbol);
    return snapshot.latestTrade?.p || 0;
  }

  // Crypto
  async getCryptoBars(
    symbols: string | string[],
    timeframe: string = '1Day',
    params?: { start?: string; end?: string; limit?: number }
  ): Promise<{ bars: Record<string, Bar[]>; nextPageToken?: string }> {
    const symbolList = Array.isArray(symbols) ? symbols : [symbols];
    const data = await this.client.get<any>('/v1beta3/crypto/us/bars', {
      symbols: symbolList.join(','),
      timeframe,
      ...params,
    }, this.baseURL);

    const bars: Record<string, Bar[]> = {};
    for (const [symbol, barList] of Object.entries(data.bars || {})) {
      bars[symbol] = (barList as any[]).map(b => this.parseBar(b));
    }
    return { bars, nextPageToken: data.next_page_token };
  }

  async getCryptoSnapshots(symbols: string | string[]): Promise<Record<string, any>> {
    const symbolList = Array.isArray(symbols) ? symbols : [symbols];
    const data = await this.client.get<any>('/v1beta3/crypto/us/snapshots', {
      symbols: symbolList.join(','),
    }, this.baseURL);
    return data.snapshots || {};
  }

  // Options
  async getOptionsContracts(params: {
    underlyingSymbols?: string[];
    type?: 'call' | 'put';
    expirationDateGte?: string;
    expirationDateLte?: string;
    strikePriceGte?: number;
    strikePriceLte?: number;
    limit?: number;
  }): Promise<any> {
    return this.client.get('/v2/options/contracts', {
      underlying_symbols: params.underlyingSymbols?.join(','),
      type: params.type,
      expiration_date_gte: params.expirationDateGte,
      expiration_date_lte: params.expirationDateLte,
      strike_price_gte: params.strikePriceGte,
      strike_price_lte: params.strikePriceLte,
      limit: params.limit,
    });
  }

  // Meta
  async getExchanges(): Promise<Record<string, string>> {
    return this.client.get('/v2/stocks/meta/exchanges', {}, this.baseURL);
  }

  // Parsers
  private parseBar(data: any): Bar {
    return {
      timestamp: new Date(data.t),
      open: data.o,
      high: data.h,
      low: data.l,
      close: data.c,
      volume: data.v,
      tradeCount: data.n,
      vwap: data.vw,
    };
  }

  private parseTrade(data: any): Trade {
    return {
      timestamp: new Date(data.t),
      price: data.p,
      size: data.s,
      exchange: data.x,
      id: data.i,
      conditions: data.c,
    };
  }

  private parseQuote(data: any): Quote {
    return {
      timestamp: new Date(data.t),
      askPrice: data.ap,
      askSize: data.as,
      bidPrice: data.bp,
      bidSize: data.bs,
      askExchange: data.ax,
      bidExchange: data.bx,
    };
  }
}
