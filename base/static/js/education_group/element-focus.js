document.addEventListener("DOMContentLoaded", function(event) {
    var eltidfocus = localStorage.getItem('eltidfocus');
    console.log('avt if');
    if (eltidfocus){
        console.log('if');
        var elt = document.getElementById(eltidfocus);
        if (elt){
            console.log('avt if2');
            elt.focus();
            elt.scrollIntoView({'block': 'center', 'inline': 'center'});
        }
    }
});
$('.btn_to_focus').click(function (evt) {
    console.log('sdjqsdf');
    console.log(this.id);
    localStorage.setItem('eltidfocus', this.id);
});
