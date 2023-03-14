
const colour_codes = {
   "BLACK":"\\x1b[30m",
   "RED":"\\x1b[31m",
   "GREEN":"\\x1b[32m",
   "YELLOW":"\\x1b[33m",
   "BLUE":"\\x1b[34m",
   "MAGENTA":"\\x1b[35m",
   "CYAN":"\\x1b[36m",
   "WHITE":"\\x1b[37m",
   "GREY":"\\x1b[90m",
   "BOLD":"\\x1b[1m",
   "DIM":"\\x1b[2m",
   "ITALIC":"\\x1b[3m",
   "UNDERLINE":"\\x1b[4m",
   "BLINK":"\\x1b[5m",
   "INVERT":"\\x1b[7m",
   "STRIKETHROUGH":"\\x1b[9m",
   "RESET":"\\x1b[0m",
   "error":"\\x1b[31m",
   "info":"\\x1b[34m",
   "success":"\\x1b[32m",
   "warning":"\\x1b[33m",
}
function print(text){
    console.log(text);

    var Convert = require('ansi-to-html');
    var convert = new Convert();
    console.log(convert.toHtml(text));

    document.getElementById("output").innerHTML += text + "<br>";
}
eel.expose(print);

function clear_screen(){
    document.getElementById("output").innerHTML = ""
}
eel.expose(clear_screen);


let input_buffer = ""
let is_inputting = false
function get_input(prompt){
    // Get the input boxs
    const input_prompt = document.getElementById("input_prompt");
    const input_box = document.getElementById("input");

    // Set the prompt
    input_prompt.innerHTML = prompt

    // If not waiting for the user to press enter
    if (!is_inputting){

        // Define a handler
        function input_handler(e){
             input_buffer = input_box.value
             input_box.value = ""
             input_box.removeEventListener("change", input_handler)
             is_inputting = false
        }

        // Register the handler as a listener
        input_box.addEventListener("change", input_handler)

        // Wait for input
        is_inputting = true
    }

    return input_buffer

}
eel.expose(get_input);

function clear_input_buffer(){
    input_buffer = ""
}
eel.expose(clear_input_buffer)