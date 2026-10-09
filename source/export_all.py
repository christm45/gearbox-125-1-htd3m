import math, os, cadquery as cq
from build_gearbox import *

parts = build()
hw = hardware()

# bagues : (axe, z_face, ouverte_vers_le_haut)
RINGS = [("A", 0.0, True), ("A", Z_PL, False),
         ("B", 0.0, True), ("B", Z_CV, False),
         ("O", Z_PL + H_PLATE, True), ("O", Z_CV, False)]
ring0 = make_ring()
rings, brgs = [], []
for k, zf, up in RINGS:
    ang = math.degrees(math.atan2(OUTV[k][1], OUTV[k][0]))
    px, py = POCKET[k]
    r = ring0
    if up:
        r = r.translate((0, 0, zf - POCKET_H))
    else:
        r = r.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, zf + POCKET_H))
    r = r.rotate((0, 0, 0), (0, 0, 1), ang).translate((px, py, 0))
    rings.append(r)
    nx, ny = NOM[k]
    brgs.append(bearing(nx, ny, zf if up else zf + BRG_H) if not up else bearing(nx, ny, zf))
    if not up:
        brgs[-1] = tube(nx, ny, zf, BRG_OD, BRG_H, BRG_ID)

# verification bagues / roulements / pieces imprimees
house = {k: v[0] for k, v in parts.items() if not k.startswith("6")}
def vol(a, b):
    try: return a.intersect(b).val().Volume()
    except Exception: return 0.0
bad = []
for i, r in enumerate(rings):
    for pn, ps in house.items():
        v = vol(r, ps)
        if v > 0.5: bad.append(("bague%d" % i, pn, round(v, 1)))
    v = vol(r, brgs[i])
    if v > 0.5: bad.append(("bague%d" % i, "roulement", round(v, 1)))
    for hn, hs in hw.items():
        v = vol(r, hs)
        if v > 0.5: bad.append(("bague%d" % i, hn, round(v, 1)))
print("Interferences bagues :", bad if bad else "aucune")

asm = cq.Assembly(name="reducteur_125_triangle")
col = {"1_base": (0.75, 0.75, 0.78), "2_mur_etage_1_2": (0.55, 0.65, 0.85), "3_plaque": (0.75, 0.75, 0.78),
       "4_mur_etage_3": (0.55, 0.65, 0.85), "5_couvercle": (0.75, 0.75, 0.78)}
for n, (s, z0) in parts.items():
    if n.startswith("6"): continue
    asm.add(s, name=n, color=cq.Color(*col[n], 1))
for i, r in enumerate(rings):
    asm.add(r, name="bague%d" % i, color=cq.Color(0.9, 0.5, 0.1, 1))
for i, b in enumerate(brgs):
    asm.add(b, name="roulement688_%d" % i, color=cq.Color(0.3, 0.3, 0.3, 1))
for n, s in hw.items():
    c = (0.2, 0.2, 0.2) if n.startswith("belt") else (0.85, 0.85, 0.2) if n.startswith("pulley") else (0.6, 0.6, 0.65)
    asm.add(s, name=n, color=cq.Color(*c, 1))
asm.save(os.path.join(OUT, "assemblage_complet.step"))
for n, (s, z0) in parts.items():
    flat = s.translate((0, 0, -z0)) if z0 else s
    cq.exporters.export(flat, os.path.join(OUT, n + ".step"))
print("STEP ok")
for n, (s, z0) in build_variants().items():
    flat = s.translate((0, 0, -z0)) if z0 else s
    cq.exporters.export(flat, os.path.join(OUT, n + ".step"))
print("STEP variantes AZ ok")
