(function(){
	const container = document.getElementById('bubble-messages');
	if(!container) return;

	// Simple rotating mock replies. Replace with real API call later.
	const mockReplies = [
		'Respuesta mock: recibido — procesando tu entrada.',
		'Respuesta mock: gracias, analizamos el texto.',
		'Respuesta mock: este es un ejemplo de respuesta de la API.',
		'Respuesta mock: mensaje recibido correctamente.'
	];
	let mockIndex = 0;

	function now(){
		const d = new Date();
		return d.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
	}

	function createBubble(text, who){
		const el = document.createElement('div');
		el.className = 'bubble ' + (who === 'user' ? 'user' : 'bot');
		el.innerHTML = `
			<div class="content">${escapeHtml(text)}</div>
			<small class="meta">${who === 'user' ? 'Tú' : 'Asistente'} • ${now()}</small>
		`;
		return el;
	}

	function appendAndScroll(node){
		container.appendChild(node);
		// small timeout to let layout update before scrolling
		setTimeout(()=> container.scrollTop = container.scrollHeight, 60);
	}

	function escapeHtml(unsafe){
		return unsafe
			.replaceAll('&','&amp;')
			.replaceAll('<','&lt;')
			.replaceAll('>','&gt;')
			.replaceAll('"','&quot;')
			.replaceAll("'","&#039;");
	}

	// Simulate an API reply using a timeout. Returns a Promise<string>.
	function mockApiReply(userText){
		return new Promise((resolve)=>{
			const reply = mockReplies[mockIndex % mockReplies.length] + ' — eco: "' + userText.slice(0,120) + '"';
			mockIndex++;
			// random-ish delay to feel natural
			const delay = 600 + Math.floor(Math.random()*900);
			setTimeout(()=> resolve(reply), delay);
		});
	}

	// Handler for outgoing messages
	async function handleSend(detail){
		const text = (detail && detail.text) || (typeof detail === 'string' ? detail : '');
		if(!text || !text.trim()) return;

		// Append user bubble
		const userBubble = createBubble(text, 'user');
		appendAndScroll(userBubble);

		// Show a temporary 'typing' bubble for the bot
		const typing = document.createElement('div');
		typing.className = 'bubble bot';
		typing.innerHTML = `<div class="content">…</div><small class="meta">Asistente</small>`;
		appendAndScroll(typing);

		try{
			const reply = await mockApiReply(text);
			// replace typing bubble with actual reply
			const botBubble = createBubble(reply, 'bot');
			container.replaceChild(botBubble, typing);
			appendAndScroll(botBubble);
		}catch(err){
			typing.querySelector('.content').textContent = 'Error en la respuesta.';
		}
	}

	// Listen for the custom event dispatched by the sidebar when sending
	document.addEventListener('message:send', (e)=>{
		if(!e || !e.detail) return;
		handleSend(e.detail);
	});

		// NOTE: we intentionally do not listen to 'send-button-click' here.
		// The sidebar dispatches the canonical 'message:send' event when the user submits.
		// Listening to multiple events caused duplicate bubbles (both 'message:send' and
		// 'send-button-click' being fired). Keep a single source of truth.

	// Expose programmatic API
	window.bubbleChat = {
		send: (text)=> handleSend({ text }),
		clear: ()=> { container.innerHTML = ''; }
	};

})();
