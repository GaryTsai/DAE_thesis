var current_date = new Date();
var month = current_date.getMonth() + 1; //January is 0!
var year = current_date.getFullYear();
var authority = $('#authority').val();
var gateway_uid = $('.h5.text-uppercase').attr('id');
var meter_info = new Object();

$(document).ready(function () {
    // get an hour before yesterday's electricity
    $.ajax({
        type: "GET",
        url: "/api/v1.0/role",
        dataType: 'json',
        async: false,
        success: function (response) {
            role = response;
        },
        error: function () {
            swal({
                title: '角色設定',
                type: 'error'
            });
        }
    })
    // 選擇電錶
    $.ajax({
        type: "GET",
        url: "/api/v1.0/query/settings",
        dataType: 'json',
        // async: false,
        data: {
            'authority': authority,
            'gateway_uid': gateway_uid
        },
        success: function (meter_data) {
            if (role == "Cloud" && authority == '1')
                meter_data = JSON.parse(meter_data);
            if (meter_data.length == 0) {
                swal({
                    title: '此Gateway尚未設定電錶',
                    type: 'success'
                })
            } else {
                for (item in meter_data) {
                    meter_info[item] = meter_data[item]['model'];
                }
                swal({
                    title: '請選擇電錶',
                    input: 'select',
                    inputOptions: meter_info,
                    // inputPlaceholder: '',
                    showCancelButton: true,
                    allowOutsideClick: false,
                    showLoaderOnConfirm: true,

                }).then(function (value) {
                    address = meter_data[value]['address'];
                    channel = meter_data[value]['ch'];
                    model = meter_data[value]['model'];
                    if (authority == "1") {
                        year = new Date().getFullYear();
                        month = new Date().getMonth();
                        console.log();
                        length = power_check(gateway_uid, year, 7, authority, model, address, channel)
                        console.log('length' + length);
                        if (length >= 4) {
                            initset_date(new Date().getFullYear(), 7, authority, gateway_uid, address, channel);
                            // initset_date(new Date().getFullYear(), new Date().getMonth() + 1, authority, gateway_uid, address, channel);
                        } else {
                            swal({
                                title: '此電錶無任何電力資訊',
                                type: 'warning',
                                showCancelButton: true,
                                allowOutsideClick: false,
                                showLoaderOnConfirm: true,
                            }).then((result) => {
                                window.location.assign('/gateway');
                            });
                        }
                    } else {
                        year = 2017;
                        month = 12;
                        initset_date(year, month, authority, gateway_uid, address, channel);
                    }
                }, function (dismiss) {
                    if (dismiss === 'cancel') {
                        window.location.assign('/gateway');
                    }
                })
            }
        },
        error: function (meter_data) {
            alert("開機設定資料讀取逾時");
        }
    });
})
if (authority == "1") {
    year = new Date().getFullYear();
    month = new Date().getMonth();
} else {
    year = 2017;
    month = 11;
}
$("#power_information_time").datepicker({
    dateFormat: 'yy-mm ',
    changeMonth: true,
    currentText: "當月",
    minDate: new Date(2017, 1 - 1, 1),
    maxDate: '0',
    changeYear: true,
    monthNames: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
    monthNamesShort: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
    showMonthAfterYear: true,
    showButtonPanel: true,
    // defaultDate: "2017-12",
    onClose: function (dateText, inst) {
        var new_month = $("#ui-datepicker-div .ui-datepicker-month :selected").val();
        var new_year = $("#ui-datepicker-div .ui-datepicker-year :selected").val();
        $(this).val($.datepicker.formatDate('yy-mm', new Date(new_year, new_month, 1)));
    }

}).datepicker('setDate', new Date(year, month, 01)); //11代表實際月份12
$("#power_information_time").focus(function () {
    $(".ui-datepicker-calendar").hide();
    $("#ui-datepicker-div").position({
        my: "center top",
        at: "center bottom",
        of: $(this)
    });
    $("#ui-datepicker-div .ui-datepicker-month :selected").val(new_month);
    $("#ui-datepicker-div .ui-datepicker-year :selected").val(new_year);
}).datepicker('setDate', new Date(year, month, 01));
// 時間選擇月份
$('#time_search').click(function () {
    var dateEntered = new Date($('#power_information_time').val());
    year = dateEntered.getFullYear();
    month = dateEntered.getMonth() + 1;
    if (authority == "1") {
        length = power_check(gateway_uid, year, month, authority, model, address, channel);
        if (length >= 4) {
            initset_date(year, month, authority, gateway_uid, address, channel);
        } else {
            swal({
                title: month + '月電錶無任何電力資訊',
                type: 'warning',
                allowOutsideClick: false
            })

        }
    } else if (authority == "0") {
        if (year == 2018) {
            swal({
                title: year + '年' + month + '月電錶無任何電力資訊',
                type: 'warning',
                allowOutsideClick: false
            })
        } else {
            initset_date(year, month, authority, gateway_uid, address, channel);
        }
    }
});

