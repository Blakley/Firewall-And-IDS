
// Function to add logs to the front-end terminal logger
function insertTerminalText(text) {
    // Create a new div element with the class "Terminal__text"
    var newTextElement = document.createElement("div");
    newTextElement.className = "Terminal__text";
    
    // Replace newline characters with <br> tags
    var formattedText = text.replace(/\n/g, "<br>");
    
    // Set the innerHTML of the new element
    newTextElement.innerHTML = formattedText;
    
    // Get the Terminal__Prompt element
    var promptElement = document.querySelector('.Terminal__Prompt');
    
    // Insert the new element before the Terminal__Prompt element
    promptElement.parentNode.insertBefore(newTextElement, promptElement);
}


// checks for new logs
var _loginterval = setInterval(function() {
    let route = '/terminal';

    $.get(route, function(data) {
        
        let msg = data.message;
        if (msg != "")
            insertTerminalText(msg);

    }, 'json');

}, 1000);