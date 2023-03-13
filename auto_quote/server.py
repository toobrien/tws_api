from sys import path

path.append("../")

from ib_futures.fclient     import fclient
from json                   import loads
from time                   import sleep


CONFIG              = loads(open("./config.json", "r").read())
ORDER_ID_TO_INSTR   = {}


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


if __name__ == "__main__":
    
    fc = fclient(
        host    = CONFIG["tws"]["host"],
        port    = CONFIG["tws"]["port"],
        id      = CONFIG["tws"]["client_id"]
    )

    instr = ( "HO", "NYMEX", "single", "J23" )

    fc.set_order_status_handler(order_status_handler)

    ids = fc.submit_order(instr, "BUY", "LMT", 2.5000, 1, None, None)

    for id in ids:
    
        ORDER_ID_TO_INSTR[id] = instr

    if ids:
    
        sleep(10)

        fc.cancel_order(ids["parent_id"])