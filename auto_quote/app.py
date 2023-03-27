from sys import path

path.append("../")

from asyncio            import gather, sleep
from datetime           import datetime
from ib_futures.fclient import fclient
from json               import loads
from quote_defs         import QUOTE_DEFS
from typing             import List


CONFIG              = loads(open("./config.json", "r").read())
L1_HANDLES          = {}
L1_DATA             = {}
ORDER_STATES        = {}
MARKET_DATA_OK      = True
TWS_CONNECTION_OK   = True


###############################
## FCLIENT RESPONSE HANDLERS ##
###############################


def error_handler(reqId, errorCode, errorString, advancedOrderRejectJson = ""):

    # connection and market data related errors

    if errorCode == 109:

        # Price is out of the range defined by the Percentage setting at order defaults frame. The order will not be transmitted. 

        # Price entered is outside the range of prices set in TWS or IB Gateway Order Precautionary Settings 

        pass

    elif errorCode == 133:

        # Submit new order failed.

        pass

    elif errorCode == 134:

        # Modify order failed.

        pass

    elif errorCode == 136:

        # This order cannot be cancelled.

        pass

    elif errorCode == 161:

        # Cancel attempted when order is not in a cancellable state. Order permId = 

        # An attempt was made to cancel an order not active at the time.

        pass

    elif errorCode == 163:

        # The price specified would violate the percentage constraint specified in the default order settings.
        
        # The order price entered is outside the allowable range specified in the Order Precautionary Settings of TWS or IB Gateway

        pass

    elif errorCode == 164:

        # There is no market data to check price percent violations.

        # No market data is available for the specified contract to determine whether the specified price is outside the price percent precautionary order setting. 

        pass

    elif errorCode == 201:

        # Order rejected - Reason: 

        # An attempted order was rejected by the IB servers.
        # See Order Placement Considerations for additional information/considerations for these errors.

        pass

    elif errorCode == 202:

        # Order cancelled - Reason:

        # An active order on the IB server was cancelled. See Order Placement Considerations for additional information/considerations for these errors.

        pass

    elif errorCode == 320:

        # Server error when reading an API client request. 

        pass

    elif errorCode == 321:

        # Server error when validating an API client request. 

        pass

    elif errorCode == 322:

        #Server error when processing an API client request. 

        pass

    elif errorCode == 323:

        # Server error: cause - s 

        pass

    elif errorCode == 334:

        # Invalid Good Till Date order

        pass

    elif errorCode == 336:

        # The time or time zone is invalid.
        # The correct format is hh:mm:ss xxx where xxx is an optionally specified time-zone.
        # E.g.: 15:59:00 EST Note that there is a space between the time and the time zone. 
        # If no time zone is specified, local time is assumed. 

        pass

    elif errorCode == 337:

        # The date, time, or time-zone entered is invalid.
        # The correct format is yyyymmdd hh:mm:ss xxx where yyyymmdd and xxx are optional.
        # E.g.: 20031126 15:59:00 ESTNote that there is a space between the date and time, and between the time and time-zone. 

        pass

    elif errorCode == 343:

        # The date, time, or time-zone entered is invalid. The correct format is yyyymmdd hh:mm:ss xxx 

        pass

    elif errorCode == 391:

        # The time or time-zone entered is invalid. The correct format is hh:mm:ss xxx 

        pass

    elif errorCode == 504:

        # Not connected.

        # You are trying to perform a request without properly connecting and/or after connection to the TWS has been broken probably due to an unhandled exception within your client application. 

        pass

    elif errorCode == 1100:

        # Connectivity between IB and the TWS has been lost.

        # Your TWS/IB Gateway has been disconnected from IB servers.
        # This can occur because of an internet connectivity issue, a nightly reset of the IB servers, or a competing session. 

        pass

    elif errorCode == 1101:

        # Connectivity between IB and TWS has been restored- data lost.

        # The TWS/IB Gateway has successfully reconnected to IB's servers.
        # Your market data requests have been lost and need to be re-submitted. 

        pass

    elif errorCode == 1102:

        # Connectivity between IB and TWS has been restored- data maintained. 

        # The TWS/IB Gateway has successfully reconnected to IB's servers. 
        # Your market data requests have been recovered and there is no need for you to re-submit them. 

        pass

    elif errorCode == 2102:

        # Unable to modify this order as it is still being processed. 

        # If you attempt to modify an order before it gets processed by the system, the modification will be rejected.
        # Wait until the order has been fully processed before modifying it. See Placing Orders for further details. 

        pass

    elif errorCode == 2103:

        # A market data farm is disconnected.

        # Indicates a connectivity problem to an IB server.
        # Outside of the nightly IB server reset, this typically indicates an underlying ISP connectivity issue. 

        pass

    elif errorCode == 2104:

        # Market data farm connection is OK 

        # A notification that connection to the market data server is ok.
        # This is a notification and not a true error condition, and is expected on first establishing connection

        pass

    elif errorCode == 2105:

        # A historical data farm is disconnected.

        # Indicates a connectivity problem to an IB server.
        # Outside of the nightly IB server reset, this typically indicates an underlying ISP connectivity issue. 

        pass

    elif errorCode == 2106:

        # A historical data farm is connected.

        # A notification that connection to the market data server is ok.
        # This is a notification and not a true error condition, and is expected on first establishing connection. 

        pass

    elif errorCode == 2107:

        # A historical data farm connection has become inactive but should be available upon demand. 

        # Whenever a connection to the historical data farm is not being used because there is not an active historical data request, the connection will go inactive in IB Gateway. 
        # This does not indicate any connectivity issue or problem with IB Gateway. As soon as a historical data request is made the status will change back to active. 

        pass

    elif errorCode == 2108:

        # A market data farm connection has become inactive but should be available upon demand. 

        # Whenever a connection to our data farms is not needed, it will become dormant.
        # There is nothing abnormal nor wrong with your client application nor with the TWS.
        # You can safely ignore this message.

        pass

    elif errorCode == 2110:

        # Connectivity between TWS and server is broken. It will be restored automatically.

        # Indicates a connectivity problem between TWS or IBG and the IB server.
        # This will usually only occur during the IB nightly server reset; cases at other times indicate a problem in the local ISP connectivity. 

        pass

    elif errorCode == 2157:

        # ???

        pass

    elif errorCode == 2158:

        # Sec-def data farm connection is OK 

        # A notification that connection to the Security definition data server is ok.
        # This is a notification and not a true error condition, and is expected on first establishing connection. 

        pass

    elif errorCode == 10006:

        # Missing parent order.

        # The parent order ID specified cannot be found.
        # In some cases this can occur with bracket orders if the child order is placed immediately after the parent order; a brief pause of 50 ms or less will be necessary before the child order is transmitted to TWS/IBG. 

        pass

    elif errorCode == 10148:

        # OrderId <OrderId> that needs to be cancelled can not be cancelled, state:

        pass

    # print message

    if advancedOrderRejectJson == "":

        print(f"reqId: {reqId}\tcode: {errorCode}\tmsg: {errorString}")

    else:

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


