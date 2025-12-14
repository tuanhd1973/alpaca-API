import 'dotenv/config';
import { AlpacaClient, TradingAPI, MarketDataAPI } from '../src';

const API_KEY = process.env.ALPACA_API_KEY!;
const API_SECRET = process.env.ALPACA_API_SECRET!;

async function main() {
  // Initialize
  const client = new AlpacaClient({
    apiKey: API_KEY,
    apiSecret: API_SECRET,
    paper: true,
  });

  const trading = new TradingAPI(client);
  const marketData = new MarketDataAPI(client);

  // Account
  const account = await trading.getAccount();
  console.log(`Buying Power: $${account.buyingPower.toLocaleString()}`);

  // Market status
  const clock = await trading.getClock();
  console.log(`Market Open: ${clock.isOpen}`);

  // Current price
  const price = await marketData.getCurrentPrice('AAPL');
  console.log(`AAPL: $${price}`);

  // Get bars
  const { bars } = await marketData.getStockBars(['AAPL'], '1Day', { limit: 5 });
  console.log(`AAPL Bars: ${bars['AAPL']?.length || 0}`);

  // Positions
  const positions = await trading.getPositions();
  console.log(`Positions: ${positions.length}`);

  console.log('Done!');
}

main().catch(console.error);
