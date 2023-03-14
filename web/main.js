
const colour_codes = {
   "BLACK":"[30m",
   "RED":"[31m",
   "GREEN":"[32m",
   "YELLOW":"[33m",
   "BLUE":"[34m",
   "MAGENTA":"[35m",
   "CYAN":"[36m",
   "WHITE":"[37m",
   "GREY":"[90m",
   "BOLD":"[1m",
   "DIM":"[2m",
   "ITALIC":"[3m",
   "UNDERLINE":"[4m",
   "BLINK":"[5m",
   "INVERT":"[7m",
   "STRIKETHROUGH":"[9m",
   "RESET":"[0m",
}

function translate_colours(text){
    // Loop through the colour codes
    for (const [key, value] of Object.entries(colour_codes)) {
        while (text.includes(value)){
            text = text.replace(value, `<span class="colour-code-${key.toLowerCase()}">`)
            text += "</span>"
        }
    }
    return text
}

function print(text){
    console.log(text);

    text = translate_colours(text)

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
    input_prompt.innerHTML = translate_colours(prompt)

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