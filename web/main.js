
function print(text){
    console.log(text);
    document.getElementById("output").innerHTML += text + "<br>";
}
eel.expose(print);

function clear_screen(){
    document.getElementById("output").innerHTML = ""
}
eel.expose(clear_screen);


let input_text = ""
let is_inputting = false
function get_input(prompt){
    const input_prompt = document.getElementById("input_prompt");
    input_prompt.innerHTML = prompt
    if (!is_inputting){
        //Get the input
        const input_box = document.getElementById("input");



        /*Input handler*/
        function input_handler(e){
             input_text = input_box.value
             input_box.value = ""
             input_box.removeEventListener("change", input_handler)
             is_inputting = false
        }
        input_box.addEventListener("change", input_handler)

        is_inputting = true
    }

    return input_text

}
eel.expose(get_input);

function clear_input_buffer(){
    input_text = ""
}
eel.expose(clear_input_buffer)