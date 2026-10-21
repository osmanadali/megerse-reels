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
- `--autoplay` oyuncunun kararlarını da AI verir (görsel test için)
- `--preview-panels` (ekran görüntüsüyle birlikte) ihale/gömme/koz panellerini sırayla açar

## Oynanış: 3 kişilik gömmeli ihaleli batak
1. Herkese 16 kart dağıtılır, ortaya 4 kart kapalı konur.
2. **İhale** dağıtanın yanından başlar (en az 7, en çok 16). Pas diyen bir daha giremez.
   Herkes pas derse dağıtanın yanındaki (ilk konuşan) 7 ile almak zorundadır.
3. İhaleyi alan önce kendi elinden **4 kart gömer** (kartlara tıkla → GÖM), sonra **kozu söyler**,
   ardından yerdeki 4 kartı eline alır.
4. İlk löveyi ihaleyi alan açar. Takıma uymak, yükseltmek, takım yoksa koz atmak zorunlu;
   koz kırılmadan koz açılamaz.
5. Puan: ihaleyi alan tutturursa aldığı el kadar artı, batarsa ihale kadar eksi;
   diğerleri aldığı el kadar artı.

Kart oynama: "SIRA SENDE" yazınca parlak kartlardan birine tıkla
(dokunmatikte: önce dokun-seç, sonra tekrar dokun-oyna). Karartılmış kartlar o an oynanamaz.

Bütün kural ayarları `scripts/rules/game_rules.gd` içinde (`GameRules`). 4 kişilik ihaleli
batak için hazır ayar: `GameRules.four_player_ihaleli()`.

## Yapı
| Klasör | İçerik |
|---|---|
| `scenes/main` | Ana sahne: ortam, ışık, oda, koltuklar, kamera, HUD |
| `scenes/table` | Yuvarlak masa (ahşap + keçe); masa üstü konumlar `TableLayout` ile oyuncu sayısına göre hesaplanır |
| `scenes/characters` | Rakip yer tutucusu (ileride karakter sistemi) |
| `scripts/cards` | `CardData` (veri), `DeckManager` (deste), `CardFaceRenderer` (prosedürel kart yüzleri), `Card3D` (masadaki kart) |
| `scripts/rules` | `GameRules` (varyant ayarları), `BatakRules` (uyma/yükseltme/koz), `BidManager` (ihale), `ScoreManager` (puan) |
| `scripts/ai` | `AIPlayer` — yalnızca kendi eli + açık kartlarla karar verir; zorluk seviyeleri için hazır |
| `scripts/game` | `TableController` (dağıt → ihale → göm → koz → löveler → puan), `SeatLayout`, `TableLayout`, `OpponentHandView` |
| `scripts/ui` | `GameHUD`, `HandView` (yelpaze el), `HandCard` |
| `scripts/audio` | `Sfx` — kodla üretilen yer tutucu kart sesleri |
| `scripts/core` | `Seat` (koltuk düzeni), ortak yardımcılar |
| `scripts/camera` | `SeatedCamera` (oturan oyuncu bakışı) |
| `tests` | Başsız birim testleri |

Koltuk 0 = Sen; rakipler masaya eşit açılarla dizilir (3 kişide sağ-ön ve sol-ön). Oyun sağa doğru (saat yönü tersine) ilerler.
