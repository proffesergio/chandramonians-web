/* A local geographic overview is always visible. The optional detailed map
   loads as an OpenStreetMap embed without an external JavaScript dependency. */
(() => {
  const button = document.getElementById('loadCommunityMap');
  const detail = document.getElementById('communityMapDetail');
  const frame = document.getElementById('communityHomeMap');
  const status = document.getElementById('communityMapStatus');
  if (!button || !detail || !frame || !status) return;
  button.addEventListener('click', () => {
    const expanded = button.getAttribute('aria-expanded') !== 'true';
    button.setAttribute('aria-expanded', String(expanded));
    detail.hidden = !expanded;
    button.textContent = expanded ? 'Hide the local map' : 'Explore the local map ↗';
    if (expanded && !frame.hasAttribute('src')) {
      frame.src = frame.dataset.src;
      status.textContent = 'The detailed map uses OpenStreetMap. If it is unavailable, use either map link above.';
    }
  });
})();
