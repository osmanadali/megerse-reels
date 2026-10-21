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
Geliştirme argümanları (`--` sonrasına yazılır):
- `--screenshot=/yol/shot.png [--shot-times=2,6.5]` belirtilen saniyelerde ekran görüntüsü alıp çıkar
- `--autoplay` oyuncunun kartlarını da AI oynar (görsel test için)

## Oynanış (şu anki prototip)
Kartlar dağıtılır → "SIRA SENDE" yazınca elindeki parlak kartlardan birine tıkla
(dokunmatikte: önce dokun-seç, sonra tekrar dokun-oyna). Karartılmış kartlar o an oynanamaz.
İhale/gömme henüz yok: koz geçici olarak **Maça**, ilk löveyi dağıtanın sağındaki açar.

## Yapı
| Klasör | İçerik |
|---|---|
| `scenes/main` | Ana sahne: ortam, ışık, oda, koltuklar, kamera, HUD |
| `scenes/table` | Masa (ahşap + keçe), `PlayArea/TrickSlots` masadaki 4 kart yuvası |
| `scenes/characters` | Rakip yer tutucusu (ileride karakter sistemi) |
| `scripts/cards` | `CardData` (veri), `DeckManager` (deste), `CardFaceRenderer` (prosedürel kart yüzleri), `Card3D` (masadaki kart) |
| `scripts/rules` | `BatakRules` — uyma, yükseltme, koz zorunluluğu, löve kazananı (saf fonksiyonlar) |
| `scripts/ai` | `AIPlayer` — yalnızca kendi eli + açık kartlarla karar verir; zorluk seviyeleri için hazır |
| `scripts/game` | `TableController` (dağıt → löveler → el sonu akışı), `OpponentHandView` |
| `scripts/ui` | `GameHUD`, `HandView` (yelpaze el), `HandCard` |
| `scripts/audio` | `Sfx` — kodla üretilen yer tutucu kart sesleri |
| `scripts/core` | `Seat` (koltuk düzeni), ortak yardımcılar |
| `scripts/camera` | `SeatedCamera` (oturan oyuncu bakışı) |
| `tests` | Başsız birim testleri |

Koltuklar: 0 = Sen (güney), 1 = Sağ, 2 = Karşı, 3 = Sol; oyun sağa doğru (saat yönü tersine) ilerler.
