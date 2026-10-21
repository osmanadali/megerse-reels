# FPS BATAK

**Masaya Otur. Kartını Oyna.**

Tamamen offline, birinci şahıs 3D Türk Batak oyunu. Godot 4.3+ / GDScript.

## Çalıştırma
Godot 4.3 ile `FPSBatak/project.godot` dosyasını açıp F5. (Esc: çıkış)

## Testler
```
godot --headless --path FPSBatak --import          # ilk seferde sınıf önbelleği için
godot --headless --path FPSBatak -s res://tests/run_tests.gd
```
Ekran görüntüsü (geliştirme): `godot --path FPSBatak -- --screenshot=/yol/shot.png`

## Yapı
| Klasör | İçerik |
|---|---|
| `scenes/main` | Ana sahne: ortam, ışık, oda, koltuklar, kamera, HUD |
| `scenes/table` | Masa (ahşap + keçe), `PlayArea/TrickSlots` masadaki 4 kart yuvası |
| `scenes/characters` | Rakip yer tutucusu (ileride karakter sistemi) |
| `scripts/cards` | `CardData` (kart verisi), `DeckManager` (deste mantığı) — görselden bağımsız |
| `scripts/core` | `Seat` (koltuk düzeni), ortak yardımcılar |
| `scripts/camera` | `SeatedCamera` (oturan oyuncu bakışı) |
| `tests` | Başsız birim testleri |

Koltuklar: 0 = Sen (güney), 1 = Sağ, 2 = Karşı, 3 = Sol; oyun sağa doğru (saat yönü tersine) ilerler.
