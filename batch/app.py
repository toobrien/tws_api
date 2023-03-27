from sys import path

path.append("../")

from batch              import BATCH
from enum               import IntEnum
from ib_futures.fclient import fclient
from json               import loads


CONFIG = loads(open("./config.json").read())


class b_order(IntEnum):

    instrument_id       = 0
    action              = 1
    time_in_force       = 2
    qty                 = 3
    limit_price         = 4
    pt_price            = 5
    sl_price            = 6
    enabled             = 7
    

async def main(fc: fclient):

    for order in BATCH:

        if order[b_order.enabled]:
        
            params = {
                "instrument_id":        order[b_order.instrument_id],
                "action":               order[b_order.action],
                "type":                 "LMT",
                "time_in_force":        order[b_order.time_in_force],
                "order_id":             None,
                "limit_price":          order[b_order.limit_price],
                "qty":                  order[b_order.qty],
                "profit_taker_price":   order[b_order.pt_price],
                "stop_loss_price":      order[b_order.sl_price],
                "duration":             None
            }

            order_id            = await fc.get_next_order_id()
            params["order_id"]  = order_id

            _ = await fc.submit_order(**params)

            pass

    pass


if __name__ == "__main__":

    fc = fclient(
        host    = CONFIG["tws"]["host"],
        port    = CONFIG["tws"]["port"],
        id      = CONFIG["tws"]["client_id"]
    )

    fc.get_loop().run_until_complete(main(fc))