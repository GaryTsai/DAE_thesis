// 週平均
function week_avg(chartData) {
    var chart = AmCharts.makeChart("week_avg", {
        "type": "serial",
        "theme": "light",
        "valueAxes": [{
            "title": "用電度數(kWh)",
            "minimum": 0,
        }],
        "dataProvider": chartData,
        "startDuration": 1,
        "graphs": [{
            "valueAxis": "power_column",
            "alphaField": "alpha",
            "balloonText": "[[category]]: <b>[[value]]kWh</b>",
            "fillAlphas": 1,
            "title": "本月平均用電度數",
            "type": "column",
            "valueField": "value",
            "dashLengthField": "dashLengthColumn",
            "fillColorsField": "lineColor",
            "lineColorField": "lineColor",
        }, {
            "valueAxis": "week_value",
            "balloonText": "[[category]]: <b>[[value]]kWh</b>",
            "bullet": "round",
            "lineThickness": 3,
            "bulletSize": 7,
            "bulletBorderAlpha": 1,
            "bulletColor": "#FFFFFF",
            "useLineColorForBulletBorder": true,
            "bulletBorderThickness": 3,
            "fillAlphas": 0,
            "lineAlpha": 1,
            "title": "本週用電度數",
            "valueField": "week_now_value",
            "dashLengthField": "dashLengthLine"
        }],
        "categoryField": "time",
        "categoryAxis": {
            "gridPosition": "start",
            "axisAlpha": 0,
            "tickLength": 0
        },
        "legend": {
            "useGraphSettings": true
        }
    });
}
//用電累積度數折線圖
function power_of_accumulation(chartData, meter, year, month) {
    var d = new Date(year, month, 01);
    var n = parseInt(month) - 1;
    var chart = AmCharts.makeChart("total_and_body", {
        "type": "serial",
        "theme": "light",
        "dataProvider": chartData['demands'],
        //left axis
        "valueAxes": [{
            "id": "power",
            "position": "left",
            "title": "累積用電度數(kWh)",
            "guides": [{
                "above": true,
                "boldLabel": true,
                "dashLength": 6,
                "inside": true,
                "label": n + "月用電度數：" + meter + " kWh",
                'position': "right",
                "lineColor": "#CC0000",
                "lineThickness": 2,
                "lineAlpha": 1,
                'fontSize': 15,
                "value": meter
            }],
            "maximum": (meter + chartData['power_of_expense'][0]['max_powernumber']),
            //  "gridThickness": 0,

        }, ],
        //DRAW THE DIAGRAM, while how th draw is set in amchart site, we can't see it
        //"title" affect below small name, "valueField" directly affect graph data
        "graphs": [{
            'id': 'power',
            "markerType": "none",
            "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b><br>累積用電:[[value]]kWh</span>",
            "lineThickness": 5,
            // "title": "累積用電度數",
            "valueField": "value",
            "valueAxis": "power",
            "lineColorField": "lineColor",
            "fillAlphas": 0.5,
            "fillColorsField": "lineColor",
            "gridThickness": 5,
            "legendValueText": " 累積用電度數 [[value]]kWh",
        }, ],
        "plotAreaBorderAlpha": 0,
        "autoMargins": true,
        "chartScrollbar": {
            "autoGridCount": true,
            "graph": "time",
            "scrollbarHeight": 25,
            "color": "#000000"
        },
        "chartCursor": {
            "cursorAlpha": 0,
            "zoomable": true,
            "categoryBalloonDateFormat": "YYYY MMM DD,JJ:NN:SS",
        },
        // buttom axis
        "categoryField": "time",
        "categoryAxis": {
            "minPeriod": "ss", //
            "parseDates": true,
            // "gridThickness": 0
        },
        "legend": {
            "useGraphSettings": true
        }
    });
}
//體感、用電度數百分比圖
function apparent_temperature_compare_with_power(data) {
    var chart = AmCharts.makeChart("column", {
        "type": "serial",
        "theme": "light",

        "dataProvider": data,
        "valueAxes": [{
                "id": "avg_power",
                "position": "left",
                // "minorGridAlpha": 0,
                // "minorGridEnabled": false,
                "position": "top",
                "axisAlpha": 0,

                "title": "平均用電度數(kWh)/小時"
            },
            {
                "id": "tempature_time",
                // "minorGridAlpha": 0.08,
                // "minorGridEnabled": true,
                "position": "left",
                "axisAlpha": 0,

                "title": "小時/天"
            }
        ],
        "valueAxis": {
            "gridAlpha": 0
        },
        "startDuration": 1,
        "graphs": [{
            // "id": "tempature_time",
            "balloonText": "<span style='font-size:13px;'>該溫度區間時間:<b>[[value]]小時/天</b></span>",
            "title": "該溫度區間時間",
            "type": "column",
            "fillAlphas": 0.8,
            "valueAxis": "tempature_time",
            "valueField": "count"
        }, {
            // "id": "avg_power",
            "balloonText": "<span style='font-size:13px;'>平均用電度數:<b>[[value]]kWh/小時</b></span>",
            "bullet": "round",
            "bulletBorderAlpha": 1,
            "bulletColor": "#FFFFFF",
            "useLineColorForBulletBorder": true,
            "fillAlphas": 0,
            "lineThickness": 2,
            "lineAlpha": 1,
            "bulletSize": 7,
            "title": "平均用電度數(kWh)/小時",
            "valueField": "value",
            "valueAxis": "avg_power"
        }],
        "chartCursor": {
            "showBalloon": false
        },
        "categoryField": "region",
        "categoryAxis": {
            "gridPosition": "start",
            // "labelRotation": 30
            "title": "溫度區間(°C)",

        },
        "export": {
            "enabled": true
        }

    });
}
//當月歷史用電
function history_power_chart(chartData) {
    var chart = AmCharts.makeChart("total_dia", {
        "type": "serial",

        "theme": "light",
        "dataProvider": chartData['demands'],

        "valueAxes": [{
            "id": "g1",
            "position": "left",
            "title": "用電度數(kWh)",
            "minimum": 0,
        }, ],

        "graphs": [{
            "valueAxis": "g1",
            "bullet": "round",
            "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b><br>用電度數:[[value]]kWh</span>",
            "bulletBorderAlpha": 0.5,
            "bulletColor": "#FFFFFF",
            "hideBulletsCount": 150,
            "marginRight": 80,
            "autoMarginOffset": 20,
            "valueField": "value",
            "useLineColorForBulletBorder": true,
            "balloon": {
                "drop": false
            },
            "lineThickness": 1.5,
            "title": "即時用電度數",
            "lineColor": "#ff0000",
            // "legendValueText": "[[value]] kWh",
        }, ],

        //效果設定
        "chartScrollbar": {
            "autoGridCount": true,
            "graph": "temperatureAxis",
            "scrollbarHeight": 25,
            "color": "#000000"
        },
        "chartCursor": {
            "limitToGraph": "temperatureAxis",
            "categoryBalloonEnabled": false,
            "categoryBalloonDateFormat": "YYYY MMM DD,JJ:NN:SS",
            "cursorPosition": "mouse"
        },
        "categoryField": "time",
        "categoryAxis": {
            "minPeriod": "ss", //
            "parseDates": true,

        },
        "legend": {
            "useGraphSettings": true

        }
    });
    chart.addListener("rendered", zoomChart);
    zoomChart();

    // this method is called when chart is first inited as we listen for "rendered" event
    function zoomChart() {
        // different zoom methods can be used - zoomToIndexes, zoomToDates, zoomToCategoryValues
        chart.zoomToIndexes((chartData["demands"][chartData["demands"].length - 2]['time_count'] - 48), (chartData["demands"][chartData["demands"].length - 2]['time_count'] + 24));
    }

}
//日平均
function day_avg_diagram(chartData) {

    var chart = AmCharts.makeChart("day_avg", {
        "type": "serial",
        "theme": "light",
        "dataProvider": chartData,
        "valueAxes": [{
            "id": "g1",
            "position": "left",
            "title": "用電度數(kWh)",
            "minimum": 0,
            // "maximum": 2,
        }],
        // "mouseWheelZoomEnabled": true,
        "graphs": [{
            "valueAxis": "g1",
            "bullet": "round",
            "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b><br>日平均用電度數:[[value]]kWh</span>",
            "bulletBorderAlpha": 0.5,
            "bulletColor": "#FFFFFF",
            "hideBulletsCount": 50,

            "valueField": "value",
            "useLineColorForBulletBorder": true,
            "balloon": {
                "drop": false
            },
            "lineThickness": 1.5,
            "title": "本月平均用電度數",
            "lineColor": "#797575",
            // "legendValueText": "[[value]] kWh",


        }, {
            "valueAxis": "real_time_value",
            "bullet": "round",
            "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b><br>即時用電度數:[[value]]kWh</span>",
            "bulletBorderAlpha": 0.5,
            "bulletColor": "#FF8888",
            "hideBulletsCount": 50,

            "valueField": "real_time",
            "useLineColorForBulletBorder": true,
            "balloon": {
                "drop": false
            },
            "lineThickness": 1.5,
            "title": "即時用電度數",
            "lineColor": "#ff0000",
            // "legendValueText": "[[value]] kWh",
        }],
        "chartCursor": {
            "limitToGraph": "temperatureAxis",
            "categoryBalloonEnabled": false,
            "categoryBalloonDateFormat": "JJ:NN",
            "cursorPosition": "mouse"
        },
        "categoryField": "time",
        "categoryAxis": {
            "Period": "mm",
            "format": "JJ:NN",
        },
        "legend": {
            "useGraphSettings": true
        }
    });
}
//用戶平均比例比較圖
function local_compare_gauge_percent(user_total_power, local_averagepower) {
    var chart = AmCharts.makeChart("percent", {
        "theme": "light",
        "type": "gauge",
        "axes": [{
            "topTextFontSize": 20,
            "topTextYOffset": 70,
            "axisColor": "#31d6ea",
            "axisThickness": 1,
            "endValue": 200,
            "gridInside": true,
            "inside": true,
            "radius": "50%",
            "valueInterval": 50,
            "tickColor": "#67b7dc",
            "startAngle": -90,
            "endAngle": 90,
            "unit": "%",
            "bandOutlineAlpha": 0,
            "bands": [{
                "color": "#3cd3a3",
                "endValue": 200,
                "innerRadius": "105%",
                "radius": "170%",
                "gradientRatio": [0.5, 0, -0.5],
                "startValue": 0
            }, {
                "color": "#ff0000",
                "endValue": 0,
                "innerRadius": "105%",
                "radius": "170%",
                "gradientRatio": [0.5, 0, -0.5],
                "startValue": 0
            }]
        }],
        "arrows": [{
            "alpha": 1,
            "innerRadius": "35%",
            "nailRadius": 0,
            "radius": "170%"
        }]
    });
    setInterval(randomValue, 3000);
    // set random value
    function randomValue() {
        temp = ((user_total_power * 100) / local_averagepower);
        chart.arrows[0].setValue(temp);
        chart.axes[0].setTopText(temp.toFixed(2) + " %");
        // adjust darker band to new value
        chart.axes[0].bands[1].setEndValue(temp);
    }
}
// 體感用電比較圖
function tempature_correlation(trmpature_correlation) {
    var chart = AmCharts.makeChart("tempature_correlation", {
        "theme": "light",
        "type": "gauge",
        "axes": [{
            "topTextFontSize": 20,
            "topTextYOffset": 70,
            "axisColor": "#31d6ea",
            "axisThickness": 1,
            "endValue": 100,
            "gridInside": true,
            "inside": true,
            "radius": "50%",
            "valueInterval": 10,
            "tickColor": "#67b7dc",
            "startAngle": -90,
            "endAngle": 90,
            "unit": "",
            "startValue": 0,
            "bandOutlineAlpha": 0,
            "bands": [{
                "color": "#ff0000",
                "endValue": 100,
                "innerRadius": "105%",
                "radius": "170%",
                "gradientRatio": [0.5, 0, -0.5],
                "startValue": 0
            }, {
                "color": "#0080ff",
                "endValue": 0,
                "innerRadius": "105%",
                "radius": "170%",
                "gradientRatio": [0.5, 0, -0.5],
                "startValue": 0
            }]
        }],
        "arrows": [{
            "alpha": 1,
            "innerRadius": "35%",
            "nailRadius": 0,
            "radius": "170%"
        }]
    });

    setInterval(randomValue, 2000);

    // set random value
    function randomValue() {

        chart.arrows[0].setValue(trmpature_correlation);
        chart.axes[0].setTopText(trmpature_correlation);
        // adjust darker band to new value
        chart.axes[0].bands[1].setEndValue(trmpature_correlation);
    }
}