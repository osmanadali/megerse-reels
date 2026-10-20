# Çizim kütüphanesi (yeniden kullan, tekrar çizme)

Kod: `scripts/artlib.py` (import: `from artlib import ...`). Hepsi gerçekçi düz-vektör, gradyan + gölge.

| Parça | Ad | Not | İlk kullanım |
|---|---|---|---|
| Gradyan seti | `DEFS` | sky, fire, trail, roof, siding, lawn, wall, floor, couch, wood, rockG, flash, bruise, cash, soft filtresi | Hodges |
| Göktaşı / kaya | `ROCK` | ~110 birim, merkez (0,0) | Hodges |
| Ateş topu + iz | `FIREBALL` | iz sol-üste doğru | Hodges |
| 1950'ler ABD evi | `house(x,y,s,id)` | çatı, baca, verandalı kapı, perdeli pencere (`{id}-win`) | Hodges |
| Ağaç | `TREE` | gövde tabanı (0,0) | Hodges |
| İnsan silueti | `person(x,y,s,renk,şapka)` | kalabalık için | Hodges |
| Römorkör | `ship()` / `hf/art/ship.frag` | kırmızı gövde, usturmaçalar, köprü üstü, direk | Okene |
| Avatar (Osman) | `hf/avatar/osman.svg` | ağız 0-3, göz kırpma, baş | tüm reel'ler |

Sahneye özel (henüz kütüphaneye taşınmadı, `reels/hodges/build.py` içinde): salon kesiti (kanepe, radyo, saat), delil kutusu, kapı, terazi, satılık etiketi, tarla yolu + çiftçi, araba.

## v2 (`scripts/artlib2.py`): Osman v1'i "çok kötü" buldu → v2 standardı
Doku filtreleri (`grainy`, `woodgrain`, `organic` yaprak, `rough` kaya kenarı), alan derinliği (`dof`, `dof2`), `glow`, `shadow`; desenler (duvar kağıdı, kiremit, yalı tahtası, yorgan, halı).
**Kural:** `DEFS2` sayfada bir kez (`reelkit.page(defs=DEFS2)`), sahne SVG'lerine konmaz (gizli sahnedeki pattern çizilmez).

| Parça | Ad |
|---|---|
| Göktaşı (köşeli, füzyon kabuğu, çukurlu; müzedeki gibi) | `rock2(s)` |
| Ateş topu + duman izi | `fireball2(s)` |
| Bulut | `cloud(x,y,s,o)` |
| Sonbahar ağacı (resimsi yaprak) | `tree_autumn(x,y,s,seed,blur)` |
| 1950'ler ev, açılı, dokulu | `house2(x,y,s,id)` |
| 1950'ler araba (krom, beyaz yanaklı lastik) | `car50s(s,renk)` |
| Çiftçi (tulum, hasır şapka) | `farmer2(s)` |
| İnsan (palto/şapka, gölgeli) | `person2(x,y,s,palto,şapka,ten)` |
| Tokmak | `gavel(s)` |
| Hareketli nesne kabı (motion blur) | `obj_svg()` + build'deki `mover()` |

Hodges'a özel v2 sahne çizimleri `reels/hodges/build.py` içinde: salon (duvar kağıdı, perde, ışık huzmesi, saat, radyo, kanepe + uyuyan Ann, abajur), sokak kalabalığı, kapı + buzlu camda siluet, mahkeme + pirinç terazi, aralık kapı + taş, tarla yolu.
Motion blur: `data-hf-motion-blur` (registry `motion-blur`), grain: registry `grain-overlay` (`reelkit.page(fx=True)`).
