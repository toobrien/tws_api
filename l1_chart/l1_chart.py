from sys import path

path.append("..")

from ib_futures.fclient import fclient
from json               import loads
from ib_futures.structs import instrument
from time               import sleep
from instruments        import INSTRUMENTS


CONFIG      = loads(open("../config.json", "r").read())
L1_HANDLES  = {}


def l1_stream_handler(args):

    handle          = args["reqId"]
    instrument_id   = L1_HANDLES[handle]
    measure         =   args["size"]  if "size" in args else  \
                        args["price"] if "price" in args else \
                        args["value"] if "value" in args else \
                        None

    out = f"{str(instrument_id):50s}{str(handle):5s}{args['tickType']:20s}{measure}"

    print(out)
    
    pass


if __name__ == "__main__":

    fc = fclient(
        host    = CONFIG["host"],
        port    = CONFIG["port"],
        id      = CONFIG["client_id"]
    )

    # fc.set_market_data_type(4) // for frozen data when market is closed

    fc.set_l1_stream_handler(l1_stream_handler)

    for instrument_id in INSTRUMENTS:

        handle = fc.open_l1_stream(instrument_id)

        L1_HANDLES[handle] = instrument_id

        #fc.close_l1_stream(handle)

    pass

