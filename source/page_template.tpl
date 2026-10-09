<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reducteur 125:1 HTD3M - assemblage 3D</title>
<style>
  :root{--bg:#14171c;--panel:#1d2128;--fg:#e8eaee;--mut:#9aa3b2;--acc:#e8892b;--line:#2c323c}
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;background:var(--bg);color:var(--fg);font:14px/1.4 system-ui,Segoe UI,sans-serif;overflow:hidden}
  #view{position:fixed;inset:0}
  canvas{display:block;touch-action:none}
  #panel{position:fixed;top:12px;left:12px;width:262px;max-height:calc(100% - 24px);overflow:auto;background:var(--panel);
    border:1px solid var(--line);border-radius:10px;padding:12px 14px}
  h1{font-size:15px;margin:0 0 2px}
  .sub{color:var(--mut);font-size:12px;margin-bottom:10px}
  h2{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);margin:12px 0 6px}
  label.row{display:flex;align-items:center;gap:8px;padding:2px 0;cursor:pointer}
  .sw{width:11px;height:11px;border-radius:3px;flex:none;border:1px solid #0006}
  input[type=checkbox]{accent-color:var(--acc)}
  input[type=range]{width:100%;accent-color:var(--acc)}
  .btns{display:flex;flex-wrap:wrap;gap:6px}
  button{background:#262c36;color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:5px 9px;font:inherit;cursor:pointer}
  button:hover{border-color:var(--acc)}
  .kv{display:grid;grid-template-columns:auto 1fr;gap:2px 10px;font-size:12px}
  .kv b{color:var(--mut);font-weight:500}
  .sl{display:flex;justify-content:space-between;font-size:12px;margin-top:8px}
  .sl b{color:var(--acc);font-weight:600;font-variant-numeric:tabular-nums}
  #live{margin-top:8px;font-variant-numeric:tabular-nums}
  button.on{background:var(--acc);color:#111;border-color:var(--acc)}
  #tbl{position:fixed;right:14px;bottom:34px;width:min(430px,calc(100% - 28px));max-height:58%;overflow:auto;background:var(--panel);
    border:1px solid var(--line);border-radius:10px;font-size:12px}
  #tbl summary{cursor:pointer;padding:8px 12px;font-weight:600;position:sticky;top:0;background:var(--panel);border-radius:10px}
  #tbl table{width:100%;border-collapse:collapse;margin:0 0 6px}
  #tbl th{text-align:left;color:var(--acc);font-size:11px;letter-spacing:.06em;text-transform:uppercase;padding:8px 12px 3px}
  #tbl td{padding:2px 12px;border-top:1px solid var(--line);vertical-align:top}
  #tbl td:first-child{color:var(--mut);width:46%}
  #tbl td:last-child{font-variant-numeric:tabular-nums}
  #hint{position:fixed;right:14px;bottom:10px;color:var(--mut);font-size:12px;text-align:right}
  @media (max-width:640px){#panel{width:calc(100% - 24px);max-height:42%}}
</style>
</head>
<body>
<div id="view"></div>
<details id="tbl" open><summary>Cotes (mm)</summary><table id="tblb"></table></details>
<div id="panel">
  <h1>Reducteur 125:1 &mdash; HTD 3M</h1>
  <div class="sub">3 etages 80T/16T &middot; disposition en triangle &middot; sortie coaxiale</div>
  <h2>Pieces</h2><div id="groups"></div>
  <h2>Eclate</h2><input id="explode" type="range" min="0" max="45" value="0" step="1">
  <h2>Boitier transparent</h2><input id="ghost" type="range" min="0" max="85" value="0" step="1">
  <h2>Rotation</h2>
  <div class="btns"><button id="run">&#9654; Marche</button><button id="dir">Sens : horaire</button></div>
  <div class="sl"><span>Vitesse moteur</span><b id="v_rpm">60 tr/min</b></div>
  <input id="rpm" type="range" min="1" max="300" value="60" step="1">
  <div class="sl"><span>Acceleration</span><b id="v_acc">60 tr/min/s</b></div>
  <input id="acc" type="range" min="5" max="600" value="60" step="5">
  <div class="sl"><span>Deceleration</span><b id="v_dec">60 tr/min/s</b></div>
  <input id="dec" type="range" min="5" max="600" value="60" step="5">
  <div class="kv" id="live"></div>
  <h2>Vues</h2>
  <div class="btns"><button data-v="iso">Iso</button><button data-v="top">Dessus</button><button data-v="front">Face</button><button data-v="side">Cote</button></div>
  <h2>Donnees</h2>
  <div class="kv" id="kv"></div>
</div>
<div id="hint">glisser : tourner &middot; molette : zoom &middot; clic droit / Maj : deplacer</div>
<script>__THREE__</script>
<script>
(function(){
var DATA = __DATA__;
var GROUPS = [["base","Base + moteur"],["murs12","Murs etages 1+2 (46)"],["plaque","Plaque"],["murs3","Murs etage 3 (21)"],
  ["couvercle","Couvercle"],["bagues","Bagues excentriques"],["roulements","Roulements 688"],["poulies","Poulies"],
  ["courroies","Courroies"],["arbres","Arbres"],["moteur","Moteur NEMA 17"],["visserie","Tiges + ecrous M3"]];
var MAT = {base:[0.62,0.0],murs12:[0.62,0.0],plaque:[0.62,0.0],murs3:[0.62,0.0],couvercle:[0.62,0.0],bagues:[0.55,0.0],
  roulements:[0.3,0.65],poulies:[0.38,0.55],courroies:[0.92,0.0],arbres:[0.22,0.75],moteur:[0.5,0.35],visserie:[0.35,0.6]};
var GHOSTED = {base:1,murs12:1,plaque:1,murs3:1,couvercle:1};

var host = document.getElementById('view');
var renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
renderer.setSize(host.clientWidth||window.innerWidth, host.clientHeight||window.innerHeight);
host.appendChild(renderer.domElement);
var scene = new THREE.Scene();
scene.background = new THREE.Color(0x14171c);
var camera = new THREE.PerspectiveCamera(38, (host.clientWidth||1)/(host.clientHeight||1), 1, 3000);
scene.add(new THREE.HemisphereLight(0xdfe8ff, 0x2a2e38, 1.0));
scene.add(new THREE.AmbientLight(0xffffff, 0.25));
var d1 = new THREE.DirectionalLight(0xffffff, 0.9); d1.position.set(200,300,150); scene.add(d1);
var d2 = new THREE.DirectionalLight(0xffffff, 0.35); d2.position.set(-250,120,-200); scene.add(d2);

var ax = DATA.meta.axes;
var cx = (ax.O[0]+ax.A[0]+ax.B[0])/3, cy = (ax.O[1]+ax.A[1]+ax.B[1])/3;
var target = new THREE.Vector3(cx, 45, -cy);

var world = new THREE.Group(); scene.add(world);
var items = [];
function decode(b64){
  var bin = atob(b64), n = bin.length, u = new Uint8Array(n);
  for (var i=0;i<n;i++) u[i] = bin.charCodeAt(i);
  return new Float32Array(u.buffer);
}
DATA.comps.forEach(function(c){
  var g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(decode(c.pos), 3));
  g.computeVertexNormals();
  var P = MAT[c.group] || [0.6,0.1];
  var m = new THREE.MeshStandardMaterial({color:new THREE.Color(c.color), roughness:P[0], metalness:P[1]});
  var mesh = new THREE.Mesh(g, m);
  if (c.ax) mesh.position.set(c.ax[0], 0, c.ax[1]);
  world.add(mesh);
  items.push({mesh:mesh, group:c.group, lvl:c.lvl, name:c.name, spd:c.spd, ax:c.ax});
});

// sol
var ground = new THREE.Mesh(new THREE.CircleGeometry(520, 64), new THREE.MeshStandardMaterial({color:new THREE.Color(0x1a1e25), roughness:1, metalness:0}));
ground.rotation.x = -Math.PI/2; ground.position.set(cx, -51, -cy); scene.add(ground);

var gbox = document.getElementById('groups'), visible = {};
GROUPS.forEach(function(g){
  var col = '#888';
  for (var i=0;i<DATA.comps.length;i++) if (DATA.comps[i].group===g[0]) { col = DATA.comps[i].color; break; }
  visible[g[0]] = true;
  var l = document.createElement('label'); l.className = 'row';
  l.innerHTML = '<input type="checkbox" checked><span class="sw" style="background:'+col+'"></span><span>'+g[1]+'</span>';
  l.firstChild.addEventListener('change', function(e){ visible[g[0]] = e.target.checked; refresh(); });
  gbox.appendChild(l);
});
var kv = document.getElementById('kv');
[['Reduction','5 x 5 x 5 = 125:1'],['Entraxe',DATA.meta.C+' mm'],['Courroie','HTD 3M '+DATA.meta.belt+' mm x 10'],
 ['Hauteur','110 mm (+20 d arbre)'],['Roulements','688 (8x16x5)'],['Arbres','acier 8 mm']].forEach(function(r){
  kv.innerHTML += '<b>'+r[0]+'</b><span>'+r[1]+'</span>';
});

// ---- tableau des cotes ----
(function(){
  var tb = document.getElementById('tblb'), html = '';
  (DATA.meta.table||[]).forEach(function(g){
    html += '<tr><th colspan="2">'+g[0]+'</th></tr>';
    g[1].forEach(function(r){ html += '<tr><td>'+r[0]+'</td><td>'+r[1]+'</td></tr>'; });
  });
  tb.innerHTML = html;
})();
var explode = document.getElementById('explode'), ghost = document.getElementById('ghost');
function refresh(){
  var e = +explode.value, gh = +ghost.value/100;
  items.forEach(function(it){
    it.mesh.visible = !!visible[it.group];
    it.mesh.position.y = it.lvl*e;
    var m = it.mesh.material;
    if (GHOSTED[it.group]) { m.transparent = gh>0; m.opacity = 1-gh; m.depthWrite = (gh===0); }
  });
}
explode.addEventListener('input', refresh); ghost.addEventListener('input', refresh);
refresh();

var st = {theta:-0.75, phi:1.05, r:430};
function place(){
  st.phi = Math.max(0.02, Math.min(Math.PI-0.02, st.phi));
  st.r = Math.max(60, Math.min(1200, st.r));
  camera.position.set(target.x + st.r*Math.sin(st.phi)*Math.sin(st.theta),
                      target.y + st.r*Math.cos(st.phi),
                      target.z + st.r*Math.sin(st.phi)*Math.cos(st.theta));
  camera.lookAt(target);
}
place();
var VIEWS = {iso:[-0.75,1.05,430], top:[0,0.02,380], front:[0,Math.PI/2,430], side:[Math.PI/2,Math.PI/2,430]};
Array.prototype.forEach.call(document.querySelectorAll('button[data-v]'), function(b){
  b.addEventListener('click', function(){ var v = VIEWS[b.dataset.v]; st.theta=v[0]; st.phi=v[1]; st.r=v[2]; place(); });
});
// parametres d'URL (rendus) : #v=iso|top|front|side & th, ph, r (camera) & e (eclate) & g (transparence) & t=0 (sans tableau) & p=0 (sans panneau)
(function(){
  var H = {};
  (typeof location !== 'undefined' ? location.hash : '').slice(1).split('&').forEach(function(kv){ var a = kv.split('='); if (a[0]) H[a[0]] = a[1]; });
  if (H.v && VIEWS[H.v]) { var v = VIEWS[H.v]; st.theta=v[0]; st.phi=v[1]; st.r=v[2]; }
  if (H.th) st.theta = +H.th; if (H.ph) st.phi = +H.ph; if (H.r) st.r = +H.r;
  if (H.tx) target.x += +H.tx; if (H.ty) target.y += +H.ty; if (H.tz) target.z += +H.tz;
  if (H.e) explode.value = H.e; if (H.g) ghost.value = H.g;
  if (H.t === '0') document.getElementById('tbl').style.display = 'none';
  if (H.p === '0') document.getElementById('panel').style.display = 'none';
  place(); refresh();
})();
var drag = null, el = renderer.domElement;
el.addEventListener('contextmenu', function(e){ e.preventDefault(); });
el.addEventListener('pointerdown', function(e){
  drag = {x:e.clientX, y:e.clientY, pan:(e.button===2||e.shiftKey)};
  if (el.setPointerCapture) el.setPointerCapture(e.pointerId);
});
el.addEventListener('pointermove', function(e){
  if (!drag) return;
  var dx = e.clientX-drag.x, dy = e.clientY-drag.y; drag.x = e.clientX; drag.y = e.clientY;
  if (drag.pan) {
    var k = st.r*0.0016;
    var rx = Math.cos(st.theta), rz = -Math.sin(st.theta);
    target.x -= dx*k*rx; target.z -= dx*k*rz; target.y += dy*k;
  } else { st.theta -= dx*0.008; st.phi -= dy*0.008; }
  place();
});
function up(){ drag = null; }
el.addEventListener('pointerup', up); el.addEventListener('pointercancel', up);
el.addEventListener('wheel', function(e){ e.preventDefault(); st.r *= (e.deltaY>0?1.1:0.9); place(); }, {passive:false});

function resize(){
  var w = host.clientWidth||window.innerWidth, h = host.clientHeight||window.innerHeight;
  renderer.setSize(w,h); camera.aspect = w/h; camera.updateProjectionMatrix();
}
window.addEventListener('resize', resize); resize();
var run = false, dirSign = 1, cur = 0, ph = 0, last = null;
var btnRun = document.getElementById('run'), btnDir = document.getElementById('dir');
var inRpm = document.getElementById('rpm'), inAcc = document.getElementById('acc'), inDec = document.getElementById('dec');
var live = document.getElementById('live');
function labels(){
  document.getElementById('v_rpm').textContent = inRpm.value + ' tr/min';
  document.getElementById('v_acc').textContent = inAcc.value + ' tr/min/s';
  document.getElementById('v_dec').textContent = inDec.value + ' tr/min/s';
}
[inRpm, inAcc, inDec].forEach(function(i){ i.addEventListener('input', labels); }); labels();
btnRun.addEventListener('click', function(){
  run = !run; btnRun.innerHTML = run ? '&#10074;&#10074; Arret' : '&#9654; Marche'; btnRun.className = run ? 'on' : '';
});
btnDir.addEventListener('click', function(){
  dirSign = -dirSign; btnDir.textContent = 'Sens : ' + (dirSign>0 ? 'horaire' : 'anti-horaire');
});
var RATIOS = [['Moteur',1],['Axe A',-1/5],['Axe B',1/25],['Sortie',-1/125]];
function showLive(){
  var h = '';
  RATIOS.forEach(function(r){
    var v = cur*r[1];
    h += '<b>'+r[0]+'</b><span>'+(Math.abs(v)<0.005?'0.00':v.toFixed(Math.abs(v)<1?3:1))+' tr/min</span>';
  });
  live.innerHTML = h;
}
function step(dt){
  var target = run ? dirSign*(+inRpm.value) : 0;
  var speeding = Math.abs(target) > Math.abs(cur) && (cur===0 || (cur>0)===(target>0));
  var rate = (speeding ? +inAcc.value : +inDec.value) * dt;       // tr/min gagnes ou perdus
  if (Math.abs(target-cur) <= rate) cur = target; else cur += (target>cur ? rate : -rate);
  ph += cur * 2*Math.PI/60 * dt;
  items.forEach(function(it){ if (it.spd) it.mesh.rotation.y = ph*it.spd; });
}
window.__dbg = {items:items, step:step, get cur(){return cur;}, get ph(){return ph;}};
var tick = 0;
(function loop(t){
  if (last !== null) { var dt = Math.min(0.1, Math.max(0, (t-last)/1000)); step(dt); }
  last = t;
  if ((tick++ % 6) === 0) showLive();
  renderer.render(scene, camera); requestAnimationFrame(loop);
})(0);
})();
</script>
</body>
</html>
