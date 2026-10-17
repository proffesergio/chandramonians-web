const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

class Element {
  constructor(attrs = {}) { this.attrs = { ...attrs }; this.dataset = {}; this.listeners = {}; this.hidden = false; this.classes = new Set(); this.classList = { add: (s) => this.classes.add(s), remove: (s) => this.classes.delete(s), toggle: (s, on) => on ? this.classes.add(s) : this.classes.delete(s) }; }
  setAttribute(k, v) { this.attrs[k] = v; }
  getAttribute(k) { return this.attrs[k]; }
  hasAttribute(k) { return k in this.attrs; }
  set src(v) { this.attrs.src = v; }
  get src() { return this.attrs.src; }
  addEventListener(k, fn) { this.listeners[k] = fn; }
  fire(k, event = {}) { this.listeners[k]?.(event); }
  focus() { this.focused = true; }
}

function setup({ reduced = false, deniedStorage = false } = {}) {
  const root = new Element();
  const elements = Object.fromEntries(['textSizeToggle','motionToggle','primaryNavigation','loadCommunityMap','communityMapDetail','communityHomeMap','communityMapStatus'].map(id => [id, new Element()]));
  const menuButton = new Element({ 'aria-expanded': 'false' });
  const tabs = ['teaching', 'seminar', 'project'].map((name, i) => {
    const tab = new Element({ 'aria-controls': `${name}Panel`, 'aria-selected': String(i === 0) });
    const panel = new Element(); panel.hidden = i !== 0; elements[`${name}Panel`] = panel; return tab;
  });
  elements.communityMapDetail.hidden = true;
  elements.communityHomeMap.dataset.src = 'https://www.openstreetmap.org/export/embed.html?layer=mapnik';
  elements.loadCommunityMap.setAttribute('aria-expanded', 'false');
  const saved = new Map();
  const media = { matches: reduced, addEventListener: () => {} };
  const context = {
    document: { documentElement: root, getElementById: id => elements[id], querySelector: () => menuButton, querySelectorAll: () => tabs },
    localStorage: { getItem: key => { if (deniedStorage) throw Error('Storage disabled'); return saved.get(key); }, setItem: (key, value) => { if (deniedStorage) throw Error('Storage disabled'); saved.set(key, value); } },
    window: { matchMedia: () => media },
  };
  return { context, root, elements, menuButton, tabs, saved };
}
const run = (file, context) => vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../static/assets/js', file), 'utf8'), context);

test('programme tabs update panels and support keyboard navigation', () => {
  const state = setup(); run('community-public.js', state.context);
  state.tabs[1].fire('click');
  assert.equal(state.elements.teachingPanel.hidden, true);
  assert.equal(state.elements.seminarPanel.hidden, false);
  assert.equal(state.tabs[1].getAttribute('aria-selected'), 'true');
  state.tabs[1].fire('keydown', { key: 'ArrowRight', preventDefault() {} });
  assert.equal(state.elements.projectPanel.hidden, false);
  assert.equal(state.tabs[2].focused, true);
});

test('reading settings persist and mobile menu opens and closes', () => {
  const state = setup(); run('community-public.js', state.context);
  state.elements.textSizeToggle.fire('click');
  assert.equal(state.root.dataset.readingSize, 'large');
  assert.equal(state.saved.get('chandramonians-text-size'), 'large');
  state.elements.motionToggle.fire('click');
  assert.equal(state.root.dataset.motion, 'paused');
  state.menuButton.fire('click');
  assert.equal(state.elements.primaryNavigation.classes.has('is-open'), true);
  state.elements.primaryNavigation.fire('keydown', { key: 'Escape' });
  assert.equal(state.menuButton.getAttribute('aria-expanded'), 'false');
});

test('device reduced-motion preference wins and denied storage is tolerated', () => {
  const state = setup({ reduced: true, deniedStorage: true }); run('community-public.js', state.context);
  assert.equal(state.root.dataset.motion, 'paused');
  assert.equal(state.elements.motionToggle.disabled, true);
  assert.doesNotThrow(() => state.elements.textSizeToggle.fire('click'));
});

test('map detail opens without a third-party JavaScript loader and retains its source on reopen', () => {
  const state = setup(); run('community-map.js', state.context);
  assert.equal(state.elements.communityHomeMap.src, undefined);
  state.elements.loadCommunityMap.fire('click');
  assert.equal(state.elements.communityMapDetail.hidden, false);
  assert.equal(state.elements.loadCommunityMap.getAttribute('aria-expanded'), 'true');
  const src = state.elements.communityHomeMap.src;
  assert.match(src, /^https:\/\/www.openstreetmap.org\//);
  state.elements.loadCommunityMap.fire('click');
  assert.equal(state.elements.communityMapDetail.hidden, true);
  state.elements.loadCommunityMap.fire('click');
  assert.equal(state.elements.communityHomeMap.src, src);
});
