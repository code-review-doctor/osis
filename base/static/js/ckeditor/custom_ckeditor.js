CKEDITOR.on('instanceReady', function(e) {

    const buttonPasteFromWord = $('.'+e.editor.id).find(".cke_button__pastefromword");
    if (buttonPasteFromWord.length > 0) {
        const handleOnclickPasteFromWord = function (evt) {
            const notification1 = new CKEDITOR.plugins.notification(e.editor, {
                message: gettext("Please use the Ctrl+v shortcut to paste content."),
                type: 'info'
            });
            notification1.show();
        };
        buttonPasteFromWord[0].onclick = handleOnclickPasteFromWord;
    }

    e.editor.dataProcessor.writer.setRules('br', {
        breakAfterOpen: false
    })
    e.editor.dataProcessor.writer.setRules('p', {
        breakAfterOpen: false,
        breakBeforeOpen: false,
        breakBeforeClose: false,
        breakAfterClose: false
    })

});

function destroyAllInstances() {
    Object.values(CKEDITOR.instances).forEach((instance) => instance.destroy());
}
