# Reducteur 125:1 HTD 3M (80T/16T) — liste d'achats

Quantites **par boite**. Il en faut **une par axe** (alt + az) : multiplier par 2 pour les deux axes.
Les cotes viennent de `build_gearbox.py` (reprises dans le tableau « Cotes » en bas a droite de `reducteur_125_3D.html`).

Statut : **vu** = reference trouvee dans des fiches AliExpress (titres/resultats, pas de plan cote) ; **a verifier** = je n'ai pas pu confirmer la cote sur une fiche precise.

## Transmission

| Piece | Qte / boite | Cotes a respecter | Mot-cle AliExpress | Statut |
|---|---|---|---|---|
| Poulie HTD 3M **80 dents**, avec flasques et moyeu | 3 | gorge pour courroie **10 mm**, alesage **8 mm**, diametre exterieur flasques **<= 80 mm** (le logement fait D85, le modele prevoit D79), hauteur de moyeu **<= 8 mm** (le modele prevoit 6 mm) | `HTD 3M pulley 80T 10mm bore 8mm` (type BF) | vu (fiche « 60T 72T 75T 80T, courroie 10/15 mm, alesage 5-14 ») ; moyeu a verifier |
| Poulie HTD 3M **16 dents** | 3 : **1 alesage 5 mm** (moteur) + **2 alesage 8 mm** | gorge **10 mm**, flasques D18 environ, vis de serrage | `HTD 3M pulley 16T 10mm bore 5mm` / `bore 8mm` | vu (lots 12T-19T, alesages 4-8 mm, largeurs 6/10/15) ; 16T a 8 mm a verifier |
| Courroie HTD 3M fermee **288-3M**, 10 mm | 3 | 288 mm = 96 dents, largeur 10 mm | `HTD 3M timing belt 288 10mm closed loop` | vu (courroies 3M 10 mm en fiches) |
| Roulement **688ZZ** | 6 | D8 x D16 x 5 mm | `688ZZ bearing 8x16x5` | courant |
| Arbre acier / inox rectifie **D8** | 2 x 60,5 mm + 1 x 99 mm (acheter 300 mm a decouper) | D8 h6 ; l'arbre de sortie depasse de 20 mm | `8mm linear shaft 300mm` | courant |

## Moteur et visserie

| Piece | Qte / boite | Cotes | Statut |
|---|---|---|---|
| Moteur **NEMA 17** | 1 | corps 42,3 x 42,3 x **40 mm**, trous M3 entraxe **31 mm**, centrage D22, arbre **D5 de 26 mm minimum** (modele : 24 + 2) | courant ; longueur d'arbre a verifier |
| Vis M3 x 12 (tete cylindrique) | 4 | fixation du moteur dans la base (10 mm + 2 de prise) | courant |
| Tige filetee M3 | 3 x **110 mm** (ou 1 m a couper) | traverse base, murs, plaque, couvercle : 109 mm dans le modele | courant |
| Ecrou M3 standard (hauteur 2,4) | 6 | logements hexagonaux 5,5 mm sur plat | courant |
| Vis M3 de blocage des bagues, **tete cylindrique** | 6 | longueur **40 a 45 mm** : il y a 39,5 mm de matiere entre la face exterieure et la bague. **A confirmer apres le premier essai d'impression** | a verifier |
| Cle hexagonale 2,5 mm | 1 | pour les vis de serrage des poulies et les vis M3 | courant |

## Fixation sur le Dobson (hors transmission)

| Piece | Qte | Remarque |
|---|---|---|
| Vis a bois D4, tete cylindrique ou bombee **<= D9** | **4** pour la boite alt (2 par bride) ; **2 a 3** pour la boite az (languettes) | longueur = epaisseur du panneau du rocker box moins 3 a 5 mm. **Epaisseur a mesurer.** Trou de passage : D4,6 |
| Rondelles D4 | idem | repartit l'appui sur la bride de 9 mm |

## Pieces imprimees (PETG ou ASA conseille)

- Communes : `2_mur_etage_1_2`, `3_plaque`, `4_mur_etage_3`, `6_bague_excentrique_x6` (x6).
- **Boite ALT** : `1_base` (imprimer **retournee**, la bride basse pointe vers le haut) + `5_couvercle`.
- **Boite AZ** : `1_base_AZ_sans_oreillons` + `5_couvercle_AZ` (imprimer **retourne**, face de sortie sur le plateau).

## Pas encore dans le projet

L'organe qui entraine reellement le telescope (galet de friction, courroie, pignon) n'est **pas** concu : il faut d'abord les mesures du plateau d'azimut et du disque d'altitude du Classic 200P.
