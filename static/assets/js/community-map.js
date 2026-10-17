/* The administrative home-area coordinate is from GeoNames 7645492.
   It is deliberately not presented as the school's exact campus pin. */
(() => {
  const button = document.getElementById('loadCommunityMap');
  if (!button) return;
  const status = document.getElementById('communityMapStatus');
  const canvas = document.getElementById('communityHomeMap');
  const intro = document.getElementById('communityMapIntro');
  let map;
  button.addEventListener('click', async () => {
    button.disabled = true;
    status.textContent = 'Loading the Homna map…';
    try {
      if (!window.L) {
        await Promise.all([
          new Promise((resolve, reject) => {
            const css = document.createElement('link');
            css.rel = 'stylesheet';
            css.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
            css.onload = resolve;
            css.onerror = reject;
            document.head.appendChild(css);
          }),
          new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
          }),
        ]);
      }
      intro.hidden = true;
      intro.style.display = 'none';
      canvas.hidden = false;
      if (!map) {
        map = L.map(canvas, { scrollWheelZoom: false }).setView([23.66, 90.79], 11);
        const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 19,
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        }).addTo(map);
        tiles.on('tileerror', () => {
          status.textContent = 'Some map tiles could not load. You can use the OpenStreetMap link below.';
        });
        L.circle([23.66, 90.79], { radius: 4000, color: '#176b55', weight: 1, fillOpacity: 0.08 }).addTo(map);
        L.marker([23.66, 90.79], {
          icon: L.divIcon({ className: 'community-map-pin', iconSize: [20, 20], iconAnchor: [10, 10] }),
          title: 'Homna home area',
        }).addTo(map).bindPopup('<strong>Our home: Homna, Cumilla</strong><br>Approximate home area, rather than an exact campus location.');
      }
      map.invalidateSize();
      status.textContent = 'Explore the Homna area. Alumni locations are not shared on this map.';
    } catch (error) {
      button.disabled = false;
      status.textContent = 'The map could not load. Please retry or open the OpenStreetMap link below.';
    }
  });
})();
