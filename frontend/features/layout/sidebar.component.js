// Sidebar behavior: capture textarea input and send it when the send button is clicked or when Ctrl+Enter is pressed.
(function(){
	const textarea = document.getElementById('message-input');
	const sendButton = document.getElementById('send-button');
	if(!textarea || !sendButton) return;

	let sentOnce = false;

	function sendMessage(){
		const text = textarea.value.trim();
		if(!text) return;

		// Dispatch a custom event so other parts of the app can react
		const ev = new CustomEvent('message:send', { detail: { text }, bubbles:true });
		sendButton.dispatchEvent(ev);

		// After the very first successful send, shrink the textarea to 1/3 of initial height
		if(!sentOnce){
			textarea.classList.add('shrunk');
			sentOnce = true;
		}

		// Clear textarea after sending
		textarea.value = '';
		textarea.focus();
	}

	sendButton.addEventListener('click', sendMessage);

	// Ctrl+Enter to send
	textarea.addEventListener('keydown', (e)=>{
		if((e.ctrlKey || e.metaKey) && e.key === 'Enter'){
			e.preventDefault();
			sendMessage();
		}
	});

	// Expose a small API for tests or external code
	window.sidebarSend = sendMessage;
})();

