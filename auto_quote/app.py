from sys import path

path.append("../")

from asyncio                    import gather, sleep
from ib_futures.async_fclient   import async_fclient
from json                       import loads
from quote_defs                 import QUOTE_DEFS


CONFIG          = loads(open("./config.json", "r").read())
FC              = None
L1_HANDLES      = {}
L1_DATA         = {}
ORDER_STATES    = {}


###############################
## FCLIENT RESPONSE HANDLERS ##
###############################


def error_handler(reqId, errorCode, errorString, advancedOrderRejectJson = ""):

    parts = [
                f"reqId: {reqId}",
                f"code: {errorCode}",
                f"msg: {errorString}"
            ]

    if advancedOrderRejectJson:

        parts.append(f"adv: {advancedOrderRejectJson}")
    
    print("\t".join(parts))


def l1_stream_handler(args):

    handle      = args["reqId"]
    tick_type   = args["tickType"]
    quote       = L1_DATA[handle]

    if tick_type == "BID":

        quote["BID"] = args["price"]
    
    elif tick_type == "ASK":

        quote["ASK"] = args["price"]

    elif tick_type == "LAST":

        quote["LAST"] = args["price"]
    
    pass


def open_order_handler():

    # not sure how much needs implementing here

    pass


def order_status_handler(
    orderId:        int,
    status:         str,
    filled:         float,
    remaining:      float,
    avgFillPrice:   float,
    permId:         int,
    parentId:       int,
    lastFillPrice:  float,
    clientId:       int,
    whyHeld:        str,
    mktCapPrice:    float
):

    if orderId not in ORDER_STATES:
    
        ORDER_STATES[orderId] = {}

    order_state = ORDER_STATES[orderId]

    order_state["status"]           = status
    order_state["filled"]           = filled
    order_state["remaining"]        = remaining
    order_state["avgFillPrice"]     = avgFillPrice
    order_state["permId"]           = permId
    order_state["parentId"]         = parentId
    order_state["lastFillPrice"]    = lastFillPrice
    order_state["clientId"]         = clientId
    order_state["why_held"]         = whyHeld
    order_state["mktCapPrice"]      = mktCapPrice


##############
## QUOTING ##
##############


async def update_quote(
    l1_handle:          int,
    action:             str,
    entry:              float,
    max_worsening:      float,
    profit_taker_amt:   float,
    stop_loss_amt:      float,
    order_params:       dict,
):

    l1_latest                       = L1_DATA[l1_handle]
    best_bid                        = l1_latest["BID"]
    best_ask                        = l1_latest["ASK"]

    if  (not best_bid and action == "BUY") or \
        (not best_ask and action == "SELL"):

        return None

    current_price                   = order_params["limit_price"]
    base                            = best_bid  if action == "BUY" else best_ask
    comp_func                       = min       if action == "BUY" else max

    order_params["limit_price"]         =   comp_func(base + entry, current_price + max_worsening) \
                                            if current_price else base + entry

    order_params["profit_taker_price"]  = order_params["limit_price"] + profit_taker_amt
    order_params["stop_loss_price"]     = order_params["limit_price"] + stop_loss_amt

    new_order_ids = await FC.submit_order(**order_params)

    return (
        new_order_ids["parent_id"],
        new_order_ids["profit_taker_id"],
        new_order_ids["stop_loss_id"]
    )


async def quote_continuously(
    instrument_id:      tuple,
    max_fills:          int,
    qty:                int,
    action:             str,
    time_in_force:      str,
    entry:              float,
    enabled:            bool,
    max_worsening:      float,
    profit_taker_amt:   float,
    stop_loss_amt:      float,
    duration:           int,
    time_zone:          str
):

    # initialize state

    update_interval = duration + 1
    fills           = 0

    l1_handle               = await FC.open_l1_stream(instrument_id)
    L1_HANDLES[l1_handle]   = instrument_id

    L1_DATA[l1_handle] = {
        "BID":  None,
        "ASK":  None,
        "LAST": None
    }
    
    parent_id       = None
    stop_loss_id    = None
    profit_taker_id = None

    order_params = {
        "instrument_id":        instrument_id,
        "action":               action,
        "type":                 "LMT",
        "time_in_force":        time_in_force,
        "order_id":             None,
        "limit_price":          None,
        "qty":                  qty,
        "profit_taker_price":   None,
        "stop_loss_price":      None,
        "duration":             duration,
        "time_zone":            time_zone
    }

    # start quoting

    while (enabled):

        if  not parent_id or \
            ORDER_STATES[parent_id]["status"] == "Cancelled":

            parent_id                   = await FC.get_next_order_id()
            order_params["order_id"]    = parent_id

            res = await update_quote(
                l1_handle,
                action,
                entry,
                max_worsening,
                profit_taker_amt,
                stop_loss_amt,
                order_params
            )

            if res:

                parent_id       = res[0]
                stop_loss_id    = res[1]
                profit_taker_id = res[2]

        elif ORDER_STATES[parent_id]["status"] == "Filled":

            if  (profit_taker_id and ORDER_STATES[profit_taker_id]["status"] == "Filled") or \
                (stop_loss_id    and ORDER_STATES[stop_loss_id]["status"]    == "Filled"):

                fills += 1

                parent_id       = None
                profit_taker_id = None
                stop_loss_id    = None

        enabled = fills <= max_fills
        
        if enabled: 
            
            await sleep(update_interval)
            await FC.get_open_orders()

        pass

    pass


##################
## MAIN PROGRAM ##
##################


async def main():

    await gather(*[ quote_continuously(**qdef) for qdef in QUOTE_DEFS ])


if __name__ == "__main__":

    FC = async_fclient(
        host    = CONFIG["tws"]["host"],
        port    = CONFIG["tws"]["port"],
        id      = CONFIG["tws"]["client_id"]
    )
    
    FC.set_error_handler(error_handler)
    FC.set_l1_stream_handler(l1_stream_handler)
    #FC.set_open_order_handler(open_order_handler)
    FC.set_order_status_handler(order_status_handler)

    loop = FC.get_loop()
    
    loop.run_until_complete(main())

   