class_name TrickEstimator
extends RefCounted
## İhale AI'sının 2. ve 3. adımı: BEKLENEN LÖVE ve TEKLİF BAŞARI OLASILIĞI.
##
## Beklenen löve, HandAnalysis özelliklerinin doğrusal birleşimidir:
##     μ = Σ katsayı[i] × özellik[i]
## Katsayılar elle verilmedi; tools/ai/calibrate_bidding.gd ile oyundaki kart
## oynama AI'sı (CardTracker + PlayPolicy, NORMAL) birbirine karşı oynatılarak
## (en küçük kareler) ölçüldü:
##   Normal İhaleli : 10.000 dağıtım × 4 koz = 40.000 el (tohum 1)
##   Gömmeli İhaleli:  6.000 dağıtım × 4 koz = 24.000 el (tohum 2)
## (İlk kalibrasyon eski bağlamsız kart oynamayla yapılmıştı; güncel AI daha
## çok löve aldığı için yeniden kalibre edildi.)
## Ölçümde ihaleyi alan ilk löveyi açtığı için "ilk eli açma avantajı" sabit
## terimin içindedir.
##
## Gerçek löve sayısı tahmin etrafında dağılır; dağılımın genişliği de ölçüldü
## (σ, tahmin büyüdükçe hafifçe artar). Bir teklifin tutma olasılığı:
##     P(löve ≥ k) = 1 − Φ((k − 0,5 − μ) / σ(μ))      (Φ: normal dağılım)
##
## Gömmeli modda AI, ihaleden önce hangi kartları gömeceğini bildiği için
## özellikler GÖMMEDEN SONRA elde kalacak 12 karttan hesaplanır (boşaltılan
## renkler, kalan koz sayısı); yerden gelecek 4 kartın ortalama katkısı sabit
## terimdedir. Gömmenin değeri yalnızca gömmeli modda uygulanır.

## Katsayılar HandAnalysis.FEATURE_NAMES sırasıyla.
const COEF_STANDARD: Array[float] = [-0.5464, 0.4510, 0.9231, 0.6679, 0.4231, 0.2415, 0.9562,
	0.6403, -0.0628, 0.2589, 0.9062, 0.5171, 0.1260, 0.1938, -0.0380]
const COEF_BURIED: Array[float] = [1.3855, 0.4427, 0.7889, 0.5499, 0.3630, 0.1414, 0.9080,
	0.7320, 0.1787, 0.3975, 0.5823, 0.3507, 0.1504, 0.2791, -0.0402]
## σ(μ) = a + b·μ
const SIGMA_STANDARD := Vector2(0.8467, 0.0295)
const SIGMA_BURIED := Vector2(1.2769, 0.0510)


## `hand` elinin `trump` kozla beklenen löve tahmini.
## Dönen sözlük: mu, sigma, features (açıklama için), analyzed (özelliklerin
## hesaplandığı el: gömmelide gömülecekler çıkarılmış hali).
static func estimate(hand: Array[CardData], trump: int, rules: GameRules) -> Dictionary:
	var buried := rules.buried_cards > 0
	var analyzed: Array[CardData] = hand
	if buried:
		analyzed = hand.duplicate()
		for c in AIPlayer.choose_bury(hand, rules.buried_cards, trump):
			analyzed.erase(c)
	var f := HandAnalysis.features(analyzed, trump)
	var coef := COEF_BURIED if buried else COEF_STANDARD
	var mu := 0.0
	for i in f.size():
		mu += coef[i] * f[i]
	var sg := SIGMA_BURIED if buried else SIGMA_STANDARD
	return {"mu": mu, "sigma": maxf(0.5, sg.x + sg.y * mu), "features": f, "analyzed": analyzed}


## En yüksek beklenen löveyi veren koz ve o kozla tahmin.
static func best(hand: Array[CardData], rules: GameRules) -> Dictionary:
	var out := {}
	for suit in CardData.Suit.values():
		var e := estimate(hand, suit, rules)
		if out.is_empty() or e.mu > out.mu:
			out = e
			out["trump"] = suit
	return out


## P(alınan löve ≥ k).
static func prob_at_least(k: int, mu: float, sigma: float) -> float:
	return 1.0 - normal_cdf((k - 0.5 - mu) / sigma)


## Standart normal dağılım fonksiyonu (Abramowitz–Stegun 7.1.26, hata < 1.5e-7).
static func normal_cdf(z: float) -> float:
	var x := absf(z) / sqrt(2.0)
	var t := 1.0 / (1.0 + 0.3275911 * x)
	var y := 1.0 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t \
		+ 0.254829592) * t * exp(-x * x)
	return 0.5 * (1.0 + (y if z >= 0.0 else -y))
