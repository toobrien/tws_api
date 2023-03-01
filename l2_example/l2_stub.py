from sys import path

path.append("..")

from ib_futures.fclient import fclient
from json               import loads
from time               import sleep
from instruments        import INSTRUMENTS


CONFIG      = loads(open("../config.json", "r").read())
L2_HANDLES  = {}


def l2_stream_handler(args):

    handle          = args["reqId"]
    instrument_id   = L2_HANDLES[handle]
    
    pass


if __name__ == "__main__":

    fc = fclient(
        host    = CONFIG["host"],
        port    = CONFIG["port"],
        id      = CONFIG["client_id"]
    )

    # fc.set_market_data_type(4) // for frozen data when market is closed

    fc.set_l2_stream_handler(l2_stream_handler)

    for instrument_id in INSTRUMENTS:

        handle = fc.open_l1_stream(instrument_id)

        L2_HANDLES[handle] = instrument_id

        #fc.close_l2_stream(handle)

    pass

