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
8. ⏳ Sıradaki konu → → düzeltmeler → bağımsız hakem (puanlama skill'i, görsel kuralı güncel haliyle).

## Açık konular / riskler
- **Konuşan avatar ücretsiz + GPU'suz:** Fotoğraftan dudak senkronlu gerçekçi avatar için açık kaynak seçenekler (LivePortrait, SadTalker, Wav2Lip) GPU ister; bu konteynerde CPU'da çok yavaş olabilir. Alternatifler: kısa bir test ile CPU süresini ölç; ya da Osman kendi facecam'ini çeker; ya da Google Colab (ücretsiz GPU) üzerinde avatar üret, burada birleştir. Fotoğraflar gelince test edilecek.
- Puanlama skill'i (claude.ai'de senkronlu) hâlâ "tamamen vektör, fotoğraf yok" diyor. Yerine geçecek kural yukarıdaki görsel kuralı; skill claude.ai'den güncellenene kadar hakeme bu kuralı ayrıca ver. Gerçek görsel = eksi değil; vektörde "gerçekçilik" puanlanır.
- Daha fazla geçer konu için yeni aday turu yapılabilir (az işlenmiş, Türk izleyiciye yakın hikayeler).
