// This script simply re-dispatches a semantic event when the send button is clicked
// send-button stub: keep file for styling/structure but avoid dispatching a redundant event.
// The sidebar is the authoritative sender and dispatches `message:send`.
(function(){
	// Intentionally do not add a click handler that dispatches events.
	// This prevents duplicate send events when both sidebar and this button attach listeners.
	const btn = document.getElementById('send-button');
	if(!btn) return;
	// Optional: add a small visual press effect without emitting events
	btn.addEventListener('pointerdown', ()=> btn.classList.add('active'));
	btn.addEventListener('pointerup', ()=> btn.classList.remove('active'));
	btn.addEventListener('pointerleave', ()=> btn.classList.remove('active'));
})();
