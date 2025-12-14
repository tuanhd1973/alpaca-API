import WebSocket from 'ws';

export enum StreamType {
  IEX = 'wss://stream.data.alpaca.markets/v2/iex',
  SIP = 'wss://stream.data.alpaca.markets/v2/sip',
  CRYPTO = 'wss://stream.data.alpaca.markets/v1beta3/crypto/us',
}

export interface StreamConfig {
  autoReconnect?: boolean;
  reconnectDelay?: number;
  maxReconnectAttempts?: number;
}

type EventHandler = (data: any) => void | Promise<void>;

export class AlpacaStream {
  private ws?: WebSocket;
  private handlers: Map<string, EventHandler[]> = new Map();
  private connected = false;
  private authenticated = false;

  constructor(
    private apiKey: string,
    private apiSecret: string,
    private streamType: StreamType = StreamType.IEX,
    private config: StreamConfig = {}
  ) {
    this.config = {
      autoReconnect: true,
      reconnectDelay: 1000,
      maxReconnectAttempts: 10,
      ...config,
    };
  }

  // Event handlers
  onTrade(handler: EventHandler): this {
    return this.on('t', handler);
  }

  onQuote(handler: EventHandler): this {
    return this.on('q', handler);
  }

  onBar(handler: EventHandler): this {
    return this.on('b', handler);
  }

  on(event: string, handler: EventHandler): this {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, []);
    }
    this.handlers.get(event)!.push(handler);
    return this;
  }

  private emit(event: string, data: any): void {
    const handlers = this.handlers.get(event) || [];
    handlers.forEach(handler => handler(data));
  }

  async connect(): Promise<boolean> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.streamType);

      this.ws.on('open', () => {
        this.connected = true;
        console.log('Connected to', this.streamType);
      });

      this.ws.on('message', async (data: WebSocket.Data) => {
        const messages = JSON.parse(data.toString());
        
        for (const msg of Array.isArray(messages) ? messages : [messages]) {
          if (msg.T === 'success' && msg.msg === 'connected') {
            // Send auth
            this.ws!.send(JSON.stringify({
              action: 'auth',
              key: this.apiKey,
              secret: this.apiSecret,
            }));
          } else if (msg.T === 'success' && msg.msg === 'authenticated') {
            this.authenticated = true;
            this.emit('connected', {});
            resolve(true);
          } else if (msg.T === 'error') {
            this.emit('error', msg);
            reject(new Error(msg.msg));
          } else if (msg.T) {
            this.emit(msg.T, msg);
          }
        }
      });

      this.ws.on('error', (error) => {
        this.emit('error', error);
        reject(error);
      });

      this.ws.on('close', () => {
        this.connected = false;
        this.authenticated = false;
        this.emit('disconnected', {});
      });
    });
  }

  async subscribe(params: {
    trades?: string[];
    quotes?: string[];
    bars?: string[];
  }): Promise<void> {
    if (!this.ws || !this.authenticated) {
      throw new Error('Not connected');
    }

    const msg: any = { action: 'subscribe' };
    if (params.trades) msg.trades = params.trades;
    if (params.quotes) msg.quotes = params.quotes;
    if (params.bars) msg.bars = params.bars;

    this.ws.send(JSON.stringify(msg));
  }

  async unsubscribe(params: {
    trades?: string[];
    quotes?: string[];
    bars?: string[];
  }): Promise<void> {
    if (!this.ws) return;

    const msg: any = { action: 'unsubscribe' };
    if (params.trades) msg.trades = params.trades;
    if (params.quotes) msg.quotes = params.quotes;
    if (params.bars) msg.bars = params.bars;

    this.ws.send(JSON.stringify(msg));
  }

  close(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = undefined;
    }
  }

  get isConnected(): boolean {
    return this.connected && this.authenticated;
  }
}
