$(document).ready(function () {

    //get sum of power value
    var temp_total_power = 0
    // var user_sum_power = 0
    $.ajax({
        type: "GET",
        url: "/api/v1.0/data_co2",
        dataType: 'json',
        data: {
            "CustomerID": $('#user_id').text(),
            "authority": $('#authority').val(),
            "gateway_uid": $('#gateway_uid').val()
        },
        success: function (response) {
            user_total_power = (response[0]['sum_power']).toFixed(2);
            $('#total').html((response[0]['sum_power']).toFixed(2) + " kWh");
        },
        error: function (response) {
            sweetAlert('LVAMI 資料讀取失敗');
        }
    });
    //comapre with local users and itself power value
    $.ajax({
        type: "GET",
        url: "/api/v1.0/rank_user",
        dataType: 'json',
        data: {
            "CustomerID": $('#user_id').text(),
            "authority": $('#authority').val(),
            "gateway_uid": $('#gateway_uid').val()

        },
        success: function (response) {
            $("#avg_power").html((response[0]["local_averagepower"]).toFixed(2) + ' kWh');
            local_compare_gauge_percent(user_total_power, (response[0]["local_averagepower"]).toFixed(2));
        },
        error: function (response) {

        }
    });
    // 住家
    $("#house_compute").click(function () {
        if (isNaN($("#house_people").val()) || !$("#house_people").val()) {
            sweetAlert('家庭人數請輸入整數');
            return;
        }
        $.ajax({
            type: "GET",
            url: "/api/v1.0/data_co2",
            dataType: 'json',
            data: {
                "CustomerID": $('#user_id').text(),
                "authority": $('#authority').val(),
                "gateway_uid": $('#gateway_uid').val()

                // "DateFrom": $("#datepicker_start_date").val() + " " + "00:15",
                // "DateTo": d.getFullYear() + "-" + month_start + "-" + date_start + " " + "00:00"
            },
            success: function (response) {
                $("#avg_people").html(((response[0]['sum_power'] / $("#house_people").val()) * response[0]['day_percent']).toFixed(2) + " kWh")
                $("#co2_value_family").html(((response[0]['sum_power'] / $("#house_people").val()) * response[0]['day_percent'] * 0.529).toFixed(2) + "公斤");
                $("#tree_family").html((((response[0]['sum_power'] / $("#house_people").val()) * response[0]['day_percent'] * 0.529).toFixed(2) / 1.8).toFixed(2) + "棵");
                $("#careco_family").html((((((response[0]['sum_power'] / $("#house_people").val()) * response[0]['day_percent'] * 0.529).toFixed(2)) * 0.529) / 0.236).toFixed(1) + "公里");
            },
            error: function (response) {
                sweetAlert('LVAMI 資料讀取失敗');
            }
        });
    })
    // 餐廳/商家
    $("#store_compute").click(function () {
        if (isNaN($('#number_staff').val()) || !$('#number_staff').val()) {
            sweetAlert('員工人數請輸入整數');

            return;
        }
        if (isNaN($('#number_client').val()) || !$('#number_client').val()) {
            sweetAlert('顧客人數請輸入整數');

            return;
        }
        if (isNaN($('#staff_time').val()) || !$('#staff_time').val()) {
            sweetAlert('員工人久待時間請輸入數字');
            return;
        }
        if (isNaN($('#client_time').val()) || !$('#client_time').val()) {
            sweetAlert('顧客久待時間請輸入數字');
            return;
        }
        var staff = $('#number_staff').val() * $('#staff_time').val();
        var client = $('#number_client').val() * $('#client_time').val();
        var total = staff + client;
        var stime = $('#staff_time').val();
        var ctime = $('#client_time').val();
        $.ajax({
            type: "GET",
            url: "/api/v1.0/data_co2",
            dataType: 'json',
            data: {
                "CustomerID": $('#user_id').text(),
                "authority": $('#authority').val(),
                "gateway_uid": $('#gateway_uid').val()

                // "DateFrom": $("#datepicker_start_date").val() + " " + "00:15",
                // "DateTo": d.getFullYear() + "-" + month_start + "-" + date_start + " " + "00:00"
            },
            success: function (response) {
                var total_kWh = response[0]['sum_power'];
                var per_kWh = (total_kWh / total);
                $("#avg_staff").html(" " + ((per_kWh * stime) * response[0]['day_percent']).toFixed(2) + " kWh");
                $("#avg_client").html(" " + ((per_kWh * ctime) * response[0]['day_percent']).toFixed(2) + " kWh");
                var per_client = ((per_kWh * ctime) * response[0]['day_percent'])
                var per_staff = ((per_kWh * stime) * response[0]['day_percent']);
                $("#co2_value_client").html((per_client * 0.529).toFixed(2) + "公斤");
                $("#tree_client").html(((per_client * 0.529).toFixed(2) / 1.8).toFixed(2) + "棵");
                $("#careco_client").html(((((per_client * 0.529).toFixed(2)) * 0.529) / 0.236).toFixed(1) + "公里");
                $("#co2_value_staff").html((per_staff * 0.529).toFixed(2) + "公斤");
                $("#tree_staff").html(((per_staff * 0.529).toFixed(2) / 1.8).toFixed(2) + "棵");
                $("#careco_staff").html(((((per_staff * 0.529).toFixed(2)) * 0.529) / 0.236).toFixed(1) + "公里");
            },
            error: function (response) {
                sweetAlert('LVAMI 資料讀取失敗');
            }
        });
    })
});