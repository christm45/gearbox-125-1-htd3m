"""Tessele l'assemblage et ecrit meshes.json (positions float32 en base64, repere Y vers le haut)."""
import json, base64, math, struct, os
import cadquery as cq
from build_gearbox import *
import realistic as R

parts = build()
if os.environ.get("VARIANT") == "AZ":      # rendu de la variante AZ (couvercle a languettes, base sans oreillons)
    _v = build_variants()
    parts["1_base"] = _v["1_base_AZ_sans_oreillons"]
    parts["5_couvercle"] = _v["5_couvercle_AZ"]
hw = hardware()
# versions realistes pour l'affichage (enveloppes conservees pour les tests d'interference)
hw["pulley_M16"] = R.tpulley(O[0], O[1], ZC1, False, NS, 5.0)
hw["pulley_A80"] = R.tpulley(A[0], A[1], ZC1, True, NB, 8.0)
hw["pulley_A16"] = R.tpulley(A[0], A[1], ZC2, False, NS, 8.0)
hw["pulley_B80"] = R.tpulley(B[0], B[1], ZC2, True, NB, 8.0)
hw["pulley_B16"] = R.tpulley(B[0], B[1], ZC3, False, NS, 8.0)
hw["pulley_O80"] = R.tpulley(O[0], O[1], ZC3, False, NB, 8.0)
rb = D16 / 2 + 2.0
hw["belt1"] = R.hollow_belt(O, A, rb, RB80, ZC1)
hw["belt2"] = R.hollow_belt(A, B, rb, RB80, ZC2)
hw["belt3"] = R.hollow_belt(B, O, rb, RB80, ZC3)
del hw["motor_shaft"]
comps = []   # (nom, groupe, couleur, niveau d'eclatement, shape)

def add(name, grp, col, lvl, shp, axis=None, spd=None):
    comps.append((name, grp, col, lvl, shp, axis, spd))

add("Base + support moteur", "base", "#b9bcc4", 0.0, parts["1_base"][0])
add("Murs etages 1+2 (%d mm)" % H_W1 + "", "murs12", "#7da2da", 1.0, parts["2_mur_etage_1_2"][0])
add("Plaque de separation", "plaque", "#b9bcc4", 2.0, parts["3_plaque"][0])
add("Murs etage 3 (%d mm)" % H_W2 + "", "murs3", "#7da2da", 3.0, parts["4_mur_etage_3"][0])
add("Couvercle", "couvercle", "#b9bcc4", 4.0, parts["5_couvercle"][0])

RINGS = [("A", 0.0, True, 0.0), ("A", Z_PL, False, 2.0), ("B", 0.0, True, 0.0),
         ("B", Z_CV, False, 4.0), ("O", Z_PL + H_PLATE, True, 2.0), ("O", Z_CV, False, 4.0)]
ring0 = make_ring()
for i, (k, zf, up, lvl) in enumerate(RINGS):
    ang = math.degrees(math.atan2(OUTV[k][1], OUTV[k][0]))
    px, py = POCKET[k]
    r = ring0.translate((0, 0, zf - POCKET_H)) if up else \
        ring0.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, zf + POCKET_H))
    r = r.rotate((0, 0, 0), (0, 0, 1), ang).translate((px, py, 0))
    add("Bague excentrique %s%d" % (k, i), "bagues", "#e8892b", lvl, r)
    nx, ny = NOM[k]
    b = bearing(nx, ny, zf) if up else tube(nx, ny, zf, BRG_OD, BRG_H, BRG_ID)
    add("Roulement 688 %s%d" % (k, i), "roulements", "#4a4d55", lvl, b)

# axe de rotation et rapport de vitesse (moteur = 1) ; chaque etage inverse le sens
SPIN = {"pulley_M16": ("O", 1.0), "pulley_A80": ("A", -1 / 5), "pulley_A16": ("A", -1 / 5), "shaft_A": ("A", -1 / 5),
        "pulley_B80": ("B", 1 / 25), "pulley_B16": ("B", 1 / 25), "shaft_B": ("B", 1 / 25),
        "pulley_O80": ("O", -1 / 125), "shaft_O": ("O", -1 / 125)}
lv = {"pulley_M16": 1.0, "pulley_A80": 1.0, "belt1": 1.0, "pulley_A16": 1.0, "pulley_B80": 1.0, "belt2": 1.0,
      "pulley_B16": 3.0, "pulley_O80": 3.0, "belt3": 3.0, "shaft_A": 0.0, "shaft_B": 0.0, "shaft_O": 2.0,
      }
nice = {"pulley_M16": "Poulie 16T moteur", "pulley_A80": "Poulie 80T axe A (etage 1)", "pulley_A16": "Poulie 16T axe A (etage 2)",
        "pulley_B80": "Poulie 80T axe B (etage 2)", "pulley_B16": "Poulie 16T axe B (etage 3)",
        "pulley_O80": "Poulie 80T sortie (etage 3)", "belt1": "Courroie HTD3M etage 1", "belt2": "Courroie HTD3M etage 2",
        "belt3": "Courroie HTD3M etage 3", "shaft_A": "Arbre acier 8 mm A", "shaft_B": "Arbre acier 8 mm B",
        "shaft_O": "Arbre de sortie 8 mm", "motor_shaft": "Arbre moteur 5 mm"}
