// Traductor de Fraude - Popup Script
document.addEventListener('DOMContentLoaded', function() {
  console.log('Traductor de Fraude cargado');
  
  // Lógica de la extensión
  const contentDiv = document.getElementById('content');
  if (contentDiv) {
    contentDiv.innerHTML = '<p>Extensión lista para detectar fraude</p>';
  }
});
