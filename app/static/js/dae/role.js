var role = "";
var gateway_uid
var lvami = ['lvami01_data', 'lvami02_data', 'lvami03_data', 'lvami04_data', 'lvami05_data', 'lvami06_data', 'lvami07_data', 'lvami08_data', 'lvami09_data', 'lvami10_data','D00001', 'D00002', 'D00003', 'D00004', 'D00005', 'D00006', 'D00007', 'D00008']

$(document).ready(function () {
    gateway_uid = $('.h5.text-uppercase').attr('id');
    if (lvami.indexOf(gateway_uid.toString()) != -1) {
        return ;
    } else {
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
    }
});