 $(document).ready(function () {
     // draw the tempature_correlation dashboard
     $.ajax({
         type: "GET",
         url: "/api/v1.0/temperature_correlation",
         dataType: 'json',
         data: {
             "CustomerID": $('#user_id').text()
         },
         success: function (response) {
             tempature_correlation(response)
         },
         error: function (response) {
             sweetAlert('tempature_correlation 資料讀取失敗');
         }
     });
     //get value of current temperature and apparent temperature and avaerage of power from current apparent temperature
     $.ajax({
         type: "GET",
         url: "/api/v1.0/temperature_alarm",
         dataType: 'json',
         data: {
             "CustomerID": $('#user_id').text()
         },
         success: function (response) {
             if (response[2]['now_temp'] != "無即時溫度") {
                 $("#now_temp").html(response[2]['now_temp'] + '°C')
                 $("#now_apptemp").html((response[2]['now_apptemp']).toFix(2) + '°C')
                 $("#now_apptemp_power").html(response[2]['now_avg_value'] + 'kWh')
             } else {
                 $("#now_temp").html(response[2]['now_temp'])
                 $("#now_apptemp").html((response[2]['now_apptemp']))
                 $("#now_apptemp_power").html(response[2]['now_avg_value'])
             }
             //  $("#inform_temp").html(response[1]['alarm_apptemp'] + '°C' + " ~ " + (response[1]['alarm_apptemp'] + 2) + '°C')
         },
         error: function (response) {
             sweetAlert('LVAMI 資料讀取失敗');
         }
     });
     //  draw the diagram about temperature region time with its average power value kWh(hour/per) and
     $.ajax({
         type: "GET",
         url: "/api/v1.0/data_persent",
         dataType: 'json',
         data: {
             "CustomerID": $('#user_id').text()
         },
         success: function (response) {
             apparent_temperature_compare_with_power(response)
         },
         error: function (response) {
             sweetAlert('LVAMI 資料讀取失敗');
         }
     });
 });