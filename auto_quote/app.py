from sys import path

path.append("../")

from asyncio                    import gather, run, sleep
from ib_futures.async_fclient   import async_fclient
from json                       import loads
from quote_defs                 import QUOTE_DEFS
from sys                        import argv


CONFIG          = loads(open("./config.json", "r").read())
FC              = None
L1_HANDLES      = {}
L1_DATA         = {}
ORDER_STATES    = {}


###############################
## FCLIENT RESPONSE HANDLERS ##
###############################


def error_handler(reqId, errorCode, errorString, advancedOrderRejectJson = ""):

    print(f"reqId: {reqId}\tcode: {errorCode}\tmsg: {errorString}\tadv: {advancedOrderRejectJson}")


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

    print(
        f"orderId: {orderId}\t",
        f"status: {status}\t",
        f"filled: {filled}\t",
        f"remaining: {remaining}\t",
        f"avgFillPrice: {avgFillPrice}\t",
        f"permId: {permId}\t",
        f"parentId: {parentId}\t",
        f"lastFillPrice: {lastFillPrice}\t",
        f"clientId: {clientId}\t",
        f"whyHeld: {whyHeld}\t",
        f"mktCapPrice: {mktCapPrice}"
    )


def open_order_end_handler():

    pass


##############
## QUOTING ##
##############


async def quote_continuously(
    instrument_id:  tuple,
    max_fills:      int,
    qty:            int,
    action:         str,
    entry:          int,
    enabled:        bool,
    max_worsening:  float,
    stop_loss:      float,
    take_profit:    int,
    duration:       int
):

    # initialize state

    update_interval = duration + 1
    fills           = 0

    l1_handle               = FC.open_l1_stream(instrument_id)
    L1_HANDLES[l1_handle]   = instrument_id
    L1_DATA[l1_handle]      = {
                                "BID":  None,
                                "ASK":  None,
                                "LAST": None
                            }
    l1_latest               = L1_DATA[l1_handle]
    
    active_order_ids    = {
        "parent_id":        None,
        "profit_taker_id":  None,
        "stop_loss_id":     None
    }
    order_params        = {
        "instrument_id":        instrument_id,
        "action":               action,
        "type":                 "LMT",
        "order_id":             None,
        "limit_price":          None,
        "qty":                  qty,
        "stop_loss":            stop_loss,
        "take_profit":          None,
    }

    # start quoting

    while (enabled):

        best_bid = l1_latest["BID"]
        best_ask = l1_latest["ASK"]

        if not active_order_ids["parent_id"]:

            order_id                        = FC.get_next_order_id()
            active_order_ids["parent_id"]   = order_id
            order_params["order_id"]        = order_id

            base = best_bid if action == "BUY" else best_ask

            order_params["limit_price"] = base + entry
            order_params["take_profit"] = order_params["limit_price"] + take_profit

            new_order_ids = FC.submit_order(**order_params)

            if "profit_taker_id" in new_order_ids:

                active_order_ids["profit_taker_id"] = new_order_ids["profit_taker_id"]

            if "stop_loss_id" in new_order_ids:

                active_order_ids["stop_loss_id"] = new_order_ids["stop_loss_id"]

        # ...

        if fills <= max_fills:

            enabled = False
        
        if enabled:
        
            await sleep(update_interval)

        else:

            break

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
    
    FC.set_l1_stream_handler(l1_stream_handler)
    FC.set_order_status_handler(order_status_handler)
    FC.set_open_order_end_handler(open_order_end_handler)

    run(main())