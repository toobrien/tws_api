

async function main() {

    const lwc = window.LightweightCharts;

    const server_url    = `http://${hostname}:${port}`;

    let res     = await fetch(`${server_url}/get_quotes`);
    let quotes  = await res.json();
    
    const symbols       = [];
    const charts        = {};
    const series        = {};
    const series_idx    = [];
    const view          = document.getElementById("view");

    let chart_opts = {
        width:  chart_width,
        height: chart_height,
        crosshair: {
            mode: 0
        },
        watermark: {
            visible:    true,
            fontSize:   12,
            horzAlign:  "left",
            vertAlign:  "top",
            color:      "rgba(88, 88, 88, 0.5)",
            text:       null
        },
        timeScale: {
            tickMarkFormatter: (time, tickMarkFormatter, locale) => series_idx[time]
        },
        localization: {
            timeFormatter: (time, tickMarkFormatter, locale) => series_idx[time]
        }
    };

    var i = 0;

    for (const [ term_id, quote ] of Object.entries(quotes)) {

        const symbol    = term_id.split(":")[0];
        let   chart     = null;

        if (!symbols.includes(symbol)) {

            symbols.push(symbol);

            const chart_container = document.createElement("div");
            
            chart_container.id = `${symbol}_chart_container`;
            
            view.appendChild(chart_container);

            chart           = lwc.createChart(chart_container);
            charts[symbol]  = chart;
            
            chart_opts.watermark.text = symbol;

            chart.applyOptions(chart_opts);

            /*
            const zero_series = chart.addLineSeries();

            zero_series.createPriceLine(
                {
                    price: 0.0000,
                    color: "#FF0000",
                    lineWidth: 1,
                    lineStyle: lwc.LineStyle.Dashed,
                    lastValueVisible: false,
                    priceFormat: {
                        type:       "price",
                        precision:  4,
                        minMove:    0.0001
                    }
                }
            );
            */

        }

        chart = charts[symbol];

        const bid_series_opts = {
            upColor:            "#1984c5",
            downColor:          "#1984c5",
            priceLineVisible:   false,
            lastValueVisible:   false,
            priceFormat: {
                type:       "price",
                precision:  4,
                minMove:    0.0001
            }
        };

        const ask_series_opts = {
            upColor:            "#c23728",
            downColor:          "#c23728",
            priceLineVisible:   false,
            lastValueVisible:   false,
            priceFormat: {
                type:       "price",
                precision:  4,
                minMove:    0.0001
            }
        };

        const last_series_opts = {
            upColor:            "#000000",
            downColor:          "#000000",
            priceLineVisible:   false,
            lastValueVisible:   false,
            priceFormat: {
                type:       "price",
                precision:  4,
                minMove:    0.0001
            }
        };

        const high_bid_series_opts  = {
            upColor:            "#a7d5ed",
            downColor:          "#a7d5ed",
            priceLineVisible:   false,
            lastValueVisible:   false,
            priceFormat: {
                type:       "price",
                precision:  4,
                minMove:    0.0001
            }
        };

        const low_ask_series_opts = {
            upColor:            "#e1a692",
            downColor:          "#e1a692",
            priceLineVisible:   false,
            lastValueVisible:   false,
            priceFormat: {
                type:       "price",
                precision:  4,
                minMove:    0.0001
            }
        }; 

        series[term_id] = {
            bid_series:         chart.addBarSeries(bid_series_opts),
            ask_series:         chart.addBarSeries(ask_series_opts),
            last_series:        chart.addBarSeries(last_series_opts),
            high_bid_series:    chart.addBarSeries(high_bid_series_opts),
            low_ask_series:     chart.addBarSeries(low_ask_series_opts)
        };

        bid         = quote["BID"];
        ask         = quote["ASK"];
        last        = quote["LAST"];
        high_bid    = quote["high_bid"];
        low_ask     = quote["low_ask"];

        series[term_id].bid_series.setData([ { time: i, open: bid, high: bid, low: bid, close: bid } ]);
        series[term_id].ask_series.setData([ { time: i, open: ask, high: ask, low: ask, close: ask } ]);
        series[term_id].last_series.setData([ { time: i, open: last, high: last, low: last, close: last } ]);
        series[term_id].high_bid_series.setData([ { time: i, open: high_bid, high: high_bid, low: high_bid, close: high_bid } ]);
        series[term_id].low_ask_series.setData([ { time: i, open: low_ask, high: low_ask, low: low_ask, close: low_ask } ]);

        series_idx[i] = term_id;

        i++;

    }

    async function update_charts() {

        let res     = await fetch(`${server_url}/get_quotes`);
        let quotes  = await res.json();

        var i = 0;

        for (const [ term_id, quote ] of Object.entries(quotes)) {

            bid         = quote["BID"];
            ask         = quote["ASK"];
            last        = quote["LAST"];
            high_bid    = quote["HIGH_BID"];
            low_ask     = quote["LOW_ASK"];

            if (!last) last = (quote["BID"] + quote["ASK"]) / 2;

            series[term_id].bid_series.update({ time: i, open: bid, high: bid, low: bid, close: bid });
            series[term_id].ask_series.update({ time: i, open: ask, high: ask, low: ask, close: ask });
            series[term_id].last_series.update({ time: i, open: last, high: last, low: last, close: last });
            series[term_id].high_bid_series.update({ time: i, open: high_bid, high: high_bid, low: high_bid, close: high_bid });
            series[term_id].low_ask_series.update({ time: i, open: low_ask, high: low_ask, low: low_ask, close: low_ask });
        
            i++;

        }

    }
    
    setInterval(update_charts, update_ms);

}