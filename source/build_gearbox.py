"""Reducteur 125:1 HTD3M, 3 etages 80T/16T, disposition en TRIANGLE EQUILATERAL.

Idee : les trois etages ont le meme entraxe C (meme courroie), donc les axes
moteur -> A -> B -> sortie forment un triangle ferme. L'arbre de sortie tombe
exactement dans l'axe du moteur, un niveau plus haut : sortie coaxiale.

Niveaux (z=0 = dessus de la base) :
  base 10 | murs 52 (etages 1+2 en sandwich) | plaque 12 | murs 26 (etage 3) | couvercle 10
Reglage de tension : bagues excentriques (e = 1.5 mm) a repere 24 crans,
bloquees par une vis M3 radiale. Meme repere sur les deux bagues d'un axe.
"""
import math, os
import cadquery as cq

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------- parametres ----------------
PITCH = 3.0
NB, NS = 80, 16                       # grande / petite poulie (rapport 5 par etage)
D80 = 80 * PITCH / math.pi
D16 = 16 * PITCH / math.pi
BELT_TEETH = 96                       # courroie HTD 3M 288 mm, 10 mm (celle que tu as)
BELT_W = 10.0
_L = BELT_TEETH * PITCH
_b = -(_L - math.pi * (D80 + D16) / 2)
_c = (D80 - D16) ** 2 / 4
C = (-_b + math.sqrt(_b * _b - 8 * _c)) / 4          # entraxe nominal

H_BASE, H_W1, H_PLATE, H_W2, H_COVER = 10.0, 52.0, 12.0, 26.0, 10.0
Z_W1, Z_PL, Z_W2, Z_CV = 0.0, H_W1, H_W1 + H_PLATE, H_W1 + H_PLATE + H_W2
Z_TOP = Z_CV + H_COVER                               # 100

R_IN, R_OUT = 42.5, 51.0                             # cavite / exterieur
BRG_OD, BRG_ID, BRG_H = 16.0, 8.0, 5.0               # roulement 688
RING_OD, RING_H, E = 26.0, 6.0, 1.5                  # bague excentrique
POCKET_D, POCKET_H = 26.3, 6.2
BRG_POCKET_D = 16.15
ROD_D = 3.4                                          # tiges M3
# fixation, dans le plan d'une face plate du triangle (cote MOUNT_SIDE : 1 = A-B, oppose au moteur)
MOUNT_SIDE = 1
EAR_HOLE_D = 4.6             # trou lisse pour vis a bois / M4
# ALT (boite contre la paroi frontale) : brides au-dessus du couvercle et sous la base, vis perpendiculaires a la paroi
FL_H, FL_W, FL_T = 24.0, 70.0, 9.0     # saillie au-dela du carter, largeur, epaisseur
RIB_D, RIB_T = 18.0, 5.0               # nervures de renfort : profondeur sur le carter, epaisseur
RIB_U = (0.0, 30.5)                    # positions des nervures (decalage depuis le centre de la face) : centre + 2 bords
FL_HOLE_SP = 40.0                      # entraxe des 2 vis d'une bride
# AZ (boite tete en bas sur le fond) : languettes horizontales sur le couvercle, vis verticales
EAR_L, EAR_WAZ, EAR_HAZ = 52.0, 22.0, 10.0    # saillie le long de la face, largeur au bout, epaisseur (= couvercle)
EAR_ROOT = 32.0                        # largeur a la racine (languette effilee)
EAR_HOLE_OFF = 9.0
AZ_ENDS = (0, 1)                       # bouts de la face portant une languette (0 = cote B, 1 = cote A)
AZ_VERTEX_O = True                     # languette supplementaire au sommet moteur, perpendiculaire a la paroi

# ---------------- geometrie du triangle ----------------
O = (0.0, 0.0)                         # moteur ET sortie (coaxiaux)
A = (C, 0.0)
B = (C / 2, C * math.sqrt(3) / 2)
CEN = ((O[0] + A[0] + B[0]) / 3, (O[1] + A[1] + B[1]) / 3)
TRI = [O, A, B]


def unit(v):
    n = math.hypot(*v)
    return (v[0] / n, v[1] / n)


