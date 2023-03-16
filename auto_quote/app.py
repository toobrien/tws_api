from sys import path

path.append("../")

from asyncio                    import gather, run, sleep
from ib_futures.async_fclient   import async_fclient
from json                       import loads
from quote_defs                 import QUOTES
from sys                        import argv


CONFIG      = loads(open("./config.json", "r").read())
FC          = None
L1_HANDLES  = {}
L1_DATA     = {}
ORDER_STATE = {}



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


##############
## QUOTING ##
##############


async def quote_continuously(quote: dict):

    # initialize state

    instr   = quote["instrument"]
    enabled = quote["enabled"]
    fills   = 0

    l1_handle               = FC.open_l1_stream(instr)
    L1_HANDLES[l1_handle]   = instr
    L1_DATA[l1_handle]      = {
                                "BID":  None,
                                "ASK":  None,
                                "LAST": None
                            }
    l1_latest               = L1_DATA[l1_handle]

    # start quoting

    while (enabled):

        best_bid = l1_latest["BID"]
        best_ask = l1_latest["ASK"]

        # ...

        enabled = fills <= quote["max_fills"]
        
        if enabled:
        
            await sleep(quote["update_interval"])

        else:

            break

    pass


##################
## MAIN PROGRAM ##
##################


async def main():

    await gather(*[ quote_continuously(quote) for quote in QUOTES ])


if __name__ == "__main__":

    FC = async_fclient(
        host    = CONFIG["tws"]["host"],
        port    = CONFIG["tws"]["port"],
        id      = CONFIG["tws"]["client_id"]
    )
    
    FC.set_l1_stream_handler(l1_stream_handler)
    FC.set_order_status_handler(order_status_handler)

    run(main())