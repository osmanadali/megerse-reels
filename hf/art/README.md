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
