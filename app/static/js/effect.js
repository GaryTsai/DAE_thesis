$(document).ready(function () {
    // if (localStorage['user']){
    // $('.h5.text-uppercase').html(localStorage['user'])
    // $('.img-fluid.rounded-circle').attr('src', '/static/img/' + localStorage["user"] + '.png');
    // }
})
$('#realtime_diagram').click(function () {
    $('#day_avg').hide();
    $('#week_avg').hide();
    $('#total_dia').show();
})
$('#day_average_diagram').click(function () {
    $('#day_avg').show();
    $('#total_dia').hide();
    $('#week_avg').hide();

})

$('#week_average_diagram').click(function () {
    $('#day_avg').hide();
    $('#total_dia').hide();
    $('#week_avg').show();

})

$('#store_compute').click(function () {
    $('#house_text').hide();
    $('#family_data').hide();
    $('#staff_data').show();
    $('#client_data').show();

    $('#store_text').show();
})
$('#tab_store').click(function () {
    $('#house_text').hide();
    $('#store_text').show();
})
$('#house_compute').click(function () {
    $('#house_text').show();
    $('#family_data').show();

    $('#store_text').hide();
})
$('#tab_house').click(function () {
    $('#staff_data').hide();
    $('#client_data').hide();
    $('#store_text').hide();
    $('#house_text').show();

})
$('#tab_store').click(function () {
    $('.dashboard-counts.section-padding.env_carbon').hide();
})
$('.env_btn').click(function () {
    $('.dashboard-counts.section-padding.env_carbon').show();
})
$('#house_compute').click(function () {
    $('.dashboard-counts.section-padding.env_carbon').show();
})
$('#tab_house').click(function () {
    $('.dashboard-counts.section-padding.env_carbon').hide();
})
$('#tab_house').click(function () {
    $('.dashboard-counts.section-padding.env_carbon').hide();
})