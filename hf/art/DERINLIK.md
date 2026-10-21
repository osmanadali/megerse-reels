# Derinlik ve sahneleme standardı (v3)

Osman'ın v2 eleştirisi (20.10.2026): animasyonlar Karagöz-Hacivat gibi düz; derinlik yok; sağdan soldan simge kaydırmak basit; cisim ve kişi tasarımı eksik (ayakta duran karakterin bacağı yoktu); konuşan karakter izleyiciye değil yanındakine dönük olmalı.
Bu dosya kural, `scripts/depth.py` uygulamasıdır. Yeni sahnelerde **önce bu liste**, sonra çizim.

## 1. Çizgisel perspektif
- Her sahnenin bir `Cam`'i var: ufuk çizgisi (`horizon`), kaçış noktası (`vpx`), göz yüksekliği (`eye`). Nesneler ekran pikseliyle değil **dünya koordinatıyla** (x, z) yerleştirilir: `Scene.add(x, z, çizim, çizim_boyu, gerçek_boy)`.
- Ölçek `k = f / z`: aynı boydaki iki nesneden uzaktaki küçük kalır. Yol, ray, kaldırım kenarı gibi çizgiler kaçış noktasında birleşir (`add_road`).
- Göz yüksekliği kuralı: kamera ayakta bir insan boyundaysa, düz zemindeki tüm yetişkinlerin başları ufuk çizgisi civarında kalır, uzaklık ne olursa olsun. (Cam bunu kendiliğinden sağlar; elle yerleştirirken unutma.)

## 2. Üst üste bindirme (katmanlar)
- Her sahnede ön, orta ve arka plan olmalı. Scene nesneleri uzaktan yakına sıralar; yakındaki uzaktakini kısmen örter.
- Ön plana kadrajı kesen bir nesne koy (ağaç gövdesi, kapı kenarı, omuz, `focus=False` → bulanık). Bu tek başına derinlik hissini ikiye katlar.

## 3. Işık, gölgelendirme, düşen gölge
- Sahnede **tek ışık yönü**: `Cam(sun=(x, z), alt=derece)`. Tüm nesneler ona göre gölgelenir (`lsh` örtüsü: ışık tarafı açık, karşı taraf koyu).
- Tercih: ışık önden-yandan (`sun` z<0); gölgeler arkaya düşer, yüzler aydınlık kalır.
- Yerde duran her şeyin **temas gölgesi** (ayak altı koyu leke) ve **düşen gölgesi** olur; ikisi de yere perspektifle izdüşer (`shadow_polys`). Gölgesiz nesne havada asılı durur: yasak.

## 4. Atmosferik (hava) perspektifi
- Uzaklık bandı 0-5 (`Cam.band`): uzaktaki nesne pus rengine karışır, doygunluğu düşer, hafif bulanıklaşır (`atm0..atm5` filtreleri).
- Ayrıntı yakında: doku, düğme, yaprak. Uzakta siluet yeter.
- Çizgi kalınlığı ölçekle birlikte incelir (k çarpanı); uzak nesneye kalın kontur koyma.

## 5. Mekânsal sıkışma
- Tekrarlanan nesneler (direk, ağaç, pencere, şerit çizgisi) **eşit dünya aralığıyla** dizilir (`Scene.row`): ekranda uzağa doğru aralık kendiliğinden daralır. Ekranda eşit aralık = yanlış.

## 6. Karakter
- `figure()`: her zaman **tam vücut** (bacak, ayakkabı, temas gölgesi). Kadraj keserse kesim kadrajın ya da öndeki nesnenin işi olsun, çizimin değil.
- Yön: `turn` 0 önden, .5 üç-çeyrek, .8 neredeyse profil; `flip` sola bakar. Üç-çeyrekte uzak omuz ve uzak göz daralır, yüz bakış yönüne kayar, yakın kulak görünür, uzak kol ve bacak gövdenin arkasında kalıp koyulaşır.
- **Konuşma:** iki kişi birbirine üç-çeyrek döner (`turn≈.5`, biri `flip=True`). İzleyiciye yalnızca anlatıcı (avatar) bakar.
- 180° kuralı: aynı sahnede A solda, B sağda kalır; sahneler arasında taraf değiştirme.
- Poz: `stand`, `talk` (yakın kol jest), `walk` (bacaklar açık, kollar ters salınır).

