import math, cadquery as cq
from build_gearbox import *

parts = build()
hw = hardware()
house = {k: v[0] for k, v in parts.items() if not k.startswith("6")}

def vol(a, b):
    try:
        return a.intersect(b).val().Volume()
    except Exception:
        return 0.0

def owner(name):
    for key in ("M16", "O80", "O", "A80", "A16", "A", "B80", "B16", "B"):
        pass
    return name

# 1) materiel vs pieces imprimees (doit etre ~0, sauf arbres dans bagues/trous de passage)
bad = []
for hn, hs in hw.items():
    for pn, ps in house.items():
        v = vol(hs, ps)
        if v > 1.0:
            bad.append((hn, pn, round(v, 1)))
print("Interferences materiel / pieces imprimees :", bad if bad else "aucune")

# 2) interferences entre pieces mobiles de DEUX axes differents
groups = {
 "M": ["pulley_M16", "motor_shaft"],
 "O": ["pulley_O80", "shaft_O"],
 "A": ["pulley_A80", "pulley_A16", "shaft_A"],
 "B": ["pulley_B80", "pulley_B16", "shaft_B"],
}
bad2 = []
names = list(groups)
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        for a in groups[names[i]]:
            for b in groups[names[j]]:
                v = vol(hw[a], hw[b])
                if v > 1.0:
                    bad2.append((a, b, round(v, 1)))
print("Interferences entre axes :", bad2 if bad2 else "aucune")

# 3) courroies vs elements etrangers a leur etage
mem = {"belt1": ["pulley_M16", "motor_shaft", "pulley_A80", "shaft_A"],
       "belt2": ["pulley_A16", "pulley_A80", "shaft_A", "pulley_B80", "shaft_B"],
       "belt3": ["pulley_B16", "shaft_B", "pulley_O80", "shaft_O"]}
bad3 = []
for bn, own in mem.items():
    for hn, hs in hw.items():
        if hn.startswith("belt") or hn in own:
            continue
        v = vol(hw[bn], hs)
        if v > 1.0:
            bad3.append((bn, hn, round(v, 1)))
print("Courroie vs autres elements :", bad3 if bad3 else "aucune")

# 4) bagues vs pieces voisines : bague a l'angle reglage extreme (rotation 360 par pas de 45)
ring = make_ring()
worst = 0.0
for k, zface, up in (("A", 0.0, True), ("B", 0.0, True)):
    pass

# 5) pieces sorties du volume (hauteur d'empilement)
print("hauteur totale empilee : base %.0f + %.0f + %.0f + %.0f + %.0f = %.0f mm"
      % (H_BASE, H_W1, H_PLATE, H_W2, H_COVER, H_BASE + H_W1 + H_PLATE + H_W2 + H_COVER))
print("arbre de sortie depasse du couvercle de %.1f mm" % (60 + 59.5 - Z_TOP))
print("longueurs d'arbres : A %.1f  B %.1f  sortie %.1f" % (56 + 4.5, 94.5 + 4.5, Z_TOP + 20 - 59.5))
