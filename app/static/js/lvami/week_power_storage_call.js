$(document).ready(function () {
    $('#power_sign1').html('<i class=' + '"fa fa-battery-empty fa-lg"' + "aria-hidden=" + '"true"' + 'style="color:black;">' + "</i>" + "<span>" + " : 50萬千瓦以下限電準備" + "</span>");
    $('#power_sign2').html("<i class=" + '"fa fa-battery-quarter fa-lg"' + "aria-hidden=" + '"true"' + 'style="color:red;">' + "</i>" + "<span>" + " : 90萬千瓦以下限電準備" + "</span>");
    $('#power_sign3').html("<i class=" + '"fa fa-battery-half fa-lg"' + "aria-hidden=" + '"true"' + 'style="color:orange;">' + "</i>" + "<span>" + " : 小於等於 6% 供電警戒" + "</span>");
    $('#power_sign4').html("<i class=" + '"fa fa-battery-three-quarters fa-lg"' + "aria-hidden=" + '"true"' + 'style="color:#e6e600;">' + "</i>" + "<span>" + " : 10% ~ 6% 之間供電吃緊" + "</span>")
    $('#power_sign5').html("<i class=" + '"fa fa-battery-full fa-lg"' + "aria-hidden=" + '"true"' + 'style="color:green;">' + "</i>" + "<span>" + " : 大於等於10% 供電充裕" + "</span>");
    //一週用電警告
    $.ajax({
        type: "GET",
        url: "/api/v1.0/week_power_storage",
        dataType: 'json',
        data: {},
        success: function (response) {
            for (var i = 0; i < response.length ; i++) {
                $('#date' + i).html(response[i].date);
            }
            for (var i = 0; i < response.length ; i++) {
                $('#operatingReserve' + i).html(response[i]["operatingReserve(MW)"]);
            }
            for (var i = 0; i < response.length ; i++) {
                $('#operatingReservePercent' + i).html(response[i]["operatingReservePercent(%)"]);
            }
            for (var i = 0; i < response.length ; i++) {
                $('#systemNetPeakLoad' + i).html(response[i]["systemNetPeakLoad(MW)"]);
            }
            for (var i = 0; i < response.length ; i++) {
                $('#systemPeakLoad' + i).html(response[i]["systemPeakLoad(MW)"]);
            }
            for (var i = 0; i < response.length ; i++) {
                if (response[i]["operatingReserve"] <= 50 && response[i]["operatingReserve(MW)"] <= 6) {
                    $('#power_light' + i).html('<i class=' + '"fa fa-battery-empty fa-lg"' + "aria-hidden=" + '"true"' + 'style="color:black;">' + "</i>");
                } else if (response[i]["operatingReserve(MW)"] <= 90 && response[i]["operatingReserve(MW)"] <= 50 && response[i]["operatingReservePercent(%)"] <= 6) {
                    $('#power_light' + i).html("<i class=" + '"fa fa-battery-quarter fa-lg"' + "aria-hidden=" + '"true"' + 'style="color:red;">' + "</i>");
                } else if (response[i]["operatingReservePercent(%)"] <= 6) {
                    $('#power_light' + i).html("<i class=" + '"fa fa-battery-half fa-lg"' + "aria-hidden=" + '"true"' + 'style="color:orange;">' + "</i>");
                } else if ((response[i]["operatingReservePercent(%)"] > 6) && (response[i]["operatingReservePercent(%)"] < 10)) {
                    $('#power_light' + i).html("<i class=" + '"fa fa-battery-three-quarters fa-lg"' + "aria-hidden=" + '"true"' + 'style="color:#e6e600;">' + "</i>");
                } else if (response[i]["operatingReservePercent(%)"] >= 10) {
                    $('#power_light' + i).html("<i class=" + '"fa fa-battery-full fa-lg"' + "aria-hidden=" + '"true"' + 'style="color:green;">' + "</i>");
                }
            }
        },
        error: function (response) {
            sweetAlert('LVAMI 資料讀取失敗');
        }
    });
});