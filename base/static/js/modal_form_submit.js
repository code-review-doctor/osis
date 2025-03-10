function redirect_after_success(modal, xhr) {
    destroyAllInstances();
    $(modal).modal('toggle');
    if (xhr.hasOwnProperty('partial_reload')) {
        $(xhr["partial_reload"]).load(xhr["success_url"]);
    } else if (xhr.hasOwnProperty('success_url')) {
        window.location.href = xhr["success_url"];
        if(xhr["force_reload"]){
            window.location.reload();
        }
    } else {
        window.location.reload();
    }
}

function addDispatchEventOnSubmitAjaxForm(e) {
    document.dispatchEvent(new CustomEvent("formAjaxSubmit:onSubmit", {
        "detail": $(e.target).find("button[type='submit']")
    }));
}

var formAjaxSubmit = function (form, modal) {
    form.submit(function (e) {
        if ($(this).hasClass("validate")){
            if (! $(this).parsley().isValid()) {
                return false;
            }
        }

        // Added preventDefault so as to not add anchor "href" to address bar
        e.preventDefault();
        addDispatchEventOnSubmitAjaxForm(e);

        const isUploadForm = $(this).attr('enctype') === 'multipart/form-data';
        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: isUploadForm ? new FormData($(this)[0]) : $(this).serialize() ,
            processData: !isUploadForm,
            contentType: (isUploadForm) ? false : 'application/x-www-form-urlencoded; charset=UTF-8',
            context: this,
            success: function (xhr, ajaxOptions, thrownError) {
                //Stay on the form if there are errors.
                if ($(xhr).find('.has-error,.alert-danger:not(#notice-header),.stay_in_modal').length > 0) {
                    $(modal).find('.modal-content').html(xhr);
                    // Add compatibility with ckeditor and related textareas
                    bindTextArea();
                    // Refresh the form node because the modal content has changed.
                    form = $("#"+form.attr('id'));
                    // Binding the new content with submit method.
                    formAjaxSubmit(form, modal);
                    document.dispatchEvent(new CustomEvent("formAjaxSubmit:error", {}));
                } else {
                    redirect_after_success(modal, xhr);
                    document.dispatchEvent(new CustomEvent("formAjaxSubmit:success", {}));
                }
            },
            error: function (xhr, ajaxOptions, thrownError) {
                // handle response errors here
                this.dispatchEvent(new CustomEvent("formAjaxSubmit:error", {}));
            }
        });
    });
};

// CKEDITOR needs to dynamically bind the textareas during an XMLHttpRequest requests
function bindTextArea() {
    //clean instances before binding to avoid error on CKEDITOR.replace with same instance id
    destroyAllInstances();
    $("textarea[data-type='ckeditortype']").each(function () {
        CKEDITOR.replace($(this).attr('id'), $(this).data('config'));
    });
}

// Before submitting, we need to update textarea with ckeditor element.
function CKupdate() {
    for (let instance in CKEDITOR.instances)
        CKEDITOR.instances[instance].updateElement();
}

function submitFormWithPostponement(element){
    var input = $("<input>")
        .attr("type", "hidden")
        .attr("name", "to_postpone").val(1);
    $(element).closest("form").append(input).submit();
}

function bind_trigger_modal() {
    $(".trigger_modal").click(function () {
        let url = $(this).data("url");
        let modal_class = $(this).data("modal_class");
        let content = $('#form-modal-ajax-content');

        $('#modal_dialog_id').attr("class", "modal-dialog").addClass(modal_class);
        content.empty();
        $('#form-ajax-modal').modal('show');

        content.load(url, function () {
            bindTextArea();
            // Make the template more flexible to find the first form
            let form = $(this).find('form').first();
            formAjaxSubmit(form, '#form-ajax-modal');
        });
    });
}

bind_trigger_modal();

