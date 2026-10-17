(() => {
  const root = document.documentElement;
  root.classList.add('has-site-js');
  const readPreference = (key) => { try { return localStorage.getItem(`chandramonians-${key}`); } catch { return null; } };
  const savePreference = (key, value) => { try { localStorage.setItem(`chandramonians-${key}`, value); } catch { /* Preferences are optional. */ } };
  const sizeButton = document.getElementById('textSizeToggle');
  const applySize = (large) => {
    root.dataset.readingSize = large ? 'large' : 'normal';
    if (sizeButton) { sizeButton.setAttribute('aria-pressed', String(large)); sizeButton.innerHTML = `<span aria-hidden="true">A${large ? '−' : '+'}</span> ${large ? 'Standard text' : 'Larger text'}`; }
  };
  applySize(readPreference('text-size') === 'large');
  sizeButton?.addEventListener('click', () => { const large = root.dataset.readingSize !== 'large'; applySize(large); savePreference('text-size', large ? 'large' : 'normal'); });

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const motionButton = document.getElementById('motionToggle');
  const applyMotion = () => {
    const paused = reducedMotion.matches || readPreference('motion') === 'paused';
    root.dataset.motion = paused ? 'paused' : 'on';
    if (motionButton) {
      motionButton.setAttribute('aria-pressed', String(paused));
      motionButton.textContent = reducedMotion.matches ? 'Reduced motion' : paused ? 'Resume motion' : 'Pause motion';
      motionButton.disabled = reducedMotion.matches;
      motionButton.title = reducedMotion.matches ? 'Reduced motion follows your device settings.' : '';
    }
  };
  applyMotion();
  motionButton?.addEventListener('click', () => { savePreference('motion', root.dataset.motion === 'paused' ? 'on' : 'paused'); applyMotion(); });
  reducedMotion.addEventListener?.('change', applyMotion);

  const menuButton = document.querySelector('.menu-toggle');
  const menu = document.getElementById('primaryNavigation');
  menuButton?.addEventListener('click', () => { const open = menuButton.getAttribute('aria-expanded') !== 'true'; menuButton.setAttribute('aria-expanded', String(open)); menu?.classList.toggle('is-open', open); });
  menu?.addEventListener('keydown', (event) => { if (event.key === 'Escape') { menu.classList.remove('is-open'); menuButton?.setAttribute('aria-expanded', 'false'); menuButton?.focus(); } });

  const tabs = [...document.querySelectorAll('.programme-tabs [role="tab"]')];
  const activateTab = (selected, moveFocus = false) => {
    tabs.forEach((tab) => {
      const active = tab === selected;
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      const panel = document.getElementById(tab.getAttribute('aria-controls'));
      if (panel) panel.hidden = !active;
    });
    if (moveFocus) selected.focus();
  };
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activateTab(tab));
    tab.addEventListener('keydown', (event) => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      else if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = tabs.length - 1;
      if (next !== undefined) { event.preventDefault(); activateTab(tabs[next], true); }
    });
  });
})();
