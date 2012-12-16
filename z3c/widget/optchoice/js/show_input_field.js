var input_name = 'NAME_PLACEHOLDER' 
if (this.value == "Other"){
    $("input[name='"+input_name+"']").css('visibility','visible');
} else {
    $("input[name='"+input_name+"']").css('visibility','hidden');
}
