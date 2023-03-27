

QUOTE_DEFS = [
    {
        "instrument_id":    ( "RB", "NYMEX", "single", "K23" ),
        "max_fills":        1,
        "qty":              1,
        "duration":         10,
        "action":           "BUY",
        "time_in_force":    "GTD",
        "entry":            -0.0040,
        "enabled":          True,
        "max_worsening":    0.0020,
        "profit_taker_amt": 0.0040,
        "stop_loss_amt":    -0.080
    },
    {
        "instrument_id":    ( "RB", "NYMEX", "single", "K23" ),
        "max_fills":        1,
        "qty":              1,
        "duration":         10,
        "action":           "SELL",
        "time_in_force":    "GTD",
        "entry":            0.0050,
        "enabled":          False,
        "max_worsening":    -0.0025,
        "profit_taker_amt": -0.0040,
        "stop_loss_amt":    0.0080
    },
]
