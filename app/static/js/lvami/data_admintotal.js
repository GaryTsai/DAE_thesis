function multiple_sum_of_electricity(chartData, meter) {
  var chart = AmCharts.makeChart("admincharttotal", {
    "type": "serial",
    "theme": "light",
    "dataProvider": chartData,
    "valueAxes": [{
      "stackType": "regular",
      "gridColor": "#FFFFFF",
      "gridAlpha": 0.2,
      "dashLength": 0,
      "guides": [{
        "above": true,
        "boldLabel": true,
        "dashLength": 6,
        "inside": true,
        "lineColor": "#CC0000",
        "lineThickness": 2,
        "lineAlpha": 0.8,
        "value": meter
      }],
    }],
    "gridAboveGraphs": true,
    "startDuration": 1,
    "graphs": [{
        "balloonText": "[[category]]: 晚間用量<b>[[value]]</b>kWh",
        "fillAlphas": 0.8,
        "lineAlpha": 0.2,
        "type": "column",
        "valueField": "max_power_morning",
        "urlField": "url",
        "showHandOnHover": true

      }, {
        "balloonText": "[[category]]: 白天用量<b>[[value]]</b>kWh<br>",
        "fillAlphas": 0.8,
        "lineAlpha": 0.2,
        "type": "column",
        "valueField": "max_power_night",
        "showHandOnHover": true,
        "bulletSize": 42,
           "bulletOffset": 10,
        "customBulletField": "bullet"
      }
    ],
    "chartCursor": {
      "categoryBalloonEnabled": false,
      "cursorAlpha": 0,
      "zoomable": false
    },
    "categoryField": "account",
    "categoryAxis": {
      "gridPosition": "start",
      "gridAlpha": 0,
      "tickPosition": "start",
      "tickLength": 20
    },
    "export": {
      "enabled": true
    },
    "listeners": [{
      "event": "clickGraphItem",
      "method": function (event) {
        var user_ID = event.item.category;

        $('#admincharttotal').hide();
        $('#back_to_power').show();
        $('#adminchartft').show();
        $('#question_of_admin').hide();
        $.ajax({
          type: "GET",
          url: "/api/v1.0/data_ten_users",
          dataType: 'json',
          data: {
            "CustomerID": $('#user_id').text()
            // "DateFrom": localStorage["start_time"],
            // "DateTo": localStorage["end_time"]
          },
          success: function (response) {
            console.log(user_ID)
            //multiple_sum_of_electricity(response);
            if (user_ID.toLowerCase() == "d00001")
              multiple_realtime_1(response);
            else if (user_ID.toLowerCase() == "d00002")
              multiple_realtime_2(response);
            else if (user_ID.toLowerCase() == "d00003")
              multiple_realtime_3(response);
            else if (user_ID.toLowerCase() == "d00004")
              multiple_realtime_4(response);
            else if (user_ID.toLowerCase() == "d00005")
              multiple_realtime_5(response);
            else if (user_ID.toLowerCase() == "d00006")
              multiple_realtime_6(response);
            else if (user_ID.toLowerCase() == "d00007")
              multiple_realtime_7(response);
            else if (user_ID.toLowerCase() == "d00008")
              multiple_realtime_8(response);
            else if (user_ID.toLowerCase() == "d00009")
              multiple_realtime_9(response);
            else if (user_ID.toLowerCase() == "d00010")
              multiple_realtime_10(response);
          },
          error: function (response) {
            sweetAlert('LVAMI 資料讀取失敗');
          }
        });
      }
    }]
  });
}
function multiple_realtime_1(chartData) {
  var chart = AmCharts.makeChart("adminchartft", {
    "type": "serial",
    "theme": "light",
    "titles": [{
      "text": "多用戶的即時用電比較 ",
      "size": 20
    }],
    "dataProvider": chartData, //YYYY MMM DD,JJ:NN:SS
    "legend": {
      "position": "right",
      "equalWidths": false,

      "valueAlign": "left",
      "valueText": "[[value]]",
      "valueWidth": 100
    },

    "valueAxes": [{
      "id": "g1",
      "position": "left",
      "title": "用電度數(kWh)",
    }, ],
    "balloon": {
      "maxWidth": 300
    },
    "graphs": [{
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00001",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00001",
      "legendValueText": "[[value]] kWh",
      "hidden": false
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00002",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00002",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00003",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00003",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00004",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00004",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00005",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00005",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00006",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00006",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00007",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00007",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00008",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00008",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00009",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00009",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00010",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00010",
      "legendValueText": "[[value]] kWh",
      "hidden": true
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
      "minPeriod": "ss",
      "parseDates": true
    },
  });
  chart.addListener("rendered", zoomChart);
  zoomChart();

  // this method is called when chart is first inited as we listen for "rendered" event
  function zoomChart() {
    // different zoom methods can be used - zoomToIndexes, zoomToDates, zoomToCategoryValues
    chart.zoomToIndexes((chartData.length - 288), (chartData.length - 1));
  }

}

function multiple_realtime_2(chartData) {
  var chart = AmCharts.makeChart("adminchartft", {
    "type": "serial",
    "theme": "light",
    "titles": [{
      "text": "多用戶的即時用電比較 ",
      "size": 20
    }],
    "dataProvider": chartData, //YYYY MMM DD,JJ:NN:SS
    "legend": {
      "position": "right",
      "equalWidths": false,

      "valueAlign": "left",
      "valueText": "[[value]]",
      "valueWidth": 100
    },

    "valueAxes": [{
      "id": "g1",
      "position": "left",
      "title": "用電度數(kWh)",
    }, ],
    "balloon": {
      "maxWidth": 300
    },
    "graphs": [{
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00001",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00001",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00002",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00002",
      "legendValueText": "[[value]] kWh",
      "hidden": false
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00003",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00003",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00004",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00004",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00005",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00005",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00006",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00006",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00007",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00007",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00008",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00008",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00009",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00009",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00010",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00010",
      "legendValueText": "[[value]] kWh",
      "hidden": true
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
      "minPeriod": "ss",
      "parseDates": true
    },
  });
  chart.addListener("rendered", zoomChart);
  zoomChart();

  // this method is called when chart is first inited as we listen for "rendered" event
  function zoomChart() {
    // different zoom methods can be used - zoomToIndexes, zoomToDates, zoomToCategoryValues
    chart.zoomToIndexes((chartData.length - 288), (chartData.length - 1));
  }
}

function multiple_realtime_3(chartData) {
  var chart = AmCharts.makeChart("adminchartft", {
    "type": "serial",
    "theme": "light",
    "titles": [{
      "text": "多用戶的即時用電比較 ",
      "size": 20
    }],
    "dataProvider": chartData, //YYYY MMM DD,JJ:NN:SS
    "legend": {
      "position": "right",
      "equalWidths": false,

      "valueAlign": "left",
      "valueText": "[[value]]",
      "valueWidth": 100
    },

    "valueAxes": [{
      "id": "g1",
      "position": "left",
      "title": "用電度數(kWh)",
    }, ],
    "balloon": {
      "maxWidth": 300
    },
    "graphs": [{
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00001",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00001",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00002",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00002",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00003",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00003",
      "legendValueText": "[[value]] kWh",
      "hidden": false
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00004",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00004",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00005",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00005",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00006",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00006",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00007",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00007",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00008",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00008",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00009",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00009",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00010",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00010",
      "legendValueText": "[[value]] kWh",
      "hidden": true
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
      "minPeriod": "ss",
      "parseDates": true
    },
  });
  chart.addListener("rendered", zoomChart);
  zoomChart();

  // this method is called when chart is first inited as we listen for "rendered" event
  function zoomChart() {
    // different zoom methods can be used - zoomToIndexes, zoomToDates, zoomToCategoryValues
    chart.zoomToIndexes((chartData.length - 288), (chartData.length - 1));
  }

}

function multiple_realtime_4(chartData) {
  var chart = AmCharts.makeChart("adminchartft", {
    "type": "serial",
    "theme": "light",
    "titles": [{
      "text": "多用戶的即時用電比較 ",
      "size": 20
    }],
    "dataProvider": chartData, //YYYY MMM DD,JJ:NN:SS
    "legend": {
      "position": "right",
      "equalWidths": false,

      "valueAlign": "left",
      "valueText": "[[value]]",
      "valueWidth": 100
    },

    "valueAxes": [{
      "id": "g1",
      "position": "left",
      "title": "用電度數(kWh)",
    }, ],
    "balloon": {
      "maxWidth": 300
    },
    "graphs": [{
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00001",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00001",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00002",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00002",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00003",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00003",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00004",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00004",
      "legendValueText": "[[value]] kWh",
      "hidden": false
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00005",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00005",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00006",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00006",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00007",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00007",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00008",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00008",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00009",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00009",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00010",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00010",
      "legendValueText": "[[value]] kWh",
      "hidden": true
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
      "minPeriod": "ss",
      "parseDates": true
    },
  });
  chart.addListener("rendered", zoomChart);
  zoomChart();

  // this method is called when chart is first inited as we listen for "rendered" event
  function zoomChart() {
    // different zoom methods can be used - zoomToIndexes, zoomToDates, zoomToCategoryValues
    chart.zoomToIndexes((chartData.length - 288), (chartData.length - 1));
  }
}

function multiple_realtime_5(chartData) {
  var chart = AmCharts.makeChart("adminchartft", {
    "type": "serial",
    "theme": "light",
    "titles": [{
      "text": "多用戶的即時用電比較 ",
      "size": 20
    }],
    "dataProvider": chartData, //YYYY MMM DD,JJ:NN:SS
    "legend": {
      "position": "right",
      "equalWidths": false,

      "valueAlign": "left",
      "valueText": "[[value]]",
      "valueWidth": 100
    },

    "valueAxes": [{
      "id": "g1",
      "position": "left",
      "title": "用電度數(kWh)",
    }, ],
    "balloon": {
      "maxWidth": 300
    },
    "graphs": [{
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00001",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00001",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00002",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00002",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00003",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00003",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00004",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00004",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00005",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00005",
      "legendValueText": "[[value]] kWh",
      "hidden": false
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00006",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00006",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00007",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00007",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00008",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00008",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00009",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00009",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00010",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00010",
      "legendValueText": "[[value]] kWh",
      "hidden": true
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
      "minPeriod": "ss",
      "parseDates": true
    },
  });
  chart.addListener("rendered", zoomChart);
  zoomChart();

  // this method is called when chart is first inited as we listen for "rendered" event
  function zoomChart() {
    // different zoom methods can be used - zoomToIndexes, zoomToDates, zoomToCategoryValues
    chart.zoomToIndexes((chartData.length - 288), (chartData.length - 1));
  }
}

function multiple_realtime_6(chartData) {
  var chart = AmCharts.makeChart("adminchartft", {
    "type": "serial",
    "theme": "light",
    "titles": [{
      "text": "多用戶的即時用電比較 ",
      "size": 20
    }],
    "dataProvider": chartData, //YYYY MMM DD,JJ:NN:SS
    "legend": {
      "position": "right",
      "equalWidths": false,

      "valueAlign": "left",
      "valueText": "[[value]]",
      "valueWidth": 100
    },

    "valueAxes": [{
      "id": "g1",
      "position": "left",
      "title": "用電度數(kWh)",
    }, ],
    "balloon": {
      "maxWidth": 300
    },
    "graphs": [{
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00001",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00001",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00002",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00002",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00003",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00003",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00004",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00004",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00005",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00005",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00006",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00006",
      "legendValueText": "[[value]] kWh",
      "hidden": false
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00007",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00007",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00008",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00008",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00009",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00009",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00010",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00010",
      "legendValueText": "[[value]] kWh",
      "hidden": true
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
      "minPeriod": "ss",
      "parseDates": true
    },
  });
  chart.addListener("rendered", zoomChart);
  zoomChart();

  // this method is called when chart is first inited as we listen for "rendered" event
  function zoomChart() {
    // different zoom methods can be used - zoomToIndexes, zoomToDates, zoomToCategoryValues
    chart.zoomToIndexes((chartData.length - 288), (chartData.length - 1));
  }
}

function multiple_realtime_7(chartData) {
  var chart = AmCharts.makeChart("adminchartft", {
    "type": "serial",
    "theme": "light",
    "titles": [{
      "text": "多用戶的即時用電比較 ",
      "size": 20
    }],
    "dataProvider": chartData, //YYYY MMM DD,JJ:NN:SS
    "legend": {
      "position": "right",
      "equalWidths": false,

      "valueAlign": "left",
      "valueText": "[[value]]",
      "valueWidth": 100
    },

    "valueAxes": [{
      "id": "g1",
      "position": "left",
      "title": "用電度數(kWh)",
    }, ],
    "balloon": {
      "maxWidth": 300
    },
    "graphs": [{
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00001",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00001",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00002",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00002",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00003",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00003",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00004",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00004",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00005",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00005",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00006",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00006",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00007",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00007",
      "legendValueText": "[[value]] kWh",
      "hidden": false
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00008",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00008",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00009",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00009",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00010",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00010",
      "legendValueText": "[[value]] kWh",
      "hidden": true
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
      "minPeriod": "ss",
      "parseDates": true
    },
  });
  chart.addListener("rendered", zoomChart);
  zoomChart();

  // this method is called when chart is first inited as we listen for "rendered" event
  function zoomChart() {
    // different zoom methods can be used - zoomToIndexes, zoomToDates, zoomToCategoryValues
    chart.zoomToIndexes((chartData.length - 288), (chartData.length - 1));
  }
}

function multiple_realtime_8(chartData) {
  var chart = AmCharts.makeChart("adminchartft", {
    "type": "serial",
    "theme": "light",
    "titles": [{
      "text": "多用戶的即時用電比較 ",
      "size": 20
    }],
    "dataProvider": chartData, //YYYY MMM DD,JJ:NN:SS
    "legend": {
      "position": "right",
      "equalWidths": false,

      "valueAlign": "left",
      "valueText": "[[value]]",
      "valueWidth": 100
    },

    "valueAxes": [{
      "id": "g1",
      "position": "left",
      "title": "用電度數(kWh)",
    }, ],
    "balloon": {
      "maxWidth": 300
    },
    "graphs": [{
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00001",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00001",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00002",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00002",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00003",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00003",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00004",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00004",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00005",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00005",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00006",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00006",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00007",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00007",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00008",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00008",
      "legendValueText": "[[value]] kWh",
      "hidden": false
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00009",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00009",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00010",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00010",
      "legendValueText": "[[value]] kWh",
      "hidden": true
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
      "minPeriod": "ss",
      "parseDates": true
    },
  });
  chart.addListener("rendered", zoomChart);
  zoomChart();

  // this method is called when chart is first inited as we listen for "rendered" event
  function zoomChart() {
    // different zoom methods can be used - zoomToIndexes, zoomToDates, zoomToCategoryValues
    chart.zoomToIndexes((chartData.length - 288), (chartData.length - 1));
  }
}

function multiple_realtime_9(chartData) {
  var chart = AmCharts.makeChart("adminchartft", {
    "type": "serial",
    "theme": "light",
    "titles": [{
      "text": "多用戶的即時用電比較 ",
      "size": 20
    }],
    "dataProvider": chartData, //YYYY MMM DD,JJ:NN:SS
    "legend": {
      "position": "right",
      "equalWidths": false,

      "valueAlign": "left",
      "valueText": "[[value]]",
      "valueWidth": 100
    },

    "valueAxes": [{
      "id": "g1",
      "position": "left",
      "title": "用電度數(kWh)",
    }, ],
    "balloon": {
      "maxWidth": 300
    },
    "graphs": [{
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00001",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00001",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00002",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00002",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00003",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00003",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00004",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00004",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00005",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00005",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00006",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00006",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00007",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00007",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00008",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00008",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00009",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00009",
      "legendValueText": "[[value]] kWh",
      "hidden": false
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00010",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00010",
      "legendValueText": "[[value]] kWh",
      "hidden": true
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
      "minPeriod": "ss",
      "parseDates": true
    },
  });
  chart.addListener("rendered", zoomChart);
  zoomChart();

  // this method is called when chart is first inited as we listen for "rendered" event
  function zoomChart() {
    // different zoom methods can be used - zoomToIndexes, zoomToDates, zoomToCategoryValues
    chart.zoomToIndexes((chartData.length - 288), (chartData.length - 1));
  }
}

function multiple_realtime_10(chartData) {
  var chart = AmCharts.makeChart("adminchartft", {
    "type": "serial",
    "theme": "light",
    "titles": [{
      "text": "多用戶的即時用電比較 ",
      "size": 20
    }],
    "dataProvider": chartData, //YYYY MMM DD,JJ:NN:SS
    "legend": {
      "position": "right",
      "equalWidths": false,

      "valueAlign": "left",
      "valueText": "[[value]]",
      "valueWidth": 100
    },

    "valueAxes": [{
      "id": "g1",
      "position": "left",
      "title": "用電度數(kWh)",
    }, ],
    "balloon": {
      "maxWidth": 300
    },
    "graphs": [{
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00001",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00001",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00002",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00002",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00003",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00003",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00004",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00004",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00005",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00005",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00006",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00006",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00007",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00007",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00008",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00008",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,

      "valueField": "d00009",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00009",
      "legendValueText": "[[value]] kWh",
      "hidden": true
    }, {
      "valueAxis": "g1",
      "bullet": "round",
      "balloonText": "<span style='font-size:12px; font-family:Microsoft JhengHei;'><b>時間：[[category]]</b>用電度數:[[value]]kWh</span>",
      "bulletBorderAlpha": 0.5,
      "bulletColor": "#FFFFFF",
      "hideBulletsCount": 50,
      "valueField": "d00010",
      "useLineColorForBulletBorder": true,
      "balloon": {
        "drop": false
      },
      "lineThickness": 1.5,
      "title": "d00010",
      "legendValueText": "[[value]] kWh",
      "hidden": false
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
      "minPeriod": "ss",
      "parseDates": true
    },
  });
  chart.addListener("rendered", zoomChart);
  zoomChart();

  // this method is called when chart is first inited as we listen for "rendered" event
  function zoomChart() {
    // different zoom methods can be used - zoomToIndexes, zoomToDates, zoomToCategoryValues
    chart.zoomToIndexes((chartData.length - 288), (chartData.length - 1));
  }
}