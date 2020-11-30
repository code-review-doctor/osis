const DEFAULT_CONFIGURATION = {
    errorClass: "has-error",
    successClass: "",
    trigger: "focusin focusout",
    classHandler: function (inputField){
        return $(inputField.element.closest(".form-group") || inputField.element.closest("div"));
    },
    errorsContainer: function(inputField){
        return inputField.$element.closest(".form-group")
    },
    errorsWrapper: '<div class="help-block"></div>',
    errorTemplate: '<p></p>',
}

$(document).ready(function () {
    window.Parsley.addAsyncValidator('async-osis', remoteFieldValidation);

    $(".osis-form").parsley(DEFAULT_CONFIGURATION);

    // In case of invalid input for type integer, the value accessible from js is "", therefore you would never got an error.
    $(".osis-form").each(function(){
        addValidationOnNumberInput($(this));
    })


    window.Parsley.on('field:success', function (){
        const inputField = this;
        if(inputField.warning !== undefined && inputField.warning !== null){
            displayWarning(inputField);
        }
        else{
            hideWarning(inputField)
        }
    })

    window.Parsley.on('form:error', function (){
        highlightFormTabsWithError()
    })
    highlightFormTabsWithError()
})

function displayWarning(inputField){
    inputField._ui.$errorClassHandler.removeClass("has-success");
    inputField._ui.$errorClassHandler.addClass("has-warning");
    inputField._ui.$errorsWrapper.text(inputField.warning);
}

function hideWarning(inputField){
    inputField._ui.$errorClassHandler.removeClass("has-warning");
    inputField._ui.$errorsWrapper.text("");
}

function remoteFieldValidation(xhr) {
    const inputField = this;
    return xhr.then(function(jsonResponse) {
        if (!jsonResponse["valid"]) {
            return $.Deferred().reject(jsonResponse["msg"]);
        }
        inputField.warning = jsonResponse["msg"];
        return true;
    })
}


function addValidationOnNumberInput($form){
    $form.find("input[type=number]").each(function(){
        convertNumberInputToTextInputWithNumberValidation($(this));
    })
}

function convertNumberInputToTextInputWithNumberValidation($numberInput){
    const isDecimal = isDecimalInput($numberInput);

    $numberInput.attr("type", "text");
    $numberInput.attr("data-parsley-type", isDecimal ? "number" : "integer");
}

function isDecimalInput($numberInput){
    return $numberInput.attr("step") !== undefined;
}

function highlightFormTabsWithError(){
    const formTabsUl = document.getElementsByClassName("form-tab");
    for (const tabUlElement of formTabsUl){
        const tabContentElement = getTabContentElementFromTabUl(tabUlElement);
        if (doesTabContainsErrors(tabContentElement)) {
            highlightTabUl(tabUlElement)
        }
    }
}

function getTabContentElementFromTabUl(tabUlElement){
    const anchorElement = tabUlElement.getElementsByTagName("A")[0]
    const tabContentId = anchorElement.getAttribute("href").replace("#", "")
    return document.getElementById(tabContentId)
}

function doesTabContainsErrors(tabContentElement){
    return tabContentElement.getElementsByClassName('has-error').length > 0 || tabContentElement.getElementsByClassName('has-warning').length > 0
}

function highlightTabUl(tabUlElement){
    tabUlElement.classList.add("contains-error");
}