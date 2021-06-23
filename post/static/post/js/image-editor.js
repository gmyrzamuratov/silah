$(window).load(function () {
    $('.popupCloseButton').click(function(){
        $('.image-editor-popup').hide();
    });

    $('.watermarkCloseButton').click(function(){
        $('.watermark-editor-popup').hide();
    });

    $("#gallery").on('click', ".js-edit-photos", function () {
       $('.image-editor-popup').show();
    });

    $("#gallery").on('click', ".js-edit-watermark", function () {
       $('.watermark-editor-popup').show();
    });
});