def open_order_handler(orderId, contract, order, orderState):

    # not sure how much needs implementing here

    if orderState.status == "Submitted":
    
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
    order_state["whyHeld"]          = whyHeld
    order_state["mktCapPrice"]      = mktCapPrice


##############
## QUOTING ##
##############


def check_hours(inactive_hours):

    active_hours = True

    if inactive_hours:

        for rng in inactive_hours:

            start   = rng[0]
            end     = rng[1]

            now = datetime.now().strftime("%H:%M:%S")

            if start < now < end:

                active_hours = False

                break

    return active_hours


async def update_quote(
    fc:                 fclient,
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

        return ( None, None, None )

    current_price                   = order_params["limit_price"]
    base                            = best_bid  if action == "BUY" else best_ask
    comp_func                       = min       if action == "BUY" else max

    order_params["limit_price"]         =   comp_func(base + entry, current_price + max_worsening) \
                                            if current_price else base + entry
    order_params["profit_taker_price"]  =   order_params["limit_price"] + profit_taker_amt
    order_params["stop_loss_price"]     =   order_params["limit_price"] + stop_loss_amt

    new_order_ids = await fc.submit_order(**order_params)

    return (
        new_order_ids["parent_id"],
        new_order_ids["profit_taker_id"],
        new_order_ids["stop_loss_id"]
    )


async def quote_continuously(
    fc:                 fclient,
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
    update_interval:    int,
    duration:           int,
    inactive_hours:     List
):

    # initialize state

    fills   = 0
    enabled = enabled and check_hours(inactive_hours)

    l1_handle               = await fc.open_l1_stream(instrument_id)
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
        #"duration":             duration   # apparently can't update this, so not used
    }

    # start quoting

    while (enabled):

        if (parent_id not in ORDER_STATES or ORDER_STATES[parent_id]["status"] == "Cancelled"):

            parent_id = await fc.get_next_order_id()

            # else, reuse parent_id; i.e., modify existing order, rather than place new

        if  (parent_id not in ORDER_STATES or ORDER_STATES[parent_id]["status"] != "Filled") and \
            (MARKET_DATA_OK and TWS_CONNECTION_OK):

            order_params["order_id"] = parent_id

            parent_id, profit_taker_id, stop_loss_id = await update_quote(
                fc,
                l1_handle,
                action,
                entry,
                max_worsening,
                profit_taker_amt,
                stop_loss_amt,
                order_params
            )

        elif    parent_id in ORDER_STATES and \
                ORDER_STATES[parent_id]["status"] == "Filled" and \
                (
                    (profit_taker_id and ORDER_STATES[profit_taker_id]["status"] == "Filled") or
                    (stop_loss_id    and ORDER_STATES[stop_loss_id]["status"]    == "Filled")
                ):
    
            fills += 1

            parent_id       = None
            profit_taker_id = None
            stop_loss_id    = None

        enabled = (fills <= max_fills) and check_hours(inactive_hours)
        
        if enabled:

            await sleep(update_interval)
            await fc.get_open_orders()

        pass


##################
## MAIN PROGRAM ##
##################


async def main(fc: fclient):

    fc.set_error_handler(error_handler)
    fc.set_l1_stream_handler(l1_stream_handler)
    fc.set_open_order_handler(open_order_handler)
    fc.set_order_status_handler(order_status_handler)
   
    await gather(*[ quote_continuously(fc, **qdef) for qdef in QUOTE_DEFS ])


if __name__ == "__main__":

    fc = fclient(
        host    = CONFIG["tws"]["host"],
        port    = CONFIG["tws"]["port"],
        id      = CONFIG["tws"]["client_id"]
    )

    loop = fc.get_loop()
    
    loop.run_until_complete(main(fc))