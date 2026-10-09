"""Pieces realistes pour la vue 3D (poulies HTD 3M dentees, courroies creuses, moteur NEMA 17, visserie).
Les enveloppes simples de build_gearbox.py restent utilisees pour les tests d'interference."""
import math
import cadquery as cq
from build_gearbox import *

TOOTH_H = 1.14          # profondeur de dent HTD 3M
FLANGE_T = 0.8
BAND = 12.0
TEETH_W = BAND - 2 * FLANGE_T


def toothed_profile(n, r_tip):
    r_root = r_tip - TOOTH_H
    pts = []
    pitch = 2 * math.pi / n
    for i in range(n):
        a0 = i * pitch
        # sommet de dent (plateau), flanc, creux, flanc
        for frac, r in ((0.00, r_tip), (0.34, r_tip), (0.42, r_root), (0.84, r_root), (0.92, r_tip)):
            a = a0 + frac * pitch
            pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def tpulley(x, y, zc, hub_up, n, bore):
    r_tip = (n * PITCH / math.pi) / 2 - 0.381
    z0 = zc - BAND / 2
    core = (cq.Workplane("XY", origin=(x, y, z0 + FLANGE_T))
            .polyline(toothed_profile(n, r_tip)).close().extrude(TEETH_W))
    fr = (D80 + 2.6) / 2 if n == NB else (D16 + 2.7) / 2
    fl1 = cyl(x, y, z0, 2 * fr, FLANGE_T)
    fl2 = cyl(x, y, z0 + BAND - FLANGE_T, 2 * fr, FLANGE_T)
    hub_r = 12.0 if n == NB else 7.5
    hz = z0 + BAND if hub_up else z0 - 6
    hub = cyl(x, y, hz, 2 * hub_r, 6)
    s = core.union(fl1).union(fl2).union(hub)
    if n == NB:   # allegement : 6 grandes fenetres dans le voile
        for k in range(6):
            a = math.radians(30 + 60 * k)
            s = s.cut(cyl(x + 22.5 * math.cos(a), y + 22.5 * math.sin(a), z0 - 1, 14, BAND + 2)
                      .intersect(cyl(x, y, z0 - 1, 2 * 29.5, BAND + 2)))
    if n == NS:
        for k in range(3):
            a = math.radians(90 + 120 * k)
            for zz in (z0 - 0.5, z0 + BAND - FLANGE_T - 0.5):
                s = s.cut(cyl(x + 7.0 * math.cos(a), y + 7.0 * math.sin(a), zz, 1.8, FLANGE_T + 1.0))
        a = math.radians(0)
        s = s.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(1.4, 12, cq.Vector(x, y, hz + 3.0),
                                                                 cq.Vector(1, 0, 0))))
    s = s.cut(cyl(x, y, z0 - 8, bore, BAND + 16))
    return s


def hollow_belt(p, q, r1, r2, zc):
    return belt(p, q, r1, r2, zc).cut(belt(p, q, r1 - 2.35, r2 - 2.35, zc).translate((0, 0, 0)))


def motor():
    """NEMA 17 sous la base : corps 42.3 x 42.3 x 40, bossage 22, arbre 5 x 24."""
    body = (cq.Workplane("XY", origin=(0, 0, -H_BASE - 40)).rect(42.3, 42.3).extrude(40)
            .edges("|Z").chamfer(4.5))
    for dx in (-15.5, 15.5):
        for dy in (-15.5, 15.5):
            body = body.cut(cyl(dx, dy, -H_BASE - 1.0, 3.0, 8))
    boss = cyl(0, 0, -H_BASE, 22.0, 2.0)
    return body.union(boss)


def motor_shaft():
    return cyl(0, 0, -H_BASE, 5.0, 24.0 + 2.0)


def rods_and_nuts():
    out = []
    for (x, y) in RODS:
        out.append(("tige", cyl(x, y, -H_BASE + 0.6, 3.0, Z_TOP + H_BASE - 1.2)))
        out.append(("ecrou", hexnut(x, y, -H_BASE, 2.4).cut(cyl(x, y, -H_BASE - 1, 3.0, 5))))
        out.append(("ecrou", hexnut(x, y, Z_TOP - 2.4, 2.4).cut(cyl(x, y, Z_TOP - 3, 3.0, 5))))
    return out
