/* Progressive country clusters: original country links still work without JS. */
(() => {
  'use strict';
  const svg = document.querySelector('.alumni-atlas svg');
  const source = document.getElementById('atlasProfiles');
  const panel = document.getElementById('atlasDetail');
  if (!svg || !source || !panel) return;
  let profiles;
  try { profiles = JSON.parse(source.textContent); } catch { return; }
  const markers = [...svg.querySelectorAll('.atlas-marker')];
  if (!markers.length) return;
  const title = document.getElementById('atlasDetailTitle');
  const summary = document.getElementById('atlasDetailSummary');
  const people = document.getElementById('atlasPeople');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let frame = null;
  let selected = null;
  const world = [0, 0, 1000, 500];
  const setView = target => {
    if (frame !== null) cancelAnimationFrame(frame);
    frame = null;
    if (reduceMotion.matches || document.documentElement.dataset.motion === 'paused') {
      svg.setAttribute('viewBox', target.join(' '));
      return;
    }
    const from = svg.getAttribute('viewBox').trim().split(/\s+/).map(Number);
    let start;
    const animate = now => {
      start ??= now;
      const progress = Math.min((now - start) / 650, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      svg.setAttribute('viewBox', target.map((value, index) => from[index] + (value - from[index]) * eased).join(' '));
      frame = progress < 1 ? requestAnimationFrame(animate) : null;
    };
    frame = requestAnimationFrame(animate);
  };
  function reset() {
    panel.hidden = true;
    markers.forEach(marker => marker.removeAttribute('aria-current'));
    setView(world);
    selected?.focus();
    selected = null;
  }
  function show(marker, focusPanel = true) {
    const code = new URL(marker.getAttribute('href'), window.location.href).searchParams.get('country');
    const rows = profiles[code];
    if (!Array.isArray(rows)) return;
    selected = marker;
    markers.forEach(item => item.removeAttribute('aria-current'));
    marker.setAttribute('aria-current', 'true');
    const circle = marker.querySelector('circle');
    const x = Number(circle.getAttribute('cx'));
    const y = Number(circle.getAttribute('cy'));
    setView([Math.max(0, Math.min(640, x - 180)), Math.max(0, Math.min(320, y - 90)), 360, 180]);
    title.textContent = marker.getAttribute('aria-label').split(':')[0];
    summary.textContent = `${rows.length} ${rows.length === 1 ? 'alumnus shares' : 'alumni share'} this country in the current search.`;
    people.replaceChildren();
    for (const person of rows) {
      const card = document.createElement('article');
      card.className = 'atlas-person';
      if (person.photo) {
        const photoUrl = new URL(person.photo, window.location.href);
        if (photoUrl.origin === window.location.origin) {
          const img = document.createElement('img');
          img.src = photoUrl.href; img.alt = ''; img.width = 48; img.height = 48; img.loading = 'lazy';
          card.append(img);
        }
      }
      const heading = document.createElement('h3');
      heading.textContent = person.name;
      const details = document.createElement('p');
      details.textContent = [person.batch ? `Batch of ${person.batch}` : '', person.profession].filter(Boolean).join(' · ');
      const chat = document.createElement('button');
      chat.type = 'button'; chat.disabled = true;
      chat.textContent = 'Chat for help or support · Coming soon';
      card.append(heading, details, chat);
      if (person.profile_url) {
        const link = document.createElement('a');
        const url = new URL(person.profile_url, window.location.href);
        if (url.origin === window.location.origin) {
          link.href = url.href;
          link.textContent = 'View public profile →';
          card.append(link);
        }
      }
      people.append(card);
    }
    panel.hidden = false;
    if (focusPanel) panel.focus({ preventScroll: true });
  }
  document.getElementById('atlasTools').hidden = false;
  document.getElementById('atlasReset').addEventListener('click', reset);
  document.getElementById('atlasClose').addEventListener('click', reset);
  panel.addEventListener('keydown', event => { if (event.key === 'Escape') reset(); });
  for (const marker of markers) {
    marker.addEventListener('click', event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault(); show(marker);
    });
  }
  const country = new URLSearchParams(window.location.search).get('country');
  const initial = markers.find(marker => new URL(marker.getAttribute('href'), window.location.href).searchParams.get('country') === country);
  if (initial) show(initial, false);
})();
