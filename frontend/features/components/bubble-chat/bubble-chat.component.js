(function(){
    const container = document.getElementById('bubble-messages');
    if(!container) return;

    // --- SE ELIMINÓ EL CÓDIGO MOCK ---

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

    /**
     * INICIO: Código de la API Real
     * Esta es la nueva función que llama a tu API de Render.
     */
    async function getApiReply(userText) {
        // Esta es la URL de tu API desplegada
        const apiUrl = "https://traductor-de-fraude.onrender.com/analizar";

        // Tu API espera un JSON con "url", no con "texto".
        // Usamos una regex simple para encontrar el primer enlace en el chat.
        const urlRegex = /(https?:\/\/[^\s()<>]+)|(www\.[^\s()<>]+)/;
        const match = userText.match(urlRegex);

        // Si no se envía un enlace, el bot responde pidiéndolo.
        if (!match) {
            return "Por favor, envía un texto que contenga un enlace para analizar.";
        }

        // Preparamos el enlace (añade http:// si solo es 'www.')
        let urlToSend = match[0];
        if (urlToSend.startsWith('www.')) {
            urlToSend = 'http://' + urlToSend;
        }

        // Este es el JSON que tu API espera: { "url": "..." }
        const data = {
            url: urlToSend
        };

        try {
            // Llamamos a la API con el método POST
            const response = await fetch(apiUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data), // Enviamos el JSON
            });

            if (!response.ok) {
                // Manejar errores si la API falla (devuelve 500, etc.)
                console.error("Error de la API:", await response.json());
                return `Error del servidor (${response.status}). Intenta de nuevo.`;
            }

            // 'resultado' es el JSON que viene de tu API (con 'titulo', 'explicacion_simple', etc.)
            const resultado = await response.json(); 
            
            // Formateamos la respuesta para el chat (Ej: "¡Peligro! Están fingiendo ser tu banco.")
            return `${resultado.titulo} ${resultado.explicacion_simple}`;

        } catch (error) {
            console.error("Error al llamar a la API:", error);
            return "No se pudo contactar al analizador. Revisa tu conexión.";
        }
    }
    /**
     * FIN: Código de la API Real
     */


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
            // --- ¡CAMBIO IMPORTANTE AQUÍ! ---
            // Reemplazamos 'mockApiReply' por la llamada a la API real
            const reply = await getApiReply(text);
            // --- FIN DEL CAMBIO ---

            // replace typing bubble with actual reply
            const botBubble = createBubble(reply, 'bot');
            container.replaceChild(botBubble, typing);
            appendAndScroll(botBubble);
        }catch(err){
            console.error("Error en handleSend:", err);
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