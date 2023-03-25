
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
    const output = document.getElementById("output")
    output.innerHTML = ""
    output.scrollIntoView()

}
eel.expose(clear_screen);


let input_buffer = ""
let temp_input_buffer = ""
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
            temp_input_buffer = input_box.value
             if (e.key != "Enter"){
                return
             }

             input_buffer = input_box.value
             if (input_buffer == ""){
                 // Make sure the loop breaks
                 input_buffer = " "
             }

             input_box.removeEventListener("keypress", input_handler)
             is_inputting = false
        }

        // Register the handler as a listener
        input_box.addEventListener("keypress", input_handler)

        // Wait for input
        is_inputting = true
    }

    return input_buffer

}
eel.expose(get_input);

function force_get_input(){
    return temp_input_buffer
}
eel.expose(force_get_input);

function clear_input_buffer(){
    input_buffer = ""
    temp_input_buffer = ""
    document.getElementById("input").value = ""
}
eel.expose(clear_input_buffer)

function choose_item(option){
    input_buffer = option.id
    temp_input_buffer = input_buffer
    document.getElementById("input").value = input_buffer
    document.getElementById("input").scrollIntoView()
}

function close_window(){
    window.close()
}
eel.expose(close_window)

function set_title(title){
    document.title = "Quiz Game UI | " + title
}
eel.expose(set_title)

// Make sure the window is big enough
if (window.outerWidth < 1600 || window.outerHeight < 900){
    window.resizeTo(1600, 900);
}

function close_python_and_window(){
    eel.close_python()
}