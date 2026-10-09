// Execute reducteur_125_3D.html hors navigateur avec le VRAI three.js (seul le rendu WebGL est doublure).
// Attrape les ReferenceError/TypeError (page blanche) et controle les maillages.
const fs = require('fs'), vm = require('vm'), path = require('path');
const html = fs.readFileSync(path.join(__dirname, 'reducteur_125_3D.html'), 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
if (scripts.length !== 2) { console.log('ECHEC : 2 scripts attendus, trouves ' + scripts.length); process.exit(1); }

const noop = () => {};
function el(tag) {
  const listeners = {};
  return { tagName: tag, style: {}, dataset: {}, children: [], className: '', innerHTML: '',
    clientWidth: 900, clientHeight: 700, width: 900, height: 700, checked: true, value: '0',
    appendChild(c) { this.children.push(c); return c; },
    listeners, addEventListener(n, f) { (listeners[n] = listeners[n] || []).push(f); },
    setPointerCapture: noop, firstChild: { addEventListener: noop } };
}
const ids = {};
const document = {
  createElement: el, getElementById: id => (ids[id] = ids[id] || el('div')),
  querySelectorAll: () => [el('button')], body: el('body'),
};
let frames = 0;
const win = { devicePixelRatio: 1, innerWidth: 900, innerHeight: 700, addEventListener: noop };
const sandbox = { window: win, document, console, atob: s => Buffer.from(s, 'base64').toString('binary'),
  requestAnimationFrame: () => { frames++; return 0; }, Math, Float32Array, Uint8Array, Array, Object, JSON, Date };
sandbox.globalThis = sandbox; win.document = document;
vm.createContext(sandbox);
try {
  vm.runInContext(scripts[0], sandbox, { filename: 'three.min.js' });
  const T = sandbox.THREE || win.THREE;
  if (!T) throw new Error('THREE absent apres chargement de la lib');
  let renders = 0;
  T.WebGLRenderer = function () { return { setPixelRatio: noop, setSize: noop, domElement: el('canvas'),
    render(scene, cam) { renders++; } }; };
  sandbox.THREE = T;
  vm.runInContext(scripts[1], sandbox, { filename: 'page.js', timeout: 30000 });
  // --- test de l'animation : rampes d'acceleration / deceleration et rapports de vitesse
  const dbg = win.__dbg, fire = (id, ev) => (ids[id].listeners[ev] || []).forEach(f => f({}));
  const near = (a, b, tol) => Math.abs(a - b) <= tol;
  const chk = [];
  const run = (sec) => { for (let i = 0; i < sec * 100; i++) dbg.step(0.01); };
  ids.rpm.value = '60'; ids.acc.value = '60'; ids.dec.value = '30';
  run(1); chk.push(['arret : reste a 0', dbg.cur === 0]);
  fire('run', 'click'); run(0.5); chk.push(['acceleration 60 tr/min/s apres 0.5 s = 30', near(dbg.cur, 30, 0.5)]);
  run(1); chk.push(['plafonne a la consigne 60', dbg.cur === 60]);
  ids.acc.value = '600'; fire('run', 'click'); run(1);
  chk.push(['deceleration 30 tr/min/s apres 1 s = 30', near(dbg.cur, 30, 0.5)]);
  run(1.5); chk.push(['arret complet', dbg.cur === 0]);
  fire('dir', 'click'); fire('run', 'click'); run(2);
  chk.push(['sens inverse = -60', dbg.cur === -60]);
  const by = n => dbg.items.find(i => i.name.indexOf(n) >= 0);
  const r = n => by(n).mesh.rotation.y / dbg.ph;
  chk.push(['axe A = -1/5', near(r('80T axe A'), -1/5, 1e-6)]);
  chk.push(['axe B = +1/25', near(r('80T axe B'), 1/25, 1e-6)]);
  chk.push(['sortie = -1/125', near(r('Arbre de sortie'), -1/125, 1e-6)]);
  chk.push(['moteur = 1', near(r('16T moteur'), 1, 1e-6)]);
  chk.push(['carter immobile', by('Couvercle').mesh.rotation.y === 0]);
  chk.forEach(c => console.log((c[1] ? 'OK     ' : 'ECHEC  ') + c[0]));
  if (chk.some(c => !c[1])) { console.log("ECHEC des tests d'animation"); process.exit(1); }
  console.log('OK : la page s\'execute sans erreur, three.js r' + T.REVISION);
  console.log('rendu initial : ' + renders + ' image(s), boucle d\'animation armee : ' + (frames > 0));
  // controle des maillages via le groupe 'world' : on rejoue le decodage
  const data = JSON.parse(scripts[1].match(/var DATA = (\{[\s\S]*?\});\s*var GROUPS/)[1]);
  let tri = 0, bad = 0;
  const box = { min: [1e9, 1e9, 1e9], max: [-1e9, -1e9, -1e9] };
  for (const c of data.comps) {
    const b = Buffer.from(c.pos, 'base64'); const arr = new Float32Array(b.buffer, b.byteOffset, b.length / 4);
    if (arr.length !== c.n * 3) bad++;
    for (let i = 0; i < arr.length; i += 3) for (let k = 0; k < 3; k++) {
      if (!isFinite(arr[i + k])) bad++;
      box.min[k] = Math.min(box.min[k], arr[i + k]); box.max[k] = Math.max(box.max[k], arr[i + k]);
    }
    tri += c.n / 3;
  }
  console.log('composants : ' + data.comps.length + ', triangles : ' + tri + ', anomalies : ' + bad);
  console.log('boite englobante (three, mm) : x ' + box.min[0].toFixed(0) + '..' + box.max[0].toFixed(0) +
    '  y ' + box.min[1].toFixed(0) + '..' + box.max[1].toFixed(0) + '  z ' + box.min[2].toFixed(0) + '..' + box.max[2].toFixed(0));
} catch (e) {
  console.log('ERREUR A L\'EXECUTION : ' + e.constructor.name + ' : ' + e.message);
  console.log((e.stack || '').split('\n').slice(1, 5).join('\n'));
  process.exit(1);
}
