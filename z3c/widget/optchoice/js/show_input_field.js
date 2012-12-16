var input_name = 'review_comp_template.widgets.review_field:input' 
if (this.value == "Other"){
    $("input[name='"+input_name+"']").css('visibility','visible');
} else {
    $("input[name='"+input_name+"']").css('visibility','hidden');
}
