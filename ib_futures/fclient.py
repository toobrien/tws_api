from asyncio        import new_event_loop
from functools      import partial
from ibapi.client   import EClient
from ibapi.contract import ComboLeg, Contract
from ibapi.ticktype import TickTypeEnum 
from ibapi.wrapper  import EWrapper
from .structs       import instrument, month_codes
from threading      import get_ident, Thread
from time           import sleep


# sleep before any call to EClient
# no more than 50 requests per second

SLEEP = 0.02

# 1 = ???
# 2 = ???
# 3 = delayed, frozen
# 4 = ???

DEFAULT_DATA_TYPE = 4

# maximum concurrent data lines

MAX_DATA_LINES = 50

NOT_FOUND = 0


##############
## EWRAPPER ##
##############


class wrapper(EWrapper):


    def __init__(self):

        EWrapper.__init__(self)


    def connectAck(self):

        print(f"{get_ident()}:wrapper:connectAck")


    def nextValidId(self, orderId):

        super().nextValidId(orderId)

        print(f"{get_ident()}:wrapper:nextValidId:{orderId}")


    def connectionClosed(self):

        print(f"{get_ident()}:wrapper:connectionClosed")


    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson = ""):
        
        # this will print the message

        super().error(reqId, errorCode, errorString, advancedOrderRejectJson = "")
        
        if errorCode == 10090:

            # market data warning
            
            pass

        if errorCode == 200:
        
            # attempt to quote nonexistent contract, probably
            
            self.resolve(reqId)
    
        elif errorCode == 300:

            # attempt to cancel stream, but not open... dont worry
            
            pass


    def contractDetails(self, reqId, contractDetails):

        super().contractDetails(reqId, contractDetails)

        self.results[reqId]["res"].append(contractDetails)


    def contractDetailsEnd(self, reqId):

        self.resolve(reqId)


    # L1 data functions: tickPrice, tickSize, tickValue, tickGeneric

    def tickPrice(self, reqId, tickType, price, attrib):

        super().tickPrice(reqId, tickType, price, attrib)

        self.handlers["l1_stream"](
            {
                "reqId":    reqId, 
                "tickType": TickTypeEnum.to_str(tickType),
                "price":    price, 
                "attrib":   attrib
            }
        )

    def tickSize(self, reqId, tickType, size):

        super().tickSize(reqId, tickType, size)

        self.handlers["l1_stream"](
            {
                "reqId":    reqId, 
                "tickType": TickTypeEnum.to_str(tickType),
                "size":     size
            }
        )

    def tickString(self, reqId, tickType, value):

        super().tickString(reqId, tickType, value)

        self.handlers["l1_stream"](
            {
                "reqId":    reqId,
                "tickType": TickTypeEnum.to_str(tickType),
                "value":    value
            }
        )


    def tickGeneric(self, reqId, tickType, value):

        super().tickString(reqId, tickType, value)

        self.handlers["l1_stream"](
            {
                "reqId":    reqId,
                "tickType": TickTypeEnum.to_str(tickType),
                "value":    value
            }
        )


    def check_mkt_data_finished(self, reqId, params, field):

        if field in params["fields"]: 
            
            self.resolve(reqId)


    def resolve(self, reqId):
            
        f = self.results[reqId]

        self.loop.call_soon_threadsafe(
            f["fut"].set_result,
            f["res"]
        )

        del self.results[reqId]


#############
## ECLIENT ##
#############


class fclient(wrapper, EClient):


    def __init__(self, host, port, id):
        
        wrapper.__init__(self)
        EClient.__init__(self, wrapper = self)

        # connection

        self.host   = host
        self.port   = port
        self.id     = id

        # requests, results, and callbacks
        
        self.reqId      = -1
        self.results    = {}
        self.handlers   = {}

        # contract store

        self.contract_store = {}

        # concurrency
        
        self.open_data_lines    = 0
        self.market_data_queue  = []
        self.loop               = new_event_loop()
        self.last_exec          = -1

        # initialize connection

        self.connect(host, port, id)

        # for some reason there is a delay in connecting, and isConnected() is not reliable...

        sleep(0.5)

        thread = Thread(target=self.run)

        thread.start()


    #####################
    ## ECLIENT PRIVATE ##
    #####################


    # see constants at top of file

    def reqMarketDataType(self, kwargs):

        self.schedule(
            super().reqMarketDataType, 
            kwargs
        )


    def reqMktData(self, kwargs):

        self.reqId          += 1
        kwargs["reqId"]     =  self.reqId

        if self.open_data_lines <= MAX_DATA_LINES:            

            self.schedule(
                super().reqMktData,
                kwargs
            )

            # super().reqMktData(**kwargs)

            self.open_data_lines += 1
        
        else:

            self.market_data_queue.append(kwargs)

        return self.reqId


    def cancelMktData(self, kwargs):

        self.schedule(
            super().cancelMktData,
            kwargs
        )

        self.open_data_lines -= 1

        if self.market_data_queue:

            # only one retry per cancel!
            # any function that calls reqMktData
            # should also call cancelMktData

            self.schedule(
                self.reqMktData,
                self.market_data_queue.pop()
            )


    async def reqContractDetails(self, kwargs):

        self.reqId  += 1
        fut         = self.get_future(self.reqId)

        kwargs["reqId"] = self.reqId

        self.schedule(
            super().reqContractDetails, 
            kwargs
        )

        return await fut


    ####################
    ## ECLIENT PUBLIC ##
    ####################


    def set_market_data_type(self, type: int):

        self.reqMarketDataType(type)   


    def set_l1_stream_handler(self, handler):

        self.handlers["l1_stream"] = handler


    def set_l2_stream_handler(self, handler):

        self.handlers["l2_stream"] = handler


    def get_contract(self, instr: instrument):
        
        if instr.symbol not in self.contract_store:

            con = Contract()

            con.symbol      = instr.symbol
            con.secType     = "FUT"
            con.exchange    = instr.exchange
            con.currency    = "USD"

            contracts = self.loop.run_until_complete(
                            self.reqContractDetails(
                                {
                                    "contract": con        
                                }
                            )
                        )

            for contract_details in contracts:

                con_month   = contract_details.contractMonth
                contract_id = month_codes[int(con_month[-2:])] + con_month[2:4]

                self.contract_store[contract_id] = contract_details

        res = None

        if instr.type == "single":

            contract_id = instr.legs[0]

            try:
                
                res = self.contract_store[contract_id].contract

            except KeyError:

                print(f"{contract_id} not found")

            pass

        else:

            try:

                comboLegs = []

                for leg in instr.legs:

                    if instr.type == "custom":

                        leg = leg.split(":")[1]

                    contract_details = self.contract_store[leg]

                    cl = ComboLeg()

                    cl.conId    = contract_details.contract.conId
                    cl.ratio    = 0
                    cl.action   = ""
                    cl.exchange = instr.exchange

                    comboLegs.append(cl)

                if instr.type == "rcal":

                    comboLegs[0].ratio  = 1
                    comboLegs[0].action = "BUY"

                    comboLegs[1].ratio  = 1
                    comboLegs[1].action = "SELL"

                elif instr.type == "fly":

                    comboLegs[0].ratio = 1
                    comboLegs[0].action = "BUY"

                    comboLegs[1].ratio  = 2
                    comboLegs[1].action = "SELL"

                    comboLegs[2].ratio  = 1
                    comboLegs[2].action = "BUY"

                elif instr.type == "custom":

                    for i in range(len(instr.legs)):

                        qty     = instr.legs[i].split(":")[0]
                        action  = "SELL" if qty[0] == "-" else "BUY"
                        ratio   = int(qty[1:])

                        comboLegs[i].ratio  = ratio
                        comboLegs[i].action = action

                res = Contract()

                res.symbol      = instr.symbol
                res.secType     = "BAG"
                res.currency    = "USD"
                res.exchange    = instr.exchange
                res.comboLegs   = comboLegs

                res.comboLegs = comboLegs
            
            except KeyError:

                print(f"{contract_id} not found")

            pass

        return res


    def open_l1_stream(self, contract: Contract):
        
        handle = self.reqMktData(
                    {
                        "contract":             contract,
                        "genericTickList":      "",
                        "snapshot":             False,
                        "regulatorySnapshot":   False,
                        "mktDataOptions":       []
                    }
                )

        return handle


    def close_l1_stream(self, reqId: int):

        self.cancelMktData({ "reqId": reqId })


    def open_l2_stream(self, contract: Contract):

        pass


    def close_l2_stream(self, reqId: int):

        pass


    ###########################
    ## CONCURRENCY FUNCTIONS ##
    ###########################

    # do not call EClient methods directly, instead
    # schedule them SLEEP ms apart

    # not sure why this is breaking

    def schedule(self, func, kwargs):

        '''
        now         = self.loop.time()
        next_exec   = max(now, self.last_exec + SLEEP)

        f = partial(func, **kwargs)

        self.loop.call_at(next_exec, f)
        self.loop.call_at(now + 10, self.hello)

        self.last_exec = next_exec
        '''

        sleep(SLEEP)

        func(**kwargs)


    # for synchronizing with EWrapper

    def get_future(self, reqId, params = None):

        fut = self.loop.create_future()

        self.results[reqId] = {
            "fut":      fut,
            "params":   params,
            "res":      []
        }

        return fut

    
    def get_last_exec(self):                return self.last_exec
    def get_loop(self):                     return self.loop
    def get_market_data_queue(self):        return self.market_data_queue
    def get_open_data_lines(self):          return self.open_data_lines
    def get_results(self):                  return self.results

    def set_last_exec(self, time):          self.last_exec          = time
    def set_loop(self, loop):               self.loop               = loop
    def set_market_data_queue(self, queue): self.queue              = queue
    def set_open_data_lines(self, lines):   self.open_data_lines    = lines
    def set_results(self, results):         self.results            = results