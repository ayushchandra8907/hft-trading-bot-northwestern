#include <cstdint>
#include <vector>
#include <math.h>
#include <cmath>
#include <string>
#include <unordered_map>
#include <algorithm>
#include <array>


enum class Side { buy = 0, sell = 1 };
enum class Ticker : std::uint8_t { ETH = 0, BTC = 1, LTC = 2 }; // NOLINT

bool place_market_order(Side side, Ticker ticker, float quantity);
std::int64_t place_limit_order(Side side, Ticker ticker, float quantity,
                               float price, bool ioc = false);
bool cancel_order(Ticker ticker, std::int64_t order_id);
void println(const std::string &text);

class Strategy {
private:
    std::unordered_map<Ticker, float> inventory = {
        {Ticker::ETH, 0.0f},
        {Ticker::BTC, 0.0f},
        {Ticker::LTC, 0.0f}
    };

    float capital = 100000.0f;

    std::unordered_map<Ticker, float> best_bid = {{Ticker::ETH, 0.0}, {Ticker::BTC, 0.0}, {Ticker::LTC, 0.0}};
    std::unordered_map<Ticker, float> best_ask = {{Ticker::ETH, 0.0}, {Ticker::BTC, 0.0}, {Ticker::LTC, 0.0}};

    std::unordered_map<Ticker, std::vector<std::int64_t>> active_orders = {
        {Ticker::ETH, {-1, -1} },
        {Ticker::BTC, {-1, -1} },
        {Ticker::LTC, {-1, -1} }
    };

    //hyperparamters
    float base_order_size = 25.0;

    float spread_improvement = 0.01;
    float max_position = 150.0;
    float inventory_skew = 0.01;

    int quote_frequency = 250;
    long update_counter = 0;

public:
    Strategy() {}

    void on_trade_update(Ticker ticker, Side side, float quantity, float price) {
        return;
    }
    
    void on_orderbook_update(Ticker ticker, Side side, float quantity, float price) {
        if(quantity == 0) {
            if(side == Side::buy) {
                best_bid[ticker] = 0.0;
            } else {
                best_ask[ticker] = 0.0;
            }
        } else {
            if(side == Side::buy) {
                best_bid[ticker] = price;
            } else {
                best_ask[ticker] = price;
            }
        }

        update_counter++;

        if(update_counter % quote_frequency == 0) {
            _aggresive_quote(ticker);
        } 

    }

  
    void on_account_update(Ticker ticker, Side side, float price, float quantity, float capital_remaining) {
        

        //update state

        capital = capital_remaining;
        if(side == Side::buy) {
            inventory[ticker] += quantity;
        } else {
            inventory[ticker] -= quantity;
        }

        // clear filled order
        if(side == Side::buy) {
            active_orders[ticker][0] = -1;
        } else {
            active_orders[ticker][1] = -1;
        }

        //emergyency unwind
        if(std::abs(inventory[ticker]) > max_position) {
            _emergency_unwind(ticker);
        }
        
    }

    // OTHER METHODS

    void _aggresive_quote(Ticker ticker) {
        float best_b = best_bid[ticker];
        float best_a = best_ask[ticker];

        if(best_b == 0 || best_a == 0) {
            return;
        }

        if(best_a <= best_b) {
            return;
        }

        //calculate inventory adjustment
        float inv_adj = inventory[ticker] * spread_improvement * inventory_skew;

        //quote aggro
        float tick_size = 0.01;
        float our_bid = best_b + tick_size - inv_adj;
        float our_ask = best_a - tick_size - inv_adj;

        //ensure we maintain spread
        if(our_ask <= our_bid) {
            float mid = (best_b + best_a) / 2;

            our_bid = mid - tick_size;
            our_ask = mid + tick_size;
        }

        //calcualte sizes with inventory consideratio
        float bid_size = _calculate_size(ticker, Side::buy);
        float ask_size = _calculate_size(ticker, Side::sell);

        //update bid aggro
        if(bid_size > 0) {
            if(active_orders[ticker][0] != -1) {
                cancel_order(ticker, active_orders[ticker][0]);
            }

            std::int64_t order_id = place_limit_order(Side::buy, ticker, bid_size, our_bid);
            active_orders[ticker][0] = order_id;
        }

        //update ask aggro
        if(ask_size > 0) {
            if(active_orders[ticker][1] != -1) {
                cancel_order(ticker, active_orders[ticker][1]);
            }

            std::int64_t order_id = place_limit_order(Side::sell, ticker, ask_size, our_ask);
            active_orders[ticker][1] = order_id;
        }

    }

    float _calculate_size(Ticker ticker, Side side) {
        float inv = inventory[ticker];

        if(side == Side::buy && inv >= max_position * .7) {
            return 0;
        }
        if(side == Side::sell && inv <= -max_position * .7) {
            return 0;
        }
        
        float factor = std::max(.2, 1.0 - std::abs(inv)/max_position);

        if ((side == Side::sell && inv > 0) || (side == Side::buy && inv < 0)){
            factor *= 1.5;
        }


        return base_order_size * factor;
        
    }

    void _emergency_unwind(Ticker ticker) {
        _cancel_all(ticker);

        float inv = inventory[ticker];
        float best_b = best_bid[ticker];
        float best_a = best_ask[ticker];

        if(best_b == 0 || best_a == 0) {
            return;
        }

        if(inv > max_position * .7) {
            float size = std::min(inv*.5, inv - max_position*.5);
            place_limit_order(Side::sell, ticker, size, best_b * .998, true);
        } else if(inv < -1*max_position * .7) {
            float size = std::min(std::abs(inv)*.5, std::abs(inv) - max_position*.5);
            place_limit_order(Side::buy, ticker, size, best_a*1.002, true);
        }

    }

    void _cancel_all(Ticker ticker) {
        if(active_orders[ticker][0] != -1) {
            cancel_order(ticker, active_orders[ticker][0]);
            active_orders[ticker][0] = -1;
        }

        if(active_orders[ticker][1] != -1) {
            cancel_order(ticker, active_orders[ticker][1]);
            active_orders[ticker][1] = -1;
        }
    }


};
