from sys import path

path.append("../")

from ib_futures.fclient     import fclient
from json                   import loads
from quote_defs             import QUOTE_DEFS
from sys                    import argv
from time                   import sleep


CONFIG      = loads(open("./config.json", "r").read())
L1_HANDLES  = {}
L1_DATA     = {}
ORDERS      = {}
ENABLED     = {}


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


##################
## MAIN PROGRAM ##
##################


def quote_continuously(fc: fclient, instr: tuple, qdef: dict):

    # initialize data state

    handle = fc.open_l1_stream(instr)
    
    L1_HANDLES[handle]  = instr
    L1_DATA[handle]     = {
        "BID":  None,
        "ASK":  None,
        "LAST": None
    }
    l1_latest           = L1_DATA[handle]
    ORDERS[instr]       = {}
    active_orders       = ORDERS[instr]
    ENABLED[instr]      = True

    # initialize quote parameters

    update_interval     = qdef["update_interval"]
    max_fills           = qdef["max_fills"]
    multiplier          = qdef["multiplier"]
    quote_params        = qdef["quote_params"]
    fills               = 0
    enabled             = True

    # start quoting

    while (enabled):

        best_bid = l1_latest["BID"]
        best_ask = l1_latest["ASK"]

        if not (best_bid or best_ask):

            continue

        for params in quote_params:

            side        = params["side"]
            relative_to = params["best"]
            entry       = params["entry"]
            tp          = None if "tp" not in params else params["tp"]
            sl          = None if "sl" not in params else params["sl"]
            sl_delay    = None if "sl_delay" not in params else params["sl_delay"]

            pass

        if fills >= max_fills or not ENABLED[instr]:

            break
        
        else:
        
            sleep(update_interval)

    pass


if __name__ == "__main__":
    
    fc = fclient(
        host    = CONFIG["tws"]["host"],
        port    = CONFIG["tws"]["port"],
        id      = CONFIG["tws"]["client_id"]
    )
    
    fc.set_l1_stream_handler(l1_stream_handler)
    fc.set_order_status_handler(order_status_handler)

    instr   = ( *argv[1:], )
    qdef    = QUOTE_DEFS[instr]

    quote_continuously(fc, instr, qdef)

    pass

    '''
    ids = fc.submit_order(instr, "BUY", "LMT", 2.5000, 1, None, None)

    if ids:
    
        sleep(10)

        fc.cancel_order(ids["parent_id"])
    '''