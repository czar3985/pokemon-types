$('.types-dropdown').change(function (e) {
    window.location.href = '/pokemon/' + $(this).val();
});