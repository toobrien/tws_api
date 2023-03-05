

async function main() {

    const lwc = window.LightWeightCharts;

    const server_url    = `http://${hostname}:${port}`;

    let res     = await fetch(`${server_url}/get_quotes`);
    let quotes  = await res.json();
    
    const symbols       = [];
    const charts        = {};
    const series        = {};
    const time_labels   = {};
    const view          = document.getElementById("view");

    let chart_opts = {
        width:  chart_width,
        height: chart_height,
        watermark: {
            visible:    true,
            fontSize:   12,
            horzAlign:  "left",
            vertAlign:  "top",
            color:      "rgba(88, 88, 88, 0.5)",
            text:       null
        },
        timeScale: {
            tickMarkFormatter: (time, tickMarkType, local) => time_labels[time]
        },
        localization: {
            timeFormatter: (time, tickMarkType, local) => time_labels[time]
        }
    };

    for (var [ term_id, quote ] of Object.keys(quotes)) {

        const symbol    = term_id.split()[0];
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

        }

        chart = charts[symbol];

        const bid_series_opts = {
            upColor:            "#0000FF",
            downColor:          "#0000FF",
            priceLineVisible:   false,
            priceFormat: {
                type:       "price",
                precision:  4,
                minMove:    0.0001
            }
        };

        const ask_series_opts = {
            upColor:            "#FF0000",
            downColor:          "#FF0000",
            priceLineVisible:   false,
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
            priceFormat: {
                type:       "price",
                precision:  4,
                minMove:    0.0001
            }
        };

        const high_bid_series_opts  = {
            upColor:            "#FF00FF",
            downColor:          "#FF00FF",
            priceLineVisible:   false,
            priceFormat: {
                type:       "price",
                precision:  4,
                minMove:    0.0001
            }
        };

        const low_ask_series_opts = {
            upColor:            "#FF00FF",
            downColor:          "#FF00FF",
            priceLineVisible:   false,
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

        series["term_id"]["bid_series"].setData([ { time: term_id, open: bid, high: bid, low: bid, close: bid } ]);
        series["term_id"]["ask_series"].setData([ { time: term_id, open: ask, high: ask, low: ask, close: ask } ]);
        series["term_id"]["last_series"].setData([ { time: term_id, open: last, high: last, low: last, close: last } ]);
        series["term_id"]["high_bid_series"].setData([ { time: term_id, open: high_bid, high: high_bid, low: high_bid, close: high_bid } ]);
        series["term_id"]["low_ask_series"].setData([ { time: term_id, open: low_ask, high: low_ask, low: low_ask, close: low_ask } ]);

    }

    async function update_charts() {

        let res     = await fetch(`${server_url}/get_quotes`);
        let quotes  = await res.json();

        for (var [ term_id, quote ] of Object.keys(quotes)) {

            bid         = quote["BID"];
            ask         = quote["ASK"];
            last        = quote["LAST"];
            high_bid    = quote["high_bid"];
            low_ask     = quote["low_ask"];

            series[term_id][bid_series].update({ time: term_id, open: bid, high: bid, low: bid, close: bid });
            series[term_id][ask_series].update({ time: term_id, open: ask, high: ask, low: ask, close: ask });
            series[term_id][last_series].update({ time: term_id, open: last, high: last, low: last, close: last });
            series[term_id][high_bid_series].update({ time: term_id, open: high_bid, high: high_bid, low: high_bid, close: high_bid });
            series[term_id][low_ask_series].update({ time: term_id, open: low_ask, high: low_ask, low: low_ask, close: low_ask });
        
            // necessary to keep x-axis labelled properly, for some reason...

            const symbol = term_id.split(":")[0];

            chart_opts.watermark.text = symbol;

            chart.applyOptions(chart_opts);
            chart.timeScale().fitContent();
        }

    }
    
    setInterval(update_charts, update_ms);

}