## 7. Hareket (animasyon) kuralları
- **Yasak:** simge veya nesnenin kadraj dışından düz kayarak girmesi, düz büyüyüp küçülme (scale pop), her şeyin aynı hızda hareketi.
- **Kamera dünyada hareket eder** (`Scene.camera_js(dx, dz, dy)`): yakın nesneler hızlı, uzaktakiler yavaş kayar (çok düzlemli kamera / parallax). Her sahnede en az bir kamera hareketi: yaklaşma (dolly), yana kayma (truck) veya ikisi.
- Bir şey sahneye girecekse **dünyanın içinden** girer: kapıdan çıkar, yoldan yürüyerek gelir, kamera dönüp onu bulur, ön plandaki nesnenin arkasından açılır, ışık yanınca görünür.
- Odak kaydırma (rack focus): önemli an gelince ön plan bulanıklaşır, konu netleşir.
- Geçişler: kamera bir nesnenin önünden geçerek (wipe by foreground) veya eşleşen hareketle; düz kesme yok.

## Kontrol listesi (her sahne)
- [ ] Ufuk + kaçış noktası belli, nesneler dünya koordinatında
- [ ] Ön / orta / arka plan var, en az bir örtüşme
- [ ] Tek ışık yönü, her nesnede temas + düşen gölge
- [ ] Uzak nesneler puslu ve ayrıntısız
- [ ] Tekrarlanan nesneler eşit dünya aralığında
- [ ] Karakterler tam boy; konuşanlar birbirine dönük
- [ ] Kamera hareketi var; kayarak giren simge yok

Kaynaklar: Osman'ın 5 başlıklı notu (realismtoday.com, pelintogrul.com), çok düzlemli kamera (en.wikipedia.org/wiki/Multiplane_camera), Adobe Animate Layer Depth, 180° kuralı (artlist.io/blog/180-degree-rule).
Demo: `python3 hf/demo/build_demo.py && (cd hf && npx -y hyperframes@0.8.181 render -c demo/derinlik.html -o renders/derinlik-demo.mp4)`.

---

# v3.1: sahne hissi, ayrıntı, ışık (Osman, 20.10.2026)

Osman'ın verdiği terimler yapay zekâ görsel istemleri. Biz çizimi kodla yapıyoruz, o yüzden her terimin **vektör karşılığı** aşağıda; kod `scripts/portrait.py` (yakın plan) ve `scripts/depth.py` (geniş plan).

## 8. Karakter etkileşimi
| Terim | Bizde |
|---|---|
| facing each other / turning towards the interlocutor | `Scene.add_figure(x, z, look_at=(x2, z2))`: dönüş açısı ve yönü hedeften hesaplanır. Konuşmasa da sahnedeki karakter bir şeye bakar (kişi, nesne, olay); boşluğa ya da izleyiciye bakmaz. |
| gazing at / eye contact / subtle glance | `bust(gaze=(gx, gy))`: iris hedefe kayar. Yoğun temas: iris tam hedefte, kapak açık. Hafif bakış: gx küçük, kapak hafif kısık (`expr.lid=.85`). |
| candid mid-conversation | Poz donmuş değil: baş hafif sallanır, nefes (gövde ölçeği ±%0.6), göz kırpma, ağız konuşan kişide açılıp kapanır, dinleyende mikro ifade değişir. |
| over-the-shoulder shot | `back_shoulder()` ön planda, bulanık (`dofFG`), kadrajın 1/4–1/3'ünü örter; karşıdaki `bust()` üç-çeyrek ona dönük, odakta. Ön plan kameradan daha hızlı kayar (parallax). 180° kuralı: A hep solda, B hep sağda. |

## 9. Anatomik ayrıntı (yakın plan)
| Terim | Bizde |
|---|---|
| micro-expressions | `expr`: `brow` (kaldır), `knit` (çat), `smile`, `open`, `lid`. Değişimler 0,2-0,4 sn, küçük genlik. |
| skin pores, texture | `#skin` filtresi (ince fraktal gürültü yalnızca tende), yanak kızarıklığı (`#blush`). |
| wrinkles around eyes | dış köşede kaz ayağı, alt kapak çizgisi, nazolabial kıvrım; `age` 0–1 ile koyulaşır. |
| iris texture, tear duct | limbus halkalı iris + ışınsal lifler, ışık yönünde parıltı + ikinci küçük yansıma, iç köşede pembe göz pınarı, üst kapağın göze düşen gölgesi, kapak kıvrımı, kirpikler. |
| articulated fingers, hand action | `hand_cup()`: ayrı parmaklar, boğum çizgileri, tırnaklar, alt yüzeyde gölge, kavrayan poz. Yeni eller aynı yapıyla: el ne yapıyorsa (kavrar, gösterir, dayanır) poz ona göre. |
| fabric texture, folds, stitching | `#tweed` dokusu; gerilme noktalarından (dirsek, koltuk altı, bel) çıkan kıvrımlar; dikiş = kesik çizgi (yaka, omuz). |
| metallic luster / brushed metal | `#metalB` (parlak radyal: düğme, inci, yüzük), `#brushed` (fırçalanmış: kravat iğnesi, saat kasası). |

## 10. Işık, mekân, nesne
| Terim | Bizde |
|---|---|
| volumetric lighting | `light_shafts()`: pencereden giren, açılarak sönen huzmeler (screen karışım) + uçuşan toz. |
| subsurface scattering | Işığa bakan kulak kenarında ve burun kanadında sıcak kırmızı geçirgenlik. |
| chiaroscuro / cinematic dramatic lighting | `chiaroscuro(cx, cy)`: anahtar ışığın dışı karanlığa düşer; tek, yönlü ışık (`pl`/`pr` örtüsü). |
| ambient occlusion | Birleşim yerlerinde yumuşak koyu gölge: yaka-boyun, çene altı, burun altı, alt dudak altı, fincan-masa, masa kenarı. |
| cast shadows | `shadow_polys()` (geniş plan, perspektifli); yakın planda yönlü yumuşak gölge. |
| depth of field | `Cam(focus=…)`, `dofFG` / `dofBG`: konu net, ön plan ve arka plan bulanık; önemli anda odak kaydırılır. |

Demo: `python3 hf/demo/build_ots.py && (cd hf && npx -y hyperframes@0.8.181 render -c demo/ots.html -o renders/ots-demo.mp4)`.

---

# v4: karakter stili = 2D çizgi film (Osman'ın referansı, 21.10.2026)
Referans: `hf/assets/ref/stil-1.avif` (git dışı). Karakterler artık **gerçekçi portre değil**, `scripts/toon.py`:
- Koyu sürekli kontur (`INK`), düz renk + tek ton keskin gölge (`cel()`: gölge ışığın tersindeki kenarda sert şerit).
- Saç: `hair_style` = short | fade | quiff | balding | long | bob (hacim, tutamlı saç çizgisi, favori, ense, akış çizgileri, tırtıklı parlaklık; uzun saçta omuz arkası kütle). Kulak saçın üstüne çizilir.
- Büyük baş, iri göz: beyaz + koyu iris + parıltı + **ağır üst kapak** (`expr.lid`), kalın kaş, basit burun çizgisi, ağız (`smile`, `talk`).
- Eller beş parmaklı (`hand(pose=open|point|fist|hold)`), kıyafette kıvrım çizgisi, cep, kemer tokası, çizgili çorap, spor ayakkabı (taban, burun, bağcık).
- Sahnede: `Scene.add_toon(x, z, look_at=(x2, z2), ...)` → konuştuğu kişiye döner, gözü ona bakar; perspektif, gölge, pus, kamera sistemi aynen geçerli.
- `portrait.py` (gerçekçi yakın plan) bu stil için kullanılmaz; ışık/mekân araçları (`light_shafts`, `chiaroscuro`, DoF) kullanılabilir.
