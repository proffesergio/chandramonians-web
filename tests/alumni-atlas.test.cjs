const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
class Element {
  constructor(attrs = {}) { this.attrs = attrs; this.children = []; this.listeners = {}; this.hidden = true; }
  getAttribute(key) { return this.attrs[key]; }
  setAttribute(key, value) { this.attrs[key] = value; }
  removeAttribute(key) { delete this.attrs[key]; }
  addEventListener(key, fn) { this.listeners[key] = fn; }
  append(...items) { this.children.push(...items); }
  replaceChildren() { this.children = []; }
  focus() { this.focused = true; }
}
function setup({ shared = true } = {}) {
  const ids = Object.fromEntries(['atlasProfiles', 'atlasDetail', 'atlasDetailTitle', 'atlasDetailSummary', 'atlasPeople', 'atlasTools', 'atlasReset', 'atlasClose'].map(id => [id, new Element()]));
  ids.atlasProfiles.textContent = JSON.stringify(shared ? { BGD: [{ name: '<script>private markup</script>', batch: '2001', profession: 'Teacher', photo: 'https://tracker.invalid/photo.jpg' }] } : {});
  const marker = new Element({ href: '?country=BGD', 'aria-label': 'Bangladesh: 1 alumni' });
  marker.querySelector = () => new Element({ cx: '750', cy: '250' });
  const svg = new Element({ viewBox: '0 0 1000 500' });
  svg.querySelectorAll = () => shared ? [marker] : [];
  const context = {
    document: { querySelector: () => svg, getElementById: id => ids[id], createElement: () => new Element(), documentElement: { dataset: {} } },
    window: { location: { href: 'https://www.chandramonians.com/alumni-map/', search: '' }, matchMedia: () => ({ matches: true }) },
    URL, URLSearchParams, cancelAnimationFrame: () => {}, requestAnimationFrame: () => { throw Error('Reduced motion must bypass animation'); },
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../static/assets/js/alumni-atlas.js'), 'utf8'), context);
  return { ids, marker, svg };
}
test('cluster zoom opens safe profile details and reset restores the world', () => {
  const { ids, marker, svg } = setup();
  let prevented = false;
  marker.listeners.click({ preventDefault: () => { prevented = true; } });
  assert.equal(prevented, true);
  assert.equal(svg.getAttribute('viewBox'), '570 160 360 180');
  assert.equal(ids.atlasDetail.hidden, false);
  const card = ids.atlasPeople.children[0];
  assert.equal(card.children[0].textContent, '<script>private markup</script>', 'Profile text must be assigned as text, not HTML');
  assert.equal(card.children.length, 3, 'External avatar URL must not be loaded');
  assert.equal(card.children[2].disabled, true);
  ids.atlasClose.listeners.click();
  assert.equal(ids.atlasDetail.hidden, true);
  assert.equal(svg.getAttribute('viewBox'), '0 0 1000 500');
  assert.equal(marker.focused, true);
});
test('no shared countries leaves map controls hidden', () => {
  const { ids } = setup({ shared: false });
  assert.equal(ids.atlasTools.hidden, true);
});
test('modified click preserves original country link navigation', () => {
  const { marker, ids } = setup();
  marker.listeners.click({ ctrlKey: true, preventDefault: () => assert.fail('Modified links should remain usable') });
  assert.equal(ids.atlasDetail.hidden, true);
});
