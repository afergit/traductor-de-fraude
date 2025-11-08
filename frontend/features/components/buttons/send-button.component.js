// This script simply re-dispatches a semantic event when the send button is clicked
// send-button stub: keep file for styling/structure but avoid dispatching a redundant event.
// The sidebar is the authoritative sender and dispatches `message:send`.
(function(){
	// Intentionally do not add a click handler that dispatches events.
	// This prevents duplicate send events when both sidebar and this button attach listeners.
	const btn = document.getElementById('send-button');
	if(!btn) return;
	
	// --- ¡CÓDIGO CORREGIDO AQUÍ! ---
	// Eliminamos los listeners de pointerdown/up para que sidebar.component.js sea el único que controle la entrada.
	
	// Optional: add a small visual press effect without emitting events
	// Mantenemos solo el efecto visual que no interfiere con la acción:
	btn.addEventListener('pointerup', ()=> btn.classList.remove('active'));
	btn.addEventListener('pointerleave', ()=> btn.classList.remove('active'));
	
	// Si queremos un efecto visual más simple:
	btn.addEventListener('pointerdown', ()=> {
        // No hacemos nada en pointerdown para no interferir con sidebar.component.js
    });
	// --- FIN DEL CÓDIGO CORREGIDO ---
})();