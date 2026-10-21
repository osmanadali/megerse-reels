# FPS BATAK

**Masaya Otur. Kartını Oyna.**

Tamamen offline, birinci şahıs 3D Türk Batak oyunu. Godot 4.3+ / GDScript.

## Çalıştırma
Godot 4.3 ile `FPSBatak/project.godot` dosyasını açıp F5.

**Ana menü:** Oyuna Başla · Karakterler (yakında) · Masalar · Kartlar · İstatistikler · Ayarlar (ses, tam ekran) · Çıkış.
Oyun içinde **Esc**: Devam / Ana Menü / Çıkış. İstatistikler ve ayarlar cihazda saklanır (`user://`).

## Testler
```
godot --headless --path FPSBatak --import          # ilk seferde sınıf önbelleği için
godot --headless --path FPSBatak -s res://tests/run_tests.gd
```
Geliştirme argümanları (`--` sonrasına yazılır):
- `--screenshot=/yol/shot.png [--shot-times=2,6.5]` belirtilen saniyelerde ekran görüntüsü alıp çıkar
- `--autoplay` oyuncunun kararlarını da AI verir, ayar panelini atlar (görsel test için)
- `--rounds=N --target=M --mode=standard|buried` autoplay'de maç ayarları
- `--speed=4` oyunu hızlandırır (yavaş yazılım render'ında kare sayısıyla sınırlıdır)
- `--preview-panels` (ekran görüntüsüyle birlikte) ihale/gömme/koz panellerini sırayla açar
- `--menu-start=1.5`, `--menu-panel=stats`, `--esc-at=5`, `--menu-return-at=7` menü akışını otomatik dener

## Oyun modları
Masa ayarlarından seçilir. Her modun kuralları `scripts/rules/game_rules.gd` içinde ayrı bir
yapılandırmadır (`GameRules.standard_bidding()` / `GameRules.buried_bidding()`).

| | NORMAL İHALELİ (`STANDARD_BIDDING`) | GÖMMELİ İHALELİ (`BURIED_BIDDING`) |
|---|---|---|
| Oyuncu | 4 (1 insan + 3 AI) | 3 (1 insan + 2 AI) |
| Kart | 13'er, ortada kart yok | 16'şar + 4 kapalı yer kartı |
| İhale | en az 5, en çok 13 | en az 7, en çok 16 |
| Herkes pas | ihale **4** ile dağıtanın sağındakine (yeni tur yok) | ihale **7** ile dağıtanın sağındakine |
| İhaleden sonra | ihaleyi alan kozu söyler, oyunu açar | önce 4 kart gömer, kozu söyler, yerdeki 4 kartı (göstermeden) alır, oyunu açar |

Ortak kurallar:
- Sırayla teklif verilir veya PAS denir; PAS diyen o ihale turuna tekrar giremez; mevcut en yüksek teklifin üzerine çıkmak zorunludur.
- Takıma uymak, yükseltmek, takım yoksa koz atmak zorunlu; koz kırılmadan koz açılamaz.
- Puan: ihaleyi alan tutturursa aldığı el kadar artı, batarsa ihale kadar eksi; diğerleri aldığı el kadar artı, **hiç el alamayan ihale kadar eksi**.
- Maç: tur sayısı (5/7/9/11) dolunca ya da biri hedef puana (51/71/91/101) ulaşınca biter.

Kart oynama: "SIRA SENDE" yazınca parlak kartlardan birine tıkla
(dokunmatikte: önce dokun-seç, sonra tekrar dokun-oyna). Karartılmış kartlar o an oynanamaz.

## Yapı
| Klasör | İçerik |
|---|---|
| `scenes/main` | Ana sahne: ortam, ışık, oda, koltuklar, kamera, HUD |
| `scenes/table` | Yuvarlak masa (ahşap + keçe); masa üstü konumlar `TableLayout` ile oyuncu sayısına göre hesaplanır |
| `scenes/characters` | Rakip yer tutucusu (ileride karakter sistemi) |
| `scripts/cards` | `CardData` (veri), `DeckManager` (deste), `CardFaceRenderer` (prosedürel kart yüzleri), `Card3D` (masadaki kart) |
| `scripts/rules` | `GameRules` (mod kuralları), `MatchSettings` (tur/hedef, maç sonu), `BatakRules` (uyma/yükseltme/koz), `BidManager` (ihale), `ScoreManager` (puan) |
| `scripts/ai` | `AIPlayer` — yalnızca kendi eli + açık kartlarla karar verir; zorluk seviyeleri için hazır |
| `scripts/game` | `TableController` (dağıt → ihale → göm → koz → löveler → puan), `SeatLayout`, `TableLayout`, `OpponentHandView` |
| `scripts/ui` | `MainMenu` (ana menü + duraklatma), `GameHUD`, `HandView` (yelpaze el), `HandCard`, `UiTheme` (ortak tema) |
| `scripts/audio` | `Sfx` — kodla üretilen yer tutucu kart sesleri |
| `scripts/core` | `Seat` (koltuk düzeni), `PlayerStats` (istatistik), `UserSettings` (ses/ekran) |
| `scripts/camera` | `SeatedCamera` (oturan oyuncu bakışı), `MenuCamera` (menüde masanın etrafında dönen kamera) |
| `tests` | Başsız birim testleri |

Koltuk 0 = Sen; rakipler masaya eşit açılarla dizilir (3 kişide sağ-ön ve sol-ön). Oyun sağa doğru (saat yönü tersine) ilerler.
