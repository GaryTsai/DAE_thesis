$(document).ready(function () {
    var temp = 0;
    year=2017;
    month=12;
    $.ajax({
        type: "GET",
        url: "/api/v1.0/rank_user",
        dataType: 'json',
        data: {},
        success: function (response) {
            temp = response[0]["local_averagepower"]
            $('#admin_average_sum').text(month.toString() + '月全部用戶的用電平均');
            $('#avg_power').text(response[0]["local_averagepower"] + 'kWh')
        },
        error: function (response) {}
    });
    // 多個用電戶早晚用電
    $.ajax({
        type: "GET",
        url: "/api/v1.0/data_total",
        dataType: 'json',
        data: {
            "CustomerID": $('#user_id').text()
        },
        success: function (response) {
            multiple_sum_of_electricity(response, temp);
        },
        error: function (response) {}
    });
});
$('#back_to_power').click(function () {
    $('#adminchartft').hide();
    $('#back_to_power').hide();
    $('#admincharttotal').show();
    $('#question_of_admin').show();

});