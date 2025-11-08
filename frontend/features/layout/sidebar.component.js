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
        
        // Disparamos el evento desde 'document'
        document.dispatchEvent(ev);

        // After the very first successful send, shrink the textarea to 1/3 of initial height
        if(!sentOnce){
            textarea.classList.add('shrunk');
            sentOnce = true;
        }

        // Clear textarea after sending
        textarea.value = '';
        textarea.focus();
    }

    // --- ¡LA SOLUCIÓN AL BOTÓN VA AQUÍ! ---
    // Eliminamos el listener de 'click' que fallaba. Usamos 'pointerdown' que es más directo.
    sendButton.addEventListener('pointerdown', (e) => {
        e.preventDefault(); // IMPORTANTE: Detiene cualquier otro comportamiento que bloquee el envío
        sendMessage();
    });
    // --- FIN DE LA SOLUCIÓN ---


    // Modificamos la escucha del teclado para que Enter envíe el mensaje (sin Ctrl/Meta)
    textarea.addEventListener('keydown', (e)=>{
        // Si la tecla es ENTER y NO se presiona SHIFT, enviamos el mensaje.
        if(e.key === 'Enter' && !e.shiftKey){
            e.preventDefault(); // Detiene el salto de línea por defecto
            sendMessage();
        }
    });

    // Expose a small API for tests or external code
    window.sidebarSend = sendMessage;
})();