def outward(p):                         # bissectrice sortante au sommet p
    return unit((p[0] - CEN[0], p[1] - CEN[1]))


OUTV = {"O": outward(O), "A": outward(A), "B": outward(B)}
NOM = {"O": O, "A": A, "B": B}
# centre de la poche = position nominale - E * direction sortante
POCKET = {k: (NOM[k][0] - E * OUTV[k][0], NOM[k][1] - E * OUTV[k][1]) for k in NOM}


def outline(r, z0, h):
    return (cq.Workplane("XY", origin=(0, 0, z0)).polyline(TRI).close()
            .offset2D(r, "arc").extrude(h))


def cyl(x, y, z0, d, h):
    return cq.Workplane("XY", origin=(x, y, z0)).circle(d / 2).extrude(h)


def hexnut(x, y, z0, h):
    return cq.Workplane("XY", origin=(x, y, z0)).polygon(6, 6.4).extrude(h)


# tiges M3 : milieu de chaque arete, decale vers l'exterieur
def rod_points():
    pts = []
    for i in range(3):
        p, q = TRI[i], TRI[(i + 1) % 3]
        m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
        n = outward(m)
        off = (R_IN + R_OUT) / 2
        # distance au segment le long de la normale sortante de l'arete
        e = unit((q[0] - p[0], q[1] - p[1]))
        nn = (e[1], -e[0])
        if (nn[0] * (m[0] - CEN[0]) + nn[1] * (m[1] - CEN[1])) < 0:
            nn = (-nn[0], -nn[1])
        pts.append((m[0] + nn[0] * off, m[1] + nn[1] * off))
    return pts


RODS = rod_points()


def with_rods(shape, z0, h):
    for (x, y) in RODS:
        shape = shape.cut(cyl(x, y, z0 - 1, ROD_D, h + 2))
    return shape


def radial_hole(shape, key, z):
    ux, uy = OUTV[key]
    px, py = POCKET[key]
    cyl_ = cq.Solid.makeCylinder(1.45, R_OUT + 5 - 8, cq.Vector(px + ux * 8, py + uy * 8, z),
                                 cq.Vector(ux, uy, 0))
    return shape.cut(cq.Workplane("XY").add(cyl_))


def pocket_from_top(shape, key, ztop, thru_d=None):
    x, y = POCKET[key]
    s = shape.cut(cyl(x, y, ztop - POCKET_H, POCKET_D, POCKET_H + 1))
    return s


def pocket_from_bottom(shape, key, zbot):
    x, y = POCKET[key]
    return shape.cut(cyl(x, y, zbot - 1, POCKET_D, POCKET_H + 1))


# ---------------- pieces imprimees ----------------
def _side_frame():
    """Repere local de la face de montage : x le long de la face, y vers l'exterieur (normale), origine au sommet p."""
    i = MOUNT_SIDE
    p, q = TRI[(i + 1) % 3], TRI[i]            # sens choisi pour que +90 deg = vers l'exterieur
    ang = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
    return p, ang


def _place(shape, p, ang):
    return shape.rotate((0, 0, 0), (0, 0, 1), ang).translate((p[0], p[1], 0))


def _ribs(z_face, direction):
    """Nervures triangulaires entre la bride et le carter. direction=+1 : bride au-dessus (z_face = dessus du couvercle)."""
    out = None
    yb = R_OUT - FL_T
    h = FL_H - 6.0
    for du in RIB_U:
        for sgn in ((1,) if du == 0 else (-1, 1)):
            xc = C / 2 + sgn * du
            pts = [(yb + 1.0, z_face - direction * 1.0), (yb - RIB_D, z_face - direction * 1.0), (yb + 1.0, z_face + direction * h)]
            r = cq.Workplane("YZ", origin=(xc - RIB_T / 2, 0, 0)).polyline(pts).close().extrude(RIB_T)
            out = r if out is None else out.union(r)
    return out


def _flange(zlo, zhi, zh, z_face, direction):
    e = cq.Workplane("XY").box(FL_W, FL_T, zhi - zlo, centered=False).translate((C / 2 - FL_W / 2, R_OUT - FL_T, zlo))
    e = e.faces(">Z" if direction > 0 else "<Z").edges("|Y").fillet(6.0)
    for sgn in (-1, 1):
        h = cq.Solid.makeCylinder(EAR_HOLE_D / 2, FL_T + 2, cq.Vector(C / 2 + sgn * FL_HOLE_SP / 2, R_OUT - FL_T - 1, zh), cq.Vector(0, 1, 0))
        e = e.cut(cq.Workplane("XY").add(h))
    e = e.union(_ribs(z_face, direction))
    p, ang = _side_frame()
    return _place(e, p, ang)


def flange_up(ztop):
    """Bride au-dessus du carter (couvercle) : de ztop-8 a ztop+FL_H, trous a ztop+FL_H-12, 3 nervures."""
    return _flange(ztop - 8.0, ztop + FL_H, ztop + FL_H - 12.0, ztop, +1)


def flange_down(zbot):
    """Bride sous le carter (base) : de zbot-FL_H a zbot+8, trous a zbot-FL_H+12, 3 nervures."""
    return _flange(zbot - FL_H, zbot + 8.0, zbot - FL_H + 12.0, zbot, -1)


def _taper_ear(x_root, x_tip, h, ztop, w_tip, w_root):
    """Languette effilee dans le repere local de la face (le dos contre la paroi : y = R_OUT)."""
    d = 1 if x_tip > x_root else -1
    pts = [(x_root, R_OUT - w_root), (x_root, R_OUT), (x_tip, R_OUT), (x_tip, R_OUT - w_tip), (x_root + d * 14.0, R_OUT - w_tip)]
    e = cq.Workplane("XY", origin=(0, 0, ztop - h)).polyline(pts).close().extrude(h)
    return e.faces(">X" if d > 0 else "<X").edges("|Z").fillet(w_tip / 2 - 0.5)


def floor_ears(ztop, h=EAR_HAZ):
    """Languettes AZ : plaques horizontales sur le couvercle (boite tete en bas), trou vertical vers le fond."""
    p, ang = _side_frame()
    out = None
    ranges = {0: (8.0, -EAR_L, -EAR_L + EAR_HOLE_OFF), 1: (C - 8.0, C + EAR_L, C + EAR_L - EAR_HOLE_OFF)}
    for k in AZ_ENDS:
        xr, xt, xh = ranges[k]
        e = _taper_ear(xr, xt, h, ztop, EAR_WAZ, EAR_ROOT)
        hole = cq.Solid.makeCylinder(EAR_HOLE_D / 2, h + 2, cq.Vector(xh, R_OUT - EAR_WAZ / 2, ztop - h - 1), cq.Vector(0, 0, 1))
        e = e.cut(cq.Workplane("XY").add(hole))
        out = e if out is None else out.union(e)
    out = _place(out, p, ang)
    if AZ_VERTEX_O:
        ux, uy = OUTV["O"]
        a2 = math.degrees(math.atan2(uy, ux))
        x0, x1 = R_OUT - 8.0, R_OUT + 24.0
        e = cq.Workplane("XY", origin=(0, 0, ztop - h)).polyline([(x0, -16.0), (x0, 16.0), (x0 + 12.0, 12.0), (x1, 12.0), (x1, -12.0), (x0 + 12.0, -12.0)]).close().extrude(h)
        e = e.faces(">X").edges("|Z").fillet(11.5)
        hole = cq.Solid.makeCylinder(EAR_HOLE_D / 2, h + 2, cq.Vector(x1 - EAR_HOLE_OFF - 1, 0, ztop - h - 1), cq.Vector(0, 0, 1))
        e = e.cut(cq.Workplane("XY").add(hole)).rotate((0, 0, 0), (0, 0, 1), a2).translate((O[0], O[1], 0))
        out = out.union(e)
    return out


def make_base(ears=True):
    s = outline(R_OUT, -H_BASE, H_BASE)
    s = with_rods(s, -H_BASE, H_BASE)
    for (x, y) in RODS:
        s = s.cut(hexnut(x, y, -H_BASE - 1, 3.6))            # ecrou sous la base
    # moteur NEMA 17 sous la base, axe en O
    s = s.cut(cyl(0, 0, -H_BASE - 1, 22.6, H_BASE + 2))
    for dx in (-15.5, 15.5):
        for dy in (-15.5, 15.5):
            s = s.cut(cyl(dx, dy, -H_BASE - 1, 3.4, H_BASE + 2))
    # roulements : axes A et B
    for k in ("A", "B"):
        s = pocket_from_top(s, k, 0.0)
        s = radial_hole(s, k, -POCKET_H / 2)
    if ears:
        s = s.union(flange_down(-H_BASE))
    return s


def make_wall(z0, h):
    s = outline(R_OUT, z0, h).cut(outline(R_IN, z0 - 1, h + 2))
    return with_rods(s, z0, h)


def make_plate():
    s = outline(R_OUT, Z_PL, H_PLATE)
    s = with_rods(s, Z_PL, H_PLATE)
    s = pocket_from_bottom(s, "A", Z_PL)                     # roulement haut de A
    s = radial_hole(s, "A", Z_PL + POCKET_H / 2)
    s = s.cut(cyl(B[0], B[1], Z_PL - 1, 12.5, H_PLATE + 2))  # passage de l'arbre B
    top = Z_PL + H_PLATE
    s = pocket_from_top(s, "O", top)                         # roulement bas de la sortie
    s = radial_hole(s, "O", top - POCKET_H / 2)
    return s


def make_cover(mode="alt"):
    s = outline(R_OUT, Z_CV, H_COVER)
    s = with_rods(s, Z_CV, H_COVER)
    for (x, y) in RODS:
        s = s.cut(hexnut(x, y, Z_TOP - 2.6, 3.6))            # ecrou sur le couvercle
    for k in ("B", "O"):
        s = pocket_from_bottom(s, k, Z_CV)
        s = radial_hole(s, k, Z_CV + POCKET_H / 2)
    s = s.cut(cyl(O[0], O[1], Z_CV - 1, 10.5, H_COVER + 2))  # sortie de l'arbre
    if mode == "alt":
        s = s.union(flange_up(Z_TOP))
    elif mode == "az":
        s = s.union(floor_ears(Z_TOP))
    return s


def make_ring():
    """Bague excentrique, face haute = face visible. Axe de la bague en (0,0),
    excentricite vers +X."""
    s = cyl(0, 0, 0, RING_OD, RING_H)
    s = s.cut(cyl(E, 0, RING_H - BRG_H - 0.0, BRG_POCKET_D, BRG_H + 1))   # logement 688
    s = s.cut(cyl(E, 0, -1, 10.0, RING_H + 2))                            # passage arbre
    # 24 crans sur le pourtour (repere de reglage), un cran double a +X
    for i in range(24):
        a = math.radians(i * 15)
        r = 0.45 if i else 0.9
        s = s.cut(cyl((RING_OD / 2) * math.cos(a), (RING_OD / 2) * math.sin(a), RING_H - 1.0, r * 2, 1.2))
    # 2 trous pour pointes de cle, cote oppose a l'excentricite
    for da in (-25, 25):
        a = math.radians(180 + da)
        s = s.cut(cyl(9.9 * math.cos(a), 9.9 * math.sin(a), RING_H - 2.0, 2.5, 2.2))
    return s


# ---------------- pieces du commerce (maquettes) ----------------
def tube(x, y, z0, d, h, bore=0.0):
    s = cyl(x, y, z0, d, h)
    if bore:
        s = s.cut(cyl(x, y, z0 - 1, bore, h + 2))
    return s


def pulley80(x, y, zc, hub_up):
    band = tube(x, y, zc - 6, 79.0, 12, 8.0)
    hub = tube(x, y, zc + 6 if hub_up else zc - 12, 24.0, 6, 8.0)
    return band.union(hub)


def pulley16(x, y, zc, hub_up, bore):
    band = tube(x, y, zc - 6, 18.0, 12, bore)
    hub = tube(x, y, zc + 6 if hub_up else zc - 12, 16.0, 6, bore)
    return band.union(hub)


