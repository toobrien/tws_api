from flask                  import Flask, render_template, Response
from flask_cors             import CORS
from ib_futures.fclient     import fclient
from json                   import loads, dumps
from l1_chart.instruments   import INSTRUMENTS


CONFIG = loads(open("./config.json", "r").read())

APP = Flask(__name__, static_folder = ".", static_url_path = "")
APP.config["CACHE_TYPE"] = "null"
CORS(APP)

L1_HANDLES  = {}
QUOTES      = {}


@APP.route("/get_instruments", methods = [ "GET" ])
def get_instruments():

    res = {
        str(instrument_id): handle
        for handle, instrument_id in L1_HANDLES.items()
    }

    return Response(dumps(res))


@APP.route("/get_quotes", methods = [ "GET" ])
def get_quotes():

    res = QUOTES

    return Response(dumps(res))


@APP.route("/")
def get_root():

    return render_template(
                "index.html",
                hostname        = CONFIG["hostname"],
                port            = CONFIG["port"],
                update_ms       = CONFIG["update_ms"],
                max_samples     = CONFIG["max_samples"],
                cull_samples    = CONFIG["cull_samples"],
                chart_width     = CONFIG["chart_width"],
                chart_height    = CONFIG["chart_height"],
                utc_offset      = CONFIG["utc_offset"] * 3600
            )

def l1_stream_handler(args):

    handle          = args["reqId"]
    
    '''
    # check output on console

    instrument_id   = L1_HANDLES[handle]
    measure         =   args["size"]  if "size" in args else  \
                        args["price"] if "price" in args else \
                        args["value"] if "value" in args else \
                        None

    out = f"{str(instrument_id):50s}{str(handle):5s}{args['tickType']:20s}{measure}"

    print(out)
    '''

    tick_type = args["tickType"]

    quote = QUOTES[handle]

    if tick_type == "BID":

        quote["BID"] = args["price"]
    
    elif tick_type == "ASK":

        quote["ASK"] = args["price"]

    elif tick_type == "LAST":

        quote["LAST"] = args["price"]
    
    pass


if __name__ == "__main__":

    fc = fclient(
        host    = CONFIG["tws"]["host"],
        port    = CONFIG["tws"]["port"],
        id      = CONFIG["tws"]["client_id"]
    )

    # fc.set_market_data_type(4) // for frozen data when market is closed

    fc.set_l1_stream_handler(l1_stream_handler)

    for instrument_id in INSTRUMENTS:

        handle = fc.open_l1_stream(instrument_id)

        if (handle):
        
            L1_HANDLES[handle]  = instrument_id
            QUOTES[handle]      = {
                "BID":  None,
                "ASK":  None,
                "LAST": None
            }

        #fc.close_l1_stream(handle)

    APP.run(
        host = CONFIG["hostname"],
        port = CONFIG["port"]
    )