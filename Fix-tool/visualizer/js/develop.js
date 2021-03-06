let loader;

$(function () {
    loader = $("#loader");
    loader.hide();
    $("#translate button[type=submit]").click(translateInput);
});

function translateInput(e) {
    e.preventDefault();

    loader.show();

    const inputText = $("#inputText").val();
    const sourceLang = 'cs';
    const targetLang = 'en';

    let targetText = undefined;

    $.post(
        `https://lindat.mff.cuni.cz/services/translation/api/v2/languages/?src=${sourceLang}&tgt=${targetLang}`,
        {input_text: inputText}
    ).done(function (data) {
        $("#originalTranslation").val(data);

        $.post(
            `http://bakalarka.localhost/?src=${sourceLang}&tgt=${targetLang}`,
            {
                source_text: inputText,
                target_text: data
            }
        ).done(function (data) {
            $("#afterPostprocessingTranslation").val(data);
        }).fail(function () {
            $("#translate").prepend('<div class="alert alert-danger">Cannot connect to preprocessor. Please try it later.</div>');
        });

    }).fail(function (){
        $("#translate").prepend('<div class="alert alert-danger">Cannot connect to LINDAT translation service. Please try it later.</div>');
    }).always(function (){
        loader.hide();
    });
}