def belt(p, q, r1, r2, zc):
    d = math.hypot(q[0] - p[0], q[1] - p[1])
    u = ((q[0] - p[0]) / d, (q[1] - p[1]) / d)
    n = (-u[1], u[0])
    sa = (r1 - r2) / d
    ca = math.sqrt(1 - sa * sa)
    ms = [(u[0] * sa + s * n[0] * ca, u[1] * sa + s * n[1] * ca) for s in (1, -1)]
    pts = [(p[0] + r1 * ms[0][0], p[1] + r1 * ms[0][1]), (q[0] + r2 * ms[0][0], q[1] + r2 * ms[0][1]),
           (q[0] + r2 * ms[1][0], q[1] + r2 * ms[1][1]), (p[0] + r1 * ms[1][0], p[1] + r1 * ms[1][1])]
    z0 = zc - BELT_W / 2
    prism = cq.Workplane("XY", origin=(0, 0, z0)).polyline(pts).close().extrude(BELT_W)
    return prism.union(cyl(p[0], p[1], z0, 2 * r1, BELT_W)).union(cyl(q[0], q[1], z0, 2 * r2, BELT_W))


def shaft(x, y, z0, z1):
    return cyl(x, y, z0, 8.0, z1 - z0)


def bearing(x, y, ztop):
    return tube(x, y, ztop - BRG_H, BRG_OD, BRG_H, BRG_ID)


# ---------------- construction ----------------
def build():
    parts = {
        "1_base": (make_base(), -H_BASE),
        "2_mur_etage_1_2": (make_wall(Z_W1, H_W1), Z_W1),
        "3_plaque": (make_plate(), Z_PL),
        "4_mur_etage_3": (make_wall(Z_W2, H_W2), Z_W2),
        "5_couvercle": (make_cover(), Z_CV),
        "6_bague_excentrique_x6": (make_ring(), 0.0),
    }
    return parts


def build_variants():
    """Pieces supplementaires : montage AZ (boite tete en bas sur le fond du rocker box)."""
    return {"1_base_AZ_sans_oreillons": (make_base(ears=False), -H_BASE),
            "5_couvercle_AZ": (make_cover("az"), Z_CV)}


# centres de bande de chaque etage
ZC1, ZC2, ZC3 = 9.0, 34.0, 77.0
RB80, RB16 = D80 / 2 + 2.0, D16 / 2 + 2.0                  # dos de courroie


def hardware():
    h = {}
    # axe moteur / sortie (O) : arbre moteur 5 mm (maquette) + sortie 8 mm
    h["pulley_M16"] = pulley16(*O, ZC1, False, 5.0)
    h["motor_shaft"] = cyl(O[0], O[1], -10, 5.0, 26)
    h["pulley_O80"] = pulley80(*O, ZC3, False)
    h["shaft_O"] = shaft(*O, 59.5, Z_TOP + 20)
    # axe A
    h["pulley_A80"] = pulley80(*A, ZC1, True)
    h["pulley_A16"] = pulley16(*A, ZC2, False, 8.0)
    h["shaft_A"] = shaft(*A, -4.5, 56.0)
    # axe B
    h["pulley_B80"] = pulley80(*B, ZC2, True)
    h["pulley_B16"] = pulley16(*B, ZC3, False, 8.0)
    h["shaft_B"] = shaft(*B, -4.5, 94.5)
    h["belt1"] = belt(O, A, D16 / 2 + 2.0, RB80, ZC1)
    h["belt2"] = belt(A, B, D16 / 2 + 2.0, RB80, ZC2)
    h["belt3"] = belt(B, O, D16 / 2 + 2.0, RB80, ZC3)
    return h


if __name__ == "__main__":
    print("entraxe nominal C = %.3f mm" % C)
    print("RODS", [(round(x, 1), round(y, 1)) for x, y in RODS])
    parts = build()
    for name, (shp, z0) in parts.items():
        s = shp.val()
        bb = s.BoundingBox()
        print("%-26s vol %9.0f mm3  bbox %.1f x %.1f x %.1f" % (name, s.Volume(), bb.xlen, bb.ylen, bb.zlen))
        flat = shp.translate((0, 0, -z0)) if z0 else shp
        cq.exporters.export(flat, os.path.join(OUT, name + ".stl"))
    for name, (shp, z0) in build_variants().items():
        flat = shp.translate((0, 0, -z0)) if z0 else shp
        cq.exporters.export(flat, os.path.join(OUT, name + ".stl"))
        print("%-26s variante AZ exportee" % name)
    print("exports STL ok")