for n, s in hw.items():
    if n.startswith("belt"):  g, c = "courroies", "#2b2b2f"
    elif n.startswith("pulley"): g, c = "poulies", "#e6d34a"
    else: g, c = "arbres", "#c9ccd2"
    ax_, sp_ = SPIN.get(n, (None, None))
    add(nice[n], g, c, lv[n], s, ax_, sp_)

add("Moteur NEMA 17", "moteur", "#2f3138", 0.0, R.motor())
add("Arbre moteur 5 mm", "arbres", "#c9ccd2", 0.0, R.motor_shaft(), "O", 1.0)
for i, (kind, shp) in enumerate(R.rods_and_nuts()):
    top = kind == "ecrou" and i % 3 == 2
    add("Tige M3" if kind == "tige" else "Ecrou M3", "visserie", "#aeb2ba", 4.0 if top else 0.0, shp)

out = []
for name, grp, col, lvl, shp, axis, spd in comps:
    verts, tris = shp.val().tessellate(0.12, 0.25)
    ox, oz = (0.0, 0.0)
    if axis:
        ox, oz = NOM[axis][0], -NOM[axis][1]
    pos = []
    for (a, b, c) in tris:
        for idx in (a, b, c):
            v = verts[idx]
            pos += [v.x - ox, v.z, -v.y - oz]        # CAD Z -> three Y, recentre sur l'axe
    out.append({"name": name, "group": grp, "color": col, "lvl": lvl, "n": len(pos) // 3,
                "ax": ([round(ox, 3), round(oz, 3)] if axis else None), "spd": spd,
                "pos": base64.b64encode(struct.pack("<%df" % len(pos), *pos)).decode()})
# ---------------- tableau des cotes (affiche en bas a droite de la page) ----------------
def f1(v): return ("%.1f" % v).replace(".", ",")
By = NOM["B"][1]
table = [
    ["Carter", [
        ["Hauteur du carter", "%d mm" % (Z_TOP + H_BASE)],
        ["Hauteur avec brides", "%d mm" % (Z_TOP + H_BASE + 2 * FL_H)],
        ["Largeur x profondeur", "%s x %s mm" % (f1(C + 2 * R_OUT), f1(By + 2 * R_OUT))],
        ["Entraxe (3 etages)", "%s mm" % f1(C)],
        ["Epaisseurs base / murs / plaque / murs / couvercle", "%d / %d / %d / %d / %d mm" % (H_BASE, H_W1, H_PLATE, H_W2, H_COVER)]]],
    ["Moteur", [
        ["NEMA 17", "42,3 x 42,3 x 40 mm"],
        ["Trous de fixation", "M3, entraxe 31 mm"],
        ["Arbre", "D5 x 26 mm"]]],
    ["Poulies HTD 3M", [
        ["80T (x3)", "D primitif %s, flasques D%s x 12, alesage 8" % (f1(D80), f1(D80 + 2.6))],
        ["16T (x3)", "D primitif %s, flasques D%s, alesage 5 (moteur) / 8" % (f1(D16), f1(D16 + 2.7))],
        ["Courroies (x3)", "HTD 3M %d x 10 mm, %d dents" % (BELT_TEETH * PITCH, BELT_TEETH)]]],
    ["Arbres acier D8", [
        ["Arbre A", "60,5 mm"], ["Arbre B", "99 mm"], ["Arbre de sortie", "60,5 mm (depasse de 20)"]]],
    ["Roulements, bagues, tiges", [
        ["Roulement 688 (x6)", "D8 x D16 x 5 mm"],
        ["Bague excentrique (x6)", "D26 x 6 mm, excentricite 1,5"],
        ["Tige filetee M3 (x3)", "110 mm + 6 ecrous"]]],
    ["Fixation ALT (brides)", [
        ["Bride haute et basse", "%d x %d x %d mm" % (FL_W, FL_H, FL_T)],
        ["Trous", "2 x D%s, entraxe %d mm" % (f1(EAR_HOLE_D), FL_HOLE_SP)],
        ["Nervures de renfort (x6)", "%d x %d mm" % (RIB_T, RIB_D)]]],
    ["Fixation AZ (languettes)", [
        ["Languette sur la face", "%d mm de saillie, largeur %d (racine %d), epaisseur %d" % (EAR_L, EAR_WAZ, EAR_ROOT, EAR_HAZ)],
        ["Languette au sommet moteur", "24 mm de saillie, largeur 24, epaisseur %d" % EAR_HAZ],
        ["Trous", "D%s" % f1(EAR_HOLE_D)]]],
]
meta = {"table": table, "C": round(C, 2), "belt": BELT_TEETH * PITCH, "top": Z_TOP,
        "axes": {k: [round(v[0], 2), round(v[1], 2)] for k, v in NOM.items()}}
json.dump({"meta": meta, "comps": out}, open(os.path.join(OUT, "meshes.json"), "w"))
print("composants:", len(out), " triangles:", sum(c["n"] for c in out) // 3,
      " taille json: %.1f Mo" % (os.path.getsize(os.path.join(OUT, "meshes.json")) / 1e6))
