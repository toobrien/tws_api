from flask              import Flask, render_template, Response
from flask_cors         import CORS
from ib_futures.fclient import fclient
from json               import loads, dumps
from sys                import argv


CONFIG = loads(open("./config.json", "r").read())

APP = Flask(__name__, static_folder = ".", static_url_path = "")
APP.config["CACHE_TYPE"] = "null"
CORS(APP)

L1_HANDLES          = {}
HANDLES_TO_QUOTES   = {}
TERM_IDS_TO_QUOTES  = {}
MODE                = None
NUM_TERMS           = None


@APP.route("/get_quotes", methods = [ "GET" ])
def get_quotes():

    return Response(dumps(TERM_IDS_TO_QUOTES))


@APP.route("/")
def get_root():

    return render_template(
                "index.html",
                hostname        = CONFIG["hostname"],
                port            = CONFIG["port"],
                update_ms       = CONFIG["update_ms"],
                mode            = MODE,
                chart_width     = CONFIG["chart"]["chart_width"],
                chart_height    = CONFIG["chart"]["chart_height"]
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

    if not quote["INITIALIZED"]:

        if tick_type == "BID" and not quote["INIT_BID"]:

            quote["INIT_BID"]       = args["price"]
        
        elif tick_type == "ASK" and not quote["INIT_ASK"]:

            quote["INIT_ASK"]       = args["price"]
        
        elif tick_type == "LAST" and not quote["INIT_LAST"]:

            quote["INIT_LAST"]      = args["price"]

        else:

            quote["INITIALIZED"]    = True

    else:

        if tick_type == "BID":

            quote["BID"]        = args["price"] - quote["INIT_BID"]
            quote["HIGH_BID"]   = max(quote["HIGH_BID", quote["BID"]])

        elif tick_type == "ASK":

            quote["ASK"]        = args["price"] - quote["ASK"]
            quote["LOW_ASK"]    = min(quote["LOW_ASK"], quote["ASK"])

        elif tick_type == "LAST":

            quote["LAST"]       = args["price"] - quote["LAST"]


if __name__ == "__main__":

    fc = fclient(
        host    = CONFIG["tws"]["host"],
        port    = CONFIG["tws"]["port"],
        id      = CONFIG["tws"]["client_id"]
    )

    # fc.set_market_data_type(4) // for frozen data when market is closed

    MODE                = argv[1]
    NUM_TERMS           = int(argv[2])
    qualified_symbols   = argv[3:]

    if MODE == "norm":
    
        fc.set_l1_stream_handler(norm_handler)

    elif MODE == "diff":

        fc.set_l1_stream_handler(diff_handler)

    else:

        print("mode must be one of: [ 'norm', 'diff' ]")

        exit()

    for pair in qualified_symbols:

        parts       = pair.split(":")
        symbol      = parts[0]
        exchange    = parts[1]

        ids = fc.get_instrument_ids(symbol, exchange)

        for instrument_id in ids[:NUM_TERMS]:

            handle = fc.open_l1_stream(instrument_id)

            if (handle):
            
                symbol  = instrument_id[0]
                term    = instrument_id[3]
                term_id = f"{symbol} {term}" 

                L1_HANDLES[handle]              = term_id
                HANDLES_TO_QUOTES[handle]       = {
                    "BID":      None,
                    "ASK":      None,
                    "LAST":     None,
                    "HIGH_BID": float("-inf"),
                    "LOW_ASK":  float("int")
                }
                TERM_IDS_TO_QUOTES[term_id]     = HANDLES_TO_QUOTES[handle]

                if MODE == "diff":

                    HANDLES_TO_QUOTES[handle]["INITIALIZED"]    = False
                    HANDLES_TO_QUOTES[handle]["INIT_BID"]       = None
                    HANDLES_TO_QUOTES[handle]["INIT_ASK"]       = None
                    HANDLES_TO_QUOTES[handle]["INIT_LAST"]      = None


    APP.run(
        host = CONFIG["hostname"],
        port = CONFIG["port"]
    )