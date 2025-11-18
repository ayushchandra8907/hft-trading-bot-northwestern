# Northwestern Algorithmic Trading Competition 2025 – HFT and Crypto Market-Making

**Team:** Parry Nall & Ayush Chandra  
**Ranking:** Top 10 / 50 (20%) in High Frequency Trading (HFT) Case  
October 18, 2025

---

## Project Overview

This repository contains our team submission for the **Northwestern Algorithmic Trading Competition 2025**, organized by **NU Fintech**. We participated in both the **High Frequency Trading (HFT)** and **Crypto Market-Making** cases.

Our adaptive **C++ market-making algorithm** was designed to:

1. **Perform multi-asset market making** across BTC, ETH, and LTC with independent orderbooks, inventory tracking, and risk management.  
2. **Implement adaptive quoting logic**, continuously adjusting bid/ask levels based on market spread and inventory exposure.  
3. **Dynamically scale order sizes** to balance capital utilization and inventory risk.  
4. **Trigger emergency unwind routines** when positions exceed maximum safety limits.  
5. **Refresh quotes at a fixed frequency** to maintain optimal placement during high volatility.  

Our strategy achieved **Top 10 / 50 (20%) in the HFT case** based on total Profit and Loss (PnL).

---

## Methods Overview

- **on_orderbook_update()** — Updates best bid/ask prices and triggers aggressive quote placement.  
- **on_account_update()** — Updates capital and inventory after fills; triggers emergency unwind if positions exceed thresholds.  
- **on_trade_update()** — Tracks trade fills and realized/unrealized PnL.  
- **_aggresive_quote()** — Places adaptive limit orders using spread improvement and inventory skew adjustments.  
- **_calculate_size()** — Determines order size based on current inventory, exposure, and risk parameters.  
- **_emergency_unwind()** — Reduces positions safely when exposure exceeds maximum limits.  
- **_cancel_all()** — Cancels stale orders to prevent execution errors before re-quoting.

---

## Hyperparameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `base_order_size` | 25–30 | Default size for each order. |
| `spread_improvement` | 0.01 | Tightens quotes relative to market spread. |
| `max_position` | 150–200 | Caps maximum exposure per asset. |
| `inventory_skew` | 0.01 | Adjusts quote bias to offset overexposure. |
| `quote_frequency` | 150–250 | Sets how often quotes are refreshed. |

These were tuned through backtesting and simulated competition runs to balance risk management and PnL performance.

---

## Competition Context

**Event:** Northwestern Algorithmic Trading Competition 2025  
**Organized by:** Northwestern Fintech (NUFT)  
**Sponsors:** IMC Trading, Hudson River Trading (HRT), Five Rings, Chicago Trading Company, All Options  

**Cases Entered:**  
- **High Frequency Trading (HFT)** — C++ adaptive market-making under high volatility (**Placed Top 10 / 50**).  
- **Crypto Market-Making** — Focused on liquidity provision and volatility-based quoting strategies.  

Both algorithms were executed live on the **NU Fintech Exchange**, where strategies were ranked by PnL and execution stability.

---

## Results

- **Participated in:** HFT and Crypto Market-Making Cases  
- **HFT Ranking:** Top 10 / 50 (20%)  
- **Metric:** Final Net PnL (Capital + Portfolio Value)  

![Competition Results Screenshot](/pnl_graph.png)

---
