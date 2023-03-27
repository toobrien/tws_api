from sys                import argv, path

path.append("../")

from flask              import Flask, render_template, Response
from flask_cors         import CORS
from ib_futures.fclient import fclient
from json               import loads, dumps


CONFIG = loads(open("./config.json", "r").read())

APP = Flask(__name__, static_folder = ".", static_url_path = "")
APP.config["CACHE_TYPE"] = "null"
CORS(APP)

L1_HANDLES              = {}
HANDLES_TO_QUOTES       = {}
FRIENDLY_IDS_TO_QUOTES  = {}
MODE                    = None
NUM_TERMS               = None


@APP.route("/get_quotes", methods = [ "GET" ])
def get_quotes():

    return Response(dumps(FRIENDLY_IDS_TO_QUOTES))


@APP.route("/")
def get_root():

    return render_template(
                "index.html",
                hostname        = CONFIG["hostname"],
                port            = CONFIG["port"],
                update_ms       = CONFIG["update_ms"],
                mode            = MODE,
                chart_width     = CONFIG["chart"]["width"],
                chart_height    = CONFIG["chart"]["height"]
            )


def norm_handler(args):

    handle      = args["reqId"]
    tick_type   = args["tickType"]

    quote = HANDLES_TO_QUOTES[handle]

    if tick_type == "BID":

        quote["BID"]        = args["price"]
        quote["HIGH_BID"]   = max(quote["HIGH_BID"], args["price"])
    
    elif tick_type == "ASK":

        quote["ASK"]        = args["price"]
        quote["LOW_ASK"]    = min(quote["LOW_ASK"], args["price"])

    elif tick_type == "LAST":

        quote["LAST"] = args["price"]


def diff_handler(args):

    handle      = args["reqId"]
    tick_type   = args["tickType"]

    quote = HANDLES_TO_QUOTES[handle]

    if not quote["INIT_PRICE"]:
            
        if tick_type == "LAST" and not quote["INIT_PRICE"]:

            quote["INIT_PRICE"] = args["price"]

        else:

            return

    else:

        if tick_type == "BID":

            quote["BID"]        = args["price"] - quote["INIT_PRICE"]
            quote["HIGH_BID"]   = max(quote["HIGH_BID"], quote["BID"])

        elif tick_type == "ASK":

            quote["ASK"]        = args["price"] - quote["INIT_PRICE"]
            quote["LOW_ASK"]    = min(quote["LOW_ASK"], quote["ASK"])

        elif tick_type == "LAST":

            quote["LAST"]       = args["price"] - quote["INIT_PRICE"]

    pass


async def main(fc: fclient):

    # fc.set_market_data_type(4) // for frozen data when market is closed

    MODE                = argv[1]
    NUM_TERMS           = int(argv[2])
    qualified_symbols   = argv[3:]
    width               = None

    if MODE == "norm":
    
        fc.set_l1_stream_handler(norm_handler)

    elif MODE == "diff":

        fc.set_l1_stream_handler(diff_handler)

    elif "rcal" in MODE:

        parts = MODE.split(":")
        MODE  = f"{parts[0]}:rcal"

        if "diff" in MODE:

            fc.set_l1_stream_handler(diff_handler)

        else:

            fc.set_l1_stream_handler(norm_handler)

        width = int(parts[2])

    else:

        print("mode must be one of: [ 'norm', 'diff', 'rcal:<width>' ]")

        exit()

    for pair in qualified_symbols:

        parts       = pair.split(":")
        symbol      = parts[0]
        exchange    = parts[1]

        ids = (await fc.get_instrument_ids(symbol, exchange))[:NUM_TERMS]

        if "rcal" in MODE:

            new_ids = []

            for i in range(len(ids[:-width])):

                front_leg   = ids[i]
                back_leg    = ids[i + width]

                new_id = ( front_leg[0], front_leg[1], "rcal", front_leg[3], back_leg[3] )

                new_ids.append(new_id)

            ids = new_ids

        for instrument_id in ids:

            handle = await fc.open_l1_stream(instrument_id)

            if (handle):
            
                symbol      = instrument_id[0]
                terms       = "".join(instrument_id[3:])
                friendly_id = f"{symbol}:{terms}"

                L1_HANDLES[handle]                  = friendly_id
                HANDLES_TO_QUOTES[handle]           = {
                    "BID":      None,
                    "ASK":      None,
                    "LAST":     None,
                    "HIGH_BID": -10**8,
                    "LOW_ASK":  10**8
                }
                FRIENDLY_IDS_TO_QUOTES[friendly_id] = HANDLES_TO_QUOTES[handle]

                if "diff" in MODE:

                    HANDLES_TO_QUOTES[handle]["INIT_PRICE"] = None


    APP.run(
        host = CONFIG["hostname"],
        port = CONFIG["port"]
    )


if __name__ == "__main__":

    fc = fclient(
        host    = CONFIG["tws"]["host"],
        port    = CONFIG["tws"]["port"],
        id      = CONFIG["tws"]["client_id"]
    )

    loop = fc.get_loop()

    loop.run_until_complete(main(fc))