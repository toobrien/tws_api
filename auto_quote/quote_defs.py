

QUOTE_DEFS = [
    {
        "instrument_id":    ( "RB", "NYMEX", "single", "J23" ),
        "max_fills":        1,
        "qty":              1,
        "duration":         3,
        "action":           "BUY",
        "entry":            -0.0500,
        "enabled":          True,
        "max_worsening":    0.0025,
        "profit_taker_amt": 0.0050,
        "stop_loss_amt":    0.0050,
    },
    {
        "instrument_id":    ( "RB", "NYMEX", "single", "J23" ),
        "max_fills":        1,
        "qty":              1,
        "duration":         3,
        "action":           "SELL",
        "entry":            0.0500,
        "enabled":          False,
        "max_worsening":    -0.0025,
        "profit_taker_amt": -0.0050,
        "stop_loss_amt":    0.0050
    },
]
