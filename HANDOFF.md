# HANDOFF: yeni sohbette buradan devam et

Son güncelleme: 20.10.2026. Repo: `osmanadali/megerse-reels`, dal `claude/storytelling-reels`.
Yeni sohbette ilk mesaj: "HANDOFF.md'yi oku ve kaldığın yerden devam et."

## Hedef (Osman'ın kararları)
- Format: **storytelling reels**, 1080×1920, Türkçe.
- **Tek ücretli araç: ElevenLabs, yalnızca seslendirme.** Geri kalan her şey ücretsiz/açık kaynak. (Apify iptal edildi.)
- Ekran: altta veya sol altta **facecam tarzı avatar** (Osman'ın fotoğraflarından) hikayeyi anlatır; geri kalan alanda hikaye görselleri döner.
- Altyazı sesle **kelime kelime senkron**.
- Görseller **gerçekçi** (artık yalnızca vektör çizim değil): Osman internetten görsel bulur, nasıl kullanılacağını söyler. Animasyon, geçiş, kamera hareketi kaliteli olmalı; düz kesme yok.
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
2. ⏳ Osman: geçen konular için görsel araştırması yapacak ve kullanım talimatı verecek.
3. ⏳ Osman: avatar için fotoğraflarını gönderecek.
4. ⏳ Sonraki adımlar: senaryo → ElevenLabs ses → kelime zamanları (faster-whisper) → HyperFrames kompozisyonu (avatar + görseller + altyazı) → render → puanlama skill'i.

## Açık konular / riskler
- **Konuşan avatar ücretsiz + GPU'suz:** Fotoğraftan dudak senkronlu gerçekçi avatar için açık kaynak seçenekler (LivePortrait, SadTalker, Wav2Lip) GPU ister; bu konteynerde CPU'da çok yavaş olabilir. Alternatifler: kısa bir test ile CPU süresini ölç; ya da Osman kendi facecam'ini çeker; ya da Google Colab (ücretsiz GPU) üzerinde avatar üret, burada birleştir. Fotoğraflar gelince test edilecek.
- Puanlama skill'indeki "tamamen vektör çizim, fotoğraf yok" kuralı yeni formatla çelişiyor; skill güncellenmeli (Osman onaylarsa).
- Daha fazla geçer konu için yeni aday turu yapılabilir (az işlenmiş, Türk izleyiciye yakın hikayeler).
