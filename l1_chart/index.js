
async function main() {

    const lwc = window.LightweightCharts;

    const handle_to_chart_data  = {};
    const server_url            = `http://${hostname}:${port}`;
    
    let res = await fetch(`${server_url}/get_instruments`);
    res     = await res.json();
    
    const chart_display = document.getElementById("chart_display");
    const charts        = {};
    
    for (const [ instrument, handle ] of Object.entries(res)) {
    
        const chart_container = document.createElement("div");
    
        chart_container.id = handle;

        chart_container.onclick = (e) => { 
            
            const selected_handle   = parseInt(e.currentTarget.id);
            const selected_chart    = charts[selected_handle];
            const ts                = selected_chart.timeScale();
            const rng               = ts.getVisibleLogicalRange();

            for (const [ handle, chart ] of Object.entries(charts))

                chart.timeScale().setVisibleLogicalRange(rng);

        };

        const chart = lwc.createChart(chart_container);

        charts[handle] = chart;
    
        let friendly_name_parts = instrument.substring(1, instrument.length - 1).replaceAll("'", "").split(", ");
        let symbol              = friendly_name_parts[0];
        let year                = friendly_name_parts[3].substring(1);
        let type                = friendly_name_parts[2];
        let months              = "";

        for (let i = 3; i < friendly_name_parts.length; i++)

            months += friendly_name_parts[i][0];

        friendly_name = `${symbol} ${type} ${months} ${year}`;

        chart.applyOptions(
            {
                crosshair: {
                    mode: 0
                },
                width:        chart_width,
                height:       chart_height,   
                watermark: {
                    visible:    true,
                    fontSize:   12,
                    horzAlign:  "left",
                    vertAlign:  "top",
                    color:      "rgba(88, 88, 88, 0.5)",
                    text:       friendly_name
                },
                timeScale: {
                    timeVisible: true,
                    secondsVisible: true,
                }
            }
        );
    
        chart_display.appendChild(chart_container);
    
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
        }
    
        const bid_series    = chart.addBarSeries(bid_series_opts);
        const ask_series    = chart.addBarSeries(ask_series_opts);
        const last_series   = chart.addBarSeries(last_series_opts);

        const chart_data = {
            "chart_obj":    chart,
            "bid_series":   bid_series,
            "ask_series":   ask_series,
            "last_series":  last_series,
            "bid_data":     [],
            "ask_data":     [],
            "last_data":    []
        };
    
        bid_series.setData(chart_data["bid_data"]);
        ask_series.setData(chart_data["ask_data"]);
        last_series.setData(chart_data["last_data"]);

        handle_to_chart_data[handle] = chart_data

    }
    
    async function update_charts() {
    
        let res = await fetch(`${server_url}/get_quotes`);
        res     = await res.json();
    
        const ts = Math.floor(Date.now() / 1000) + utc_offset;
    
        for (const [ handle, quote_data ] of Object.entries(res)) {
    
            const chart_data = handle_to_chart_data[handle];
    
            let bid_series  = chart_data["bid_series"];
            let ask_series  = chart_data["ask_series"];
            let last_series = chart_data["last_series"];
    
            if (chart_data["bid_series"].length > max_samples) {
    
                const chart = chart_data["chart_obj"];
    
                const bid_data  = bid_series.slice(cull_samples, bid_series.length);
                const ask_data  = ask_series.slice(cull_samples, ask_series.length);
                const last_data = last_series.slice(cull_samples, last_series.length);

                chart_data["bid_data"]  = bid_data
                chart_data["ask_data"]  = ask_data 
                chart_data["last_data"] = last_data
    
                bid_series.setData(bid_data);
                ask_series.setData(ask_data);
                last_series.setData(last_data);
    
            }
    
            const bid_val   = quote_data["BID"];
            const ask_val   = quote_data["ASK"];
            const last_val  = quote_data["LAST"];

            if (bid_val) bid_series.update({ time: ts, open: bid_val, high: bid_val, low: bid_val, close: bid_val });

            if (ask_val)  ask_series.update({ time: ts, open: ask_val, high: ask_val, low: ask_val, close: ask_val });

            if (last_val) last_series.update({ time: ts, open: last_val, high: last_val, low: last_val, close: last_val });
    
        }
    
    }
    
    setInterval(update_charts, update_ms);

}