# HANDOFF: yeni sohbette buradan devam et

Son güncelleme: 20.10.2026. Repo: `osmanadali/megerse-reels`, dal `claude/storytelling-reels`.
Yeni sohbette ilk mesaj: "HANDOFF.md'yi oku ve kaldığın yerden devam et."

## Hedef (Osman'ın kararları)
- Format: **storytelling reels**, 1080×1920, Türkçe.
- **Tek ücretli araç: ElevenLabs, yalnızca seslendirme.** Geri kalan her şey ücretsiz/açık kaynak. (Apify iptal edildi.)
- Ekran: altta veya sol altta **facecam tarzı avatar** (Osman'ın fotoğraflarından) hikayeyi anlatır; geri kalan alanda hikaye görselleri döner.
- Altyazı sesle **kelime kelime senkron**.
- **Görsel kuralı (önemli):** Osman gerçek görsel verirse o kullanılır (nasıl kullanılacağını o söyler). Osman vermediği her şey **kesinlikle vektör çizim**, ama vektörler **gerçekçi** olmalı (detaylı, gölgeli/ışıklı, doğru oranlı; çocuksu/emoji tarzı değil). Kendi kafamdan fotoğraf/stok görsel eklemem.
- Animasyon, geçiş, kamera hareketi kaliteli olmalı; düz kesme yok.
- Render kısa sürmeli, token tasarruflu çalış, her adımda bu dosyayı güncelle + commit + push.

## Kurulu olanlar
- `./setup.sh`: Remotion, Python `.venv` (edge-tts, faster-whisper, moviepy…), Fluent Emoji. manim kurulamadı (pango yok, isteğe bağlı).
- **HyperFrames** (HTML → MP4, Apache-2.0): `hf/` projesi (`npx hyperframes@0.8.181 init hf --example blank --resolution portrait`). Skill'ler `~/.agents/skills/hyperframes*` altında. Boş proje test render'ı: 10 sn video, 13,8 sn'de render oldu (CPU, 4 çekirdek, GPU yok).
  - Yeni konteynerde: `npx -y hyperframes@0.8.181 skills update` ve `cd hf && npm run render`.
- Remotion render için: `REMOTION_CHROME=/opt/pw-browsers/chromium_headless_shell-1194/<alt-klasör>/headless_shell`.

## Durum
1. ✅ 10 konu adayı + bağımsız hakem puanı: `research/konular-2026-10.md`
   - GEÇTİ: **Ann Hodges** (77.5).
   - Sınırda: **Tsutomu Yamaguchi** (76.5 ama özgünlük 58 < 60; taze açıyla geçer).
   - Tur 2 GEÇTİ: **Harrison Okene** (80.7), **Mauro Prosperi** (78.3), **Beck Weathers** (78.2), **Frank Hayes** (76.2). Düzeltmeler dosyada.
2. ⏳ **İlk reel: Okene.** Senaryo v2 (görsel yerleşimi + dalgıç kapanışı, Osman onayladı): `reels/okene/senaryo.md`. Görseller: `reels/okene/gorseller.md`. Ses: ElevenLabs "Fatih Yıldırım" (voice_id `7VqWGAWwo2HMrylfKrcm`, eleven_v4), flow `qW2pK44UhjUG0UIXX9YF`, 4 varyasyon indirildi: `hf/assets/okene/ses/ses-1..4.mp3` (67,6/69,3/67,6/69,8 sn; 845 kredi/adet). **Seçilen: ses-4** (`hf/assets/okene/voice.mp3`, 69,8 sn). Seslendirilen metin `reels/okene/metin.txt`; kelime zamanları `reels/okene/words.json` (124 kelime, `scripts/align.py --text` ile, yazım metinden).
3. ✅ Avatar: Osman **çizim avatar** istedi (referans: sol altta çerçeveli düz-renk portre + yanında konuşma balonu altyazı). `hf/avatar/osman.svg` (osman-4.jpg'den çizildi; gruplar: mouth-0..3, eyes-open/closed, head). Ağız sesin RMS zarfından (`hf/avatar/mouth-okene.json`, 30 fps, 0-3). SadTalker/fotogerçekçi avatar **iptal**.
4. ✅ **Okene v1 render**: `python3 reels/okene/build.py` → `hf/index.html` → `cd hf && npx -y hyperframes@0.8.181 render -o renders/okene-v1.mp4` (74 sn, ~4 dk render, -16 LUFS). Fontlar: `hf/assets/fonts/` (node_modules/@fontsource/montserrat'tan latin + latin-ext 600/800 kopyası; git dışı).
5. ✅ v2: batış sahnesi gerçekçi vektörle yeniden çizildi (`hf/art/ship.frag`, yüzey→devrilme→kamera dibe iner→tortu bulutu); render `hf/renders/okene-v2.mp4`.
6. ✅ v3 (`hf/renders/okene-v3.mp4`, 73,6 sn): "ceset daha | sandığı" arasındaki 0,26 sn duraksama kesildi (`voice.mp3` artık kesilmiş sürüm, orijinal `ses/ses-4.mp3`; ffmpeg atrim 49.26 / 49.50 + 20 ms crossfade). Kelime zamanları ve ağız yeniden çıkarıldı (`scripts/mouth.py`). Yeni sahne `team` (65,5 sn): Osman'ın verdiği `basinc-odasi-dalgiclar.jpg`, en soldaki **Nico van Heerden** çemberle + etiketle işaretli.
7. ✅ Paylaşım paketi: açıklama `reels/okene/caption.md`, kapak `hf/cover-okene.html` → `hf/renders/okene-kapak.jpg` (chromium headless ekran görüntüsü). Hakem puanlaması yapılmadı.
8. ⏸ Prosperi askıda (Osman hassas içerik istemedi: bilek kesme). Notlar `reels/prosperi/hikaye.md`.
9. ⏳ **İkinci reel: Ann Hodges** (hassas içerik yok). Hikaye: `reels/hodges/hikaye.md`. Metin `reels/hodges/metin.txt`; ses tek varyasyon (1018 kredi, flow `DgbT4wpQhKaFYhT5Gex8`) `hf/assets/hodges/voice.mp3` (75,8 sn, okunuşlar: Silakoga, En Hocız, Culiyus Mıkkini). `reels/hodges/build.py` (13 sahne, vektör; sahne başları `anchor()` ile metinden). Ortak parçalar `scripts/reelkit.py` (sayfa/avatar/altyazı) + `scripts/artlib.py` (çizim kütüphanesi, envanter `hf/art/README.md`). **Osman gerçek görselleri gönderecek**; build.py `REAL` sözlüğü: `hf/assets/hodges/{morluk,ann-tas,cati,muze}.jpg` varsa vektör yerine kullanılır. v1 render `hf/renders/hodges-v1.mp4` (80 sn, -15.8 LUFS); gerçek görsel yerleşimi `reels/hodges/gorseller.md`.
- **v2 (Osman: "çizimler çok kötü, gelişmiş çizim + HyperFrames + motion blur")**: `scripts/artlib2.py` (dokulu/ışıklı/DOF) ile Hodges vektör sahneleri baştan; registry `motion-blur` + `grain-overlay` eklendi (`hf/compositions/components/`). Eski build `reels/hodges/build_v1.py`. Render `hf/renders/hodges-v2.mp4`.
- **Konu turu 3** (`research/konular-2026-10.md`, #21-30): yalnızca **Selahattin Ülkümen** geçti (75.9, şartlı: bombalama kurtarmadan önce oldu, kırılma "50 kişiden yalnızca 13'ü gerçekten vatandaştı"). Sınırda: Leonardo'nun Haliç köprüsü (74.8), Ertuğrul→Tahran (75.1 ama özg. 40), Einstein mektubu (73.8). Osman'ın seçimi bekleniyor.
- **v2 eleştirisi (Osman, 20.10):** animasyonlar Karagöz-Hacivat gibi düz, derinlik yok, kenardan kayan simgeler basit, karakterler eksik (bacaksız), konuşan karakter yanındakine dönük olmalı. → **v3 standardı:** `hf/art/DERINLIK.md` (kurallar + kontrol listesi) ve `scripts/depth.py` (dünya koordinatlı perspektif kamera, katman sıralama, tek güneş + perspektifli düşen/temas gölgesi, atm0-5 hava perspektifi, eşit dünya aralığı = sıkışma, tam boy yönlü `figure()`, her karede yeniden izdüşen kamera hareketi `camera_js`). Demo: `hf/demo/build_demo.py` → `hf/renders/derinlik-demo.mp4` (6 sn, ~40 sn render). Hodges reel'i **tamamlandı** (Osman, 21.10); yeniden kurulmayacak. Yeni stil sıradaki reelde kullanılacak.
- **v3.1 (Osman: karakterler konuştuğu kişiye dönsün; yüz/el/kıyafet/aksesuar ayrıntısı; gerçekçi ışık):** terimlerin vektör karşılıkları `hf/art/DERINLIK.md` §8-10. `scripts/portrait.py`: açı tabanlı üç-çeyrek ayrıntılı baş (iris lifleri, göz pınarı, kirpik, kaz ayağı, ten dokusu, SSS kulak), `jacket` (tüvit, kıvrım, dikiş, metal düğme, kravat iğnesi), `hand_cup` (boğumlu parmaklar), `back_shoulder` (omuz üstü ön plan), `light_shafts` (hacimsel ışık), `chiaroscuro`. `depth.Scene.add_figure(look_at=…)` hedefe döner; `Cam(focus=…)` alan derinliği. Demo `hf/demo/build_ots.py` → `hf/renders/ots-demo.mp4`. Zayıf: yüz hâlâ stilize, el-fincan kavrayışı geliştirilmeli.
- **v4 karakter stili (Osman referans verdi, 21.10):** gerçekçi portre yerine **2D çizgi film** (kontur + düz renk + keskin tek ton gölge, büyük baş, ağır kapaklı iri göz, beş parmaklı el, ayrıntılı kıyafet/ayakkabı). `scripts/toon.py` (`toon_figure`, `hand`, `sneaker`, `cel`), sahnede `Scene.add_toon(look_at=…)`. Örnek kare `hf/renders/toon-konusma.png`. Saç modelleri (short/fade/quiff/balding/long/bob) **Osman onayladı (21.10)**. Eksik: arkadan/önden görünüş, oturma pozu, yakın plan büst, ağız-ses senkronu.
- **Üçüncü reel: Selahattin Ülkümen** (21.10). Hikaye/olgular `reels/ulkumen/hikaye.md`, metin `reels/ulkumen/metin.txt`. Ses ElevenLabs Fatih Yıldırım, eleven_v4, tek varyasyon (1190 kredi), flow `zB0IWUjVp1eQLIbzhWAI`, 94,3 sn → `hf/assets/ulkumen/voice.mp3` (git dışı). Kelime zamanları `reels/ulkumen/words.json`, ağız `hf/avatar/mouth-ulkumen.json`. `reels/ulkumen/build.py`: 15 sahne, toon karakterler (`toon.py`'ye outfit=suit/uniform/dress, hat=fedora/officer, prop=paper/suitcase, pose=offer eklendi; üniformada simge yok). Snapshot kontrolü yapıldı, **render alınmadı: Osman gerçek görselleri gönderecek** (yerleşim ona göre). Bekleyen küçük düzeltmeler: yüzleşme sahnesinde ön plan komutanı kadraja (translate 700 1600), `#rlie` balonu top:200px, 151 noktası altın renk.
- **Gündem reeli: Erdemli otoyolu** (21.10, Osman istedi). Araştırma `reels/erdemli-otoyol/arastirma.md`, metin `metin.txt`, ses ElevenLabs flow `W62acadA61Q60tNPkERE` (842 kredi, 66,9 sn) → `hf/assets/erdemli/voice.mp3`; `build.py` 12 sahne (toon + depth; yeni `scripts/toonprops.py`: arkadan araba, gişe, tünel ağzı, viyadük, sıcak hava dalgası). **Render v1** `hf/renders/erdemli-v1.mp4` (71,2 sn, -15,2 LUFS, 4 dk 40 sn render). Açıklama `caption.md`.
- **Avatar** `hf/avatar/osman.svg`: ilk (Okene) sürüm kullanılır; dikleştirilmiş saç denemesi reddedildi (21.10). Ten gradyanı id'si `avskin` (portrait.py'deki `#skin` filtresiyle çakışıp yüzü beyaz bırakıyordu; Ülkümen ve Erdemli v1'de bu hata vardı).
- **Reel: Beyaz saç koparma miti** (24.10, Osman: viral, kaliteli, kapsamlı araştırma, min kredi, onay bekleme). İş akışı (7 ajan: 2 araştırma + viral + adversarial doğrulama + 2 varyant senaryo + hakem/sentez + son kontrol) → `reels/beyaz-sac/arastirma.json` (24 doğrulanmış olgu, kaynaklar). ElevenLabs kotası 612 krediye düşmüştü → metin 599 karaktere kısaltıldı (599 kredi, 46,7 sn; flow `UYtYrDVH3J1foXLEd9u6`). **Kalan ElevenLabs kredisi ≈ 13.** Yeni **v5 tam ekran tema** `scripts/reelkit2.py` (kinetik altyazı, ilerleme çubuğu, nabızlı yuvarlak avatar, flaş/punch/shake), ücretsiz SFX + müzik altlığı `scripts/sfx.py` (whoosh/pop/tick/pluck/heartbeat/riser/boom/ding, ducking, -16 LUFS), çizimler `scripts/hairart.py` (folikül kesiti, makro saç teli, cımbız, banyo/ayna, laboratuvar faresi), toon `pose="pluck"`. Build `reels/beyaz-sac/build.py` (11 sahne), render `hf/renders/beyazsac-v1.mp4` (50,4 sn, -15,5 LUFS), kapak `reels/beyaz-sac/cover.py` → `hf/renders/beyazsac-kapak.jpg`, açıklama `caption.md`.
- **Kural (Osman):** Üretilmiş çizimleri yeniden üretme, `artlib`'den kullan; beğenilmezse orada geliştir. Grafikler gerçekçi ama çizim.

## Yeni oturumda kurulum (sırayla)
1. Dal: `git fetch origin claude/storytelling-reels && git checkout claude/storytelling-reels`
2. `./setup.sh` (npm + .venv + Fluent Emoji + font).
3. `mkdir -p hf/assets/fonts && cp node_modules/@fontsource/montserrat/files/montserrat-latin{,-ext}-{600,800}-normal.woff2 hf/assets/fonts/`
4. `cd hf && npx -y hyperframes@0.8.181 skills update` (motion-blur ve grain-overlay `hf/compositions/components/` içinde, git'te).
5. **Git dışındaki dosyalar (Osman tekrar yükler):**
   - Okene: `hf/assets/okene/` → dalgic-kamera.m4v, hava-cebi-kamera.jpg, okene-portre.jpg, jascon-romorkor.webp, gorsel-4.avif, basinc-odasi-dalgiclar.jpg, voice.mp3 (kesilmiş ses-4)
   - Hodges: `hf/assets/hodges/` → ek-1.jpg, ek-2.jpg, ann-yatak.jpg, cati-polis.jpg, mckinney-aile.jpg, muze.jpg, voice.mp3
   - Avatar kaynak fotoğrafları `hf/assets/avatar/` (çizim avatar `hf/avatar/osman.svg` git'te; fotoğraflar yalnızca yeniden çizim gerekirse)
   - Sesler ElevenLabs'ta da duruyor (flow'lar yukarıda); yeniden üretmeye gerek yok, Osman indirip yükleyebilir.
6. Kelime zamanları (`reels/*/words.json`) ve ağız zarfları (`hf/avatar/mouth-*.json`) git'te; ses aynıysa yeniden çıkarmaya gerek yok.
7. Render: `python3 reels/<id>/build.py && cd hf && npx -y hyperframes@0.8.181 render -o renders/<id>.mp4`

## Açık konular / riskler
- **Konuşan avatar ücretsiz + GPU'suz:** Fotoğraftan dudak senkronlu gerçekçi avatar için açık kaynak seçenekler (LivePortrait, SadTalker, Wav2Lip) GPU ister; bu konteynerde CPU'da çok yavaş olabilir. Alternatifler: kısa bir test ile CPU süresini ölç; ya da Osman kendi facecam'ini çeker; ya da Google Colab (ücretsiz GPU) üzerinde avatar üret, burada birleştir. Fotoğraflar gelince test edilecek.
- Puanlama skill'i (claude.ai'de senkronlu) hâlâ "tamamen vektör, fotoğraf yok" diyor. Yerine geçecek kural yukarıdaki görsel kuralı; skill claude.ai'den güncellenene kadar hakeme bu kuralı ayrıca ver. Gerçek görsel = eksi değil; vektörde "gerçekçilik" puanlanır.
- Daha fazla geçer konu için yeni aday turu yapılabilir (az işlenmiş, Türk izleyiciye yakın hikayeler).
