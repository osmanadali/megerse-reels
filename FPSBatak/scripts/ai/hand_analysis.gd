class_name HandAnalysis
extends RefCounted
## İhale AI'sının 1. adımı: EL ANALİZİ.
##
## Bir eli, belirli bir koz varsayımıyla ölçülebilir özelliklere ayırır.
## Özellikler bilerek basit sayımlardır (kaç As, kaç renk boşluğu...) ki
## TrickEstimator'daki katsayılar simülasyonla kalibre edilebilsin ve her
## tahminin nereden geldiği okunabilsin. Burada hiçbir puan verilmez.

## Özelliklerin sırası TrickEstimator katsayı tablolarıyla aynıdır.
const FEATURE_NAMES: Array[String] = [
	"sabit (ilk eli açma avantajı + taban)",
	"koz uzunluğu",
	"koz As",
	"koz Papaz",
	"koz Kız",
	"koz Vale",
	"yan As",
	"yan korunmuş Papaz (≥2 kart)",
	"yan K-Q dizisi",
	"yan korunmuş Kız (≥3 kart)",
	"renk boşluğu (yan renk)",
	"tek kartlı yan renk",
	"iki kartlı yan renk",
	"koz çakma potansiyeli",
	"uzun yan renk (4 üstü kart)",
]
const F_COUNT := 15


## `hand` elinin `trump` koz varsayımıyla özellik vektörü.
static func features(hand: Array[CardData], trump: int) -> PackedFloat32Array:
	var ranks := {}  # takım -> [değerler]
	for s in CardData.Suit.values():
		ranks[s] = []
	for c in hand:
		ranks[c.suit].append(int(c.rank))
	var f := PackedFloat32Array()
	f.resize(F_COUNT)
	f[0] = 1.0
	var t: Array = ranks[trump]
	f[1] = t.size()
	f[2] = 1.0 if t.has(14) else 0.0
	f[3] = 1.0 if t.has(13) else 0.0
	f[4] = 1.0 if t.has(12) else 0.0
	f[5] = 1.0 if t.has(11) else 0.0
	var shortness := 0  # boşluk=3, tek kart=2, iki kart=1 (çakılabilecek el sayısının kabası)
	for s in CardData.Suit.values():
		if s == trump:
			continue
		var r: Array = ranks[s]
		var n := r.size()
		if r.has(14):
			f[6] += 1.0
		if r.has(13) and n >= 2:
			f[7] += 1.0
		if r.has(13) and r.has(12):
			f[8] += 1.0
		if r.has(12) and n >= 3:
			f[9] += 1.0
		match n:
			0: f[10] += 1.0
			1: f[11] += 1.0
			2: f[12] += 1.0
		shortness += maxi(0, 3 - n)
		f[14] += maxi(0, n - 4)
	# Koz çakma potansiyeli: kısa renkler ancak eldeki koz kadar çakılabilir;
	# ilk iki koz genelde koz çekmeye gider.
	f[13] = mini(shortness, maxi(0, t.size() - 2))
	return f


## Özelliklerin okunur dökümü (hata ayıklama / rapor için).
static func describe(f: PackedFloat32Array) -> String:
	var parts: PackedStringArray = []
	for i in range(1, F_COUNT):
		if f[i] != 0.0:
			parts.append("%s=%d" % [FEATURE_NAMES[i], int(f[i])])
	return ", ".join(parts)
