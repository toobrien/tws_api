

QUOTE_DEFS = {
    ( "RB", "NYMEX", "single", "J23" ): {
        "max_fills":        1,
        "multiplier":       0.0001,
        "update_interval":  5,
        "quote_params":     [
            {
                "side":             "bid",
                "relative_to":      "best",
                "entry":            -500,
                "tp":               50,
                "sl":               100,
                "sl_delay":         10,
            }
        ]
    }
}