// // Function to add logs to the front-end terminal logger
// function insertTerminalText(text) {
//     // Create a new div element with the class "Terminal__text"
//     var newTextElement = document.createElement("div");
//     newTextElement.className = "Terminal__text";

//     // Replace newline characters with <br> tags
//     var formattedText = text.replace(/\n/g, "<br>");

//     // Set the innerHTML of the new element
//     newTextElement.innerHTML = formattedText;

//     // Get the Terminal__Prompt element
//     var promptElement = document.querySelector('.Terminal__Prompt');

//     // Insert the new element before the Terminal__Prompt element
//     promptElement.parentNode.insertBefore(newTextElement, promptElement);
// }


// // checks for new logs
// var _loginterval = setInterval(function() {
//     let route = '/terminal';

//     $.get(route, function(data) {

//         let msg = data.message;
//         if (msg != "")
//             insertTerminalText(msg);

//     }, 'json');

// }, 1000);


// Terminal text insertions
const prompt = document.querySelector('.Terminal__Prompt');
const body = document.querySelector('.Terminal__body');
let inputText = ''; // variable to store user input

document.addEventListener('keydown', function(event) {
	const char = event.key;

	if (char === 'Enter') {
		event.preventDefault();

		if (inputText.toLowerCase() === 'clear') {
            // handles clearing the terminal
			const terminalTextElements = document.querySelectorAll('.Terminal__text');
			terminalTextElements.forEach(function(element) {
				body.removeChild(element);
			});
		} 
        else {
            // handles submitting the command and getting the output back

            // create submission data
            let route = '/terminal_submit'
            let form = {
                'terminal_input': inputText
            }

            // submit terminal command
            $.post(route, form, function(data) {
                // get message
                let msg = data.message
                console.log("terminal command: ", msg)

                let _text = document.createElement('div');
                _text.classList.add('Terminal__text');
                _text.textContent = msg;
                body.insertBefore(_text, prompt);

            }, 'json');
		}

		// reset terminal
		prompt.innerHTML = '<span class="Prompt__user">demo@kali:</span><span class="Prompt__location">~</span><span class="Prompt__dollar">$</span><span class="Prompt__cursor"></span>';
		inputText = '';
	} 
    else if (char == 'Backspace') {
        // handle backspaces
		event.preventDefault();

		if (inputText.length > 0) {
			inputText = inputText.slice(0, -1);   // Remove last character from inputText
			prompt.removeChild(prompt.lastChild); // Remove last character from prompt
		}
	} 
    else {
        // handle inputing the text command
		inputText += char;
		prompt.insertBefore(document.createTextNode(char), prompt.lastChild);
	}
});