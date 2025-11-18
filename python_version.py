from enum import Enum

class Side(Enum):
    BUY = 0
    SELL = 1

class Ticker(Enum):
    ETH = 0
    BTC = 1
    LTC = 2

def place_market_order(side: Side, ticker: Ticker, quantity: float) -> bool:
    """Place a market order - DO NOT MODIFY

    Parameters
    ----------
    side
        Side of order to place (Side.BUY or Side.SELL)
    ticker
        Ticker of order to place (Ticker.ETH, Ticker.BTC, or "LTC")
    quantity
        Volume of order to place
    """
    return True

def place_limit_order(side: Side, ticker: Ticker, quantity: float, price: float, ioc: bool = False) -> int:
    """Place a limit order - DO NOT MODIFY

    Parameters
    ----------
    side
        Side of order to place (Side.BUY or Side.SELL)
    ticker
        Ticker of order to place (Ticker.ETH, Ticker.BTC, or "LTC")
    quantity
        Volume of order to place
    price
        Price of order to place

    Returns
    -------
    order_id
    """
    return 0

def cancel_order(ticker: Ticker, order_id: int) -> bool:
    """Place a limit order - DO NOT MODIFY
    Parameters
    ----------
    ticker
        Ticker of order to place (Ticker.ETH, Ticker.BTC, or "LTC")
    order_id
        order_id returned by place_limit_order
    """
    return True

# You can use print() and view the logs after sandbox run has completed
# Might help for debugging
class Strategy:
    """Aggressive market making for maximum profit."""

    def __init__(self) -> None:
        """Initialize with aggressive parameters."""
        
        # Inventory tracking
        self.inventory = {Ticker.ETH: 0.0, Ticker.BTC: 0.0, Ticker.LTC: 0.0}
        
        # Capital tracking
        self.capital = 100000.0
        
        # Orderbook tracking
        self.best_bid = {Ticker.ETH: None, Ticker.BTC: None, Ticker.LTC: None}
        self.best_ask = {Ticker.ETH: None, Ticker.BTC: None, Ticker.LTC: None}
        
        # Active orders
        self.active_orders = {
            Ticker.ETH: {'bid_id': None, 'ask_id': None},
            Ticker.BTC: {'bid_id': None, 'ask_id': None},
            Ticker.LTC: {'bid_id': None, 'ask_id': None}
        }
        
        # AGGRESSIVE PARAMETERS FOR HIGH PROFIT 
        """ EDIT THESE VALUES AND OPTIMIZE """
        self.base_order_size = 20.0  # 50x larger than before
        self.spread_improvement = 0.01  # Penny improvement on best bid/ask
        self.max_position = 100.0  # Allow large positions
        self.inventory_skew = 0.1  # Moderate inventory adjustment
        
        # Quote every update
        self.quote_frequency = 1  # Maximum aggression
        self.update_counter = 0
        
        # Track performance
        self.total_pnl = 0.0
        self.trades_count = 0

    def on_trade_update(self, ticker: Ticker, side: Side, quantity: float, price: float) -> None:
        """Monitor trades."""
        pass

    def on_orderbook_update(
        self, ticker: Ticker, side: Side, quantity: float, price: float
    ) -> None:
        """Aggressive quote updates."""
        
        # Update best prices
        if quantity == 0:
            if side == Side.BUY:
                self.best_bid[ticker] = None
            else:
                self.best_ask[ticker] = None
        else:
            if side == Side.BUY:
                self.best_bid[ticker] = price
            else:
                self.best_ask[ticker] = price
        
        # Don't wait - quote immediately
        self.update_counter += 1
        if self.update_counter % self.quote_frequency != 0:
            return
        
        if self.best_bid[ticker] and self.best_ask[ticker]:
            self._aggressive_quote(ticker)

    def on_account_update(
        self,
        ticker: Ticker,
        side: Side,
        price: float,
        quantity: float,
        capital_remaining: float,
    ) -> None:
        """Track fills and update inventory."""
        
        # Calculate realized PnL for this trade
        pnl_change = capital_remaining - self.capital
        self.total_pnl += pnl_change
        self.trades_count += 1
        
        # Update state
        self.capital = capital_remaining
        if side == Side.BUY:
            self.inventory[ticker] += quantity
        else:
            self.inventory[ticker] -= quantity
        
        print(f"{'BUY' if side == Side.BUY else 'SELL'} {quantity:.1f} {ticker.name} "
              f"@ {price:.2f} | Inv:{self.inventory[ticker]:+.1f} | "
              f"Cap:{self.capital:.0f} | Total PnL:{self.total_pnl:+.2f}")
        
        # Clear filled order
        if side == Side.BUY:
            self.active_orders[ticker]['bid_id'] = None
        else:
            self.active_orders[ticker]['ask_id'] = None
        
        # Emergency unwind if position too large
        if abs(self.inventory[ticker]) > self.max_position:
            self._emergency_unwind(ticker)

    def _aggressive_quote(self, ticker: Ticker) -> None:
        """Place aggressive quotes at top of book."""
        
        best_bid = self.best_bid[ticker]
        best_ask = self.best_ask[ticker]
        
        if not best_bid or not best_ask:
            return
        
        # Ensure valid spread
        if best_ask <= best_bid:
            return
        
        # Calculate inventory adjustment
        inv_adj = self.inventory[ticker] * self.spread_improvement * self.inventory_skew
        
        # Quote AGGRESSIVELY - just inside the best prices
        # This is "pennying" - stepping ahead of others by small amount
        tick_size = 0.01
        our_bid = best_bid + tick_size - inv_adj
        our_ask = best_ask - tick_size - inv_adj
        
        # Ensure we maintain spread
        if our_ask <= our_bid:
            mid = (best_bid + best_ask) / 2
            our_bid = mid - tick_size
            our_ask = mid + tick_size
        
        # Calculate sizes with inventory consideration
        bid_size = self._calculate_size(ticker, Side.BUY)
        ask_size = self._calculate_size(ticker, Side.SELL)
        
        # Update bid aggressively
        if bid_size > 0:
            # Cancel and replace every time
            if self.active_orders[ticker]['bid_id'] is not None:
                cancel_order(ticker, self.active_orders[ticker]['bid_id'])
            
            order_id = place_limit_order(Side.BUY, ticker, bid_size, our_bid, ioc=False)
            self.active_orders[ticker]['bid_id'] = order_id
        
        # Update ask aggressively
        if ask_size > 0:
            if self.active_orders[ticker]['ask_id'] is not None:
                cancel_order(ticker, self.active_orders[ticker]['ask_id'])
            
            order_id = place_limit_order(Side.SELL, ticker, ask_size, our_ask, ioc=False)
            self.active_orders[ticker]['ask_id'] = order_id

    def _calculate_size(self, ticker: Ticker, side: Side) -> float:
        """Calculate order size with inventory adjustment."""
        
        inv = self.inventory[ticker]
        
        # Stop adding to position if too large
        if side == Side.BUY and inv >= self.max_position * 0.7:
            return 0
        if side == Side.SELL and inv <= -self.max_position * 0.7:
            return 0
        
        # Adjust size based on inventory
        if side == Side.BUY:
            factor = max(0.2, 1.0 - abs(inv) / self.max_position)
        else:
            factor = max(0.2, 1.0 - abs(inv) / self.max_position)
        
        # Increase size if we need to flatten inventory
        if (side == Side.SELL and inv > 0) or (side == Side.BUY and inv < 0):
            factor *= 1.5
        
        return self.base_order_size * factor

    def _emergency_unwind(self, ticker: Ticker) -> None:
        """Unwind large positions immediately."""
        
        self._cancel_all(ticker)
        
        inv = self.inventory[ticker]
        best_bid = self.best_bid[ticker]
        best_ask = self.best_ask[ticker]
        
        if not best_bid or not best_ask:
            return
        
        if inv > self.max_position * 0.7:
            # Dump with IOC at slightly worse price
            size = min(inv * 0.5, inv - self.max_position * 0.5)
            place_limit_order(Side.SELL, ticker, size, best_bid * 0.998, ioc=True)
            print(f"EMERGENCY SELL {size:.1f} {ticker.name}")
        
        elif inv < -self.max_position * 0.7:
            size = min(abs(inv) * 0.5, abs(inv) - self.max_position * 0.5)
            place_limit_order(Side.BUY, ticker, size, best_ask * 1.002, ioc=True)
            print(f"EMERGENCY BUY {size:.1f} {ticker.name}")

    def _cancel_all(self, ticker: Ticker) -> None:
        """Cancel all orders."""
        if self.active_orders[ticker]['bid_id']:
            cancel_order(ticker, self.active_orders[ticker]['bid_id'])
            self.active_orders[ticker]['bid_id'] = None
        if self.active_orders[ticker]['ask_id']:
            cancel_order(ticker, self.active_orders[ticker]['ask_id'])
            self.active_orders[ticker]['ask_id'] = None