function initset_date(year, month, authority, gateway_uid, address, channel) {
    $.ajax({
        type: "GET",
        url: "/api/v1.0/realtime_change",
        dataType: 'json',
        data: {
            "CustomerID": $('.h5.text-uppercase').text(),
            'year': year,
            'month': month,
            "gateway_uid": gateway_uid,
            "authority": authority,
            "channel": channel,
            "address": address
        },
        success: function (meter_data) {
            if (meter_data[0]['current_value'] == 0) {
                $("#prev_power_now_ago").html('無即時資料');
            } else {
                $("#prev_power_now_ago").html((meter_data[0]["current_value"]).toFixed(2) + 'kWh');
            }
        },
        error: function (meter_data) {}
    });
    //get ex-month sum of power
    //get the sum of expense about two category and sum of power
    //realtime of the power (15min/per)
    $.ajax({
        type: "GET",
        url: "/api/v1.0/realtime_power",
        dataType: 'json',
        data: {
            "CustomerID": $('.h5.text-uppercase').text(),
            'year': year,
            'month': month,
            "gateway_uid": gateway_uid,
            "authority": authority,
            "channel": channel,
            "address": address
        },
        success: function (meter_data) {
            $('.month_sum').text((month) + '月用電');
            $('#max_power').html((meter_data['demands'][meter_data['demands'].length - 1]['sum_power']).toFixed(2) + " kWh");
            history_power_chart(meter_data);
        },
        error: function (meter_data) {
            sweetAlert('LVAMI 即時資訊讀取失敗');
        }
    });
    // 日平均
    $.ajax({
        type: "GET",
        url: "/api/v1.0/avg_day_power",
        dataType: 'json',
        data: {
            "CustomerID": $('.h5.text-uppercase').text(),
            'year': year,
            'month': month,
            "gateway_uid": gateway_uid,
            "authority": authority,
            "channel": channel,
            "address": address
        },
        success: function (meter_data) {
            day_avg_diagram(meter_data);
        },
        error: function (meter_data) {
            sweetAlert('LVAMI 資料讀取失敗');
        }
    });
    // 週平均
    $.ajax({
        type: "GET",
        url: "/api/v1.0/avg_week_power",
        dataType: 'json',
        data: {
            "CustomerID": $('.h5.text-uppercase').text(),
            'year': year,
            'month': month,
            "gateway_uid": gateway_uid,
            "authority": authority,
            "channel": channel,
            "address": address
        },
        success: function (meter_data) {
            week_avg(meter_data);
        },
        error: function (meter_data) {
            sweetAlert('LVAMI 資料讀取失敗');
        }
    });
    //基本用電
    $.ajax({
        type: "GET",
        url: "/api/v1.0/base_demand_detection",
        dataType: 'json',
        data: {
            "CustomerID": $('.h5.text-uppercase').text(),
            'year': year,
            'month': month,
            "gateway_uid": gateway_uid,
            "authority": authority,
            "channel": channel,
            "address": address
        },
        success: function (meter_data) {
            $("#base_demand").text(meter_data["base_demand"].toFixed(2) + " kWh");
            $("#base_of_expense").text('NT$ ' + (meter_data["base_demand"] * 2880 * 1.63).toFixed(0));
            $(".month_number").text(month + '月的基礎用電費用為')
        },
        error: function (meter_data) {

        }
    });
    //用電累積
    $.ajax({
        type: "GET",
        url: "/api/v1.0/data_accumulation_kWh",
        dataType: 'json',
        data: {
            "CustomerID": $('.h5.text-uppercase').text(),
            'year': year,
            'month': month,
            "gateway_uid": gateway_uid,
            "authority": authority,
            "channel": channel,
            "address": address
        },
        // async: false,
        success: function (meter_data) {
            power_of_accumulation(meter_data, meter_data['power_of_expense'][0]['ex_month_power'], year, month);
            $('#bill5').html("NT$ " + meter_data['power_of_expense'][0]['house_bill'].toFixed(0));
            $('#bill6').html("NT$ " + meter_data['power_of_expense'][0]['store_bill'].toFixed(0));

        },
        error: function (meter_data) {
            sweetAlert('LVAMI 資料讀取失敗');
        }
    });
}
// 檢查有無電力資料
function power_check(gateway_uid, year, month, authority, modelmodel, address, channel) {
    var length = 6
    $.ajax({
        type: "GET",
        url: "/api/v1.0/power_check",
        dataType: 'json',
        async: false,
        data: {
            'model': model,
            "gateway_uid": gateway_uid,
            "authority": authority,
            "channel": channel,
            "address": address,
            "month": month,
            "year": year

        },
        success: function (meter_data) {
            length = meter_data;
            console.log(meter_data);
        },
        error: function (meter_data) {
            sweetAlert('LVAMI 資料讀取失敗');
        }
    });
    return length;
}