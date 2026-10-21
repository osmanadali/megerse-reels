extends SceneTree
## Geliştirme aracı: TrickEstimator katsayılarını simülasyonla kalibre eder.
##
##   godot --headless --path FPSBatak -s res://tools/ai/calibrate_bidding.gd -- standard 10000 1
##   godot --headless --path FPSBatak -s res://tools/ai/calibrate_bidding.gd -- buried 6000 2
##
## Her dağıtımda koltuk 0'ın eli DÖRT koz adayının her biriyle ayrı ayrı
## oynatılır (gömmelide önce o koza göre gömülür, sonra yer alınır). Elin
## özellikleri (HandAnalysis) ile gerçekte alınan löve arasında en küçük
## kareler doğrusu kurulur; ayrıca tahmin hatasının dağılımı ölçülür.

const Sim := preload("res://tools/ai/sim_common.gd")

func _init() -> void:
	var args := OS.get_cmdline_user_args()
	var buried := args[0] == "buried"
	var deals := int(args[1])
	var rng := RandomNumberGenerator.new()
	rng.seed = int(args[2])
	var rules := GameRules.buried_bidding() if buried else GameRules.standard_bidding()
	var p := HandAnalysis.F_COUNT
	var xtx: Array = []
	for i in p:
		var row := PackedFloat64Array()
		row.resize(p)
		xtx.append(row)
	var xty := PackedFloat64Array()
	xty.resize(p)
	var rows: Array = []   # [özellikler, gerçek]
	var t0 := Time.get_ticks_msec()
	for d in deals:
		var deck := DeckManager.new(rng.randi())
		deck.shuffle()
		var hands := deck.deal(rules.player_count, rules.cards_per_player)
		var kitty := deck.take_remaining()
		for trump in 4:
			var hs := Sim.copy_hands(hands)
			var h0: Array[CardData] = hs[0]
			if buried:
				Sim.apply_bury_and_kitty(h0, kitty, trump)
				# Özellikler: gömmeden sonra, yeri almadan önceki 12 kart (AI ihale anında bunu bilebilir).
			var known: Array[CardData] = h0.slice(0, h0.size() - kitty.size()) if buried else h0.duplicate()
			var f := HandAnalysis.features(known, trump)
			var y: int = Sim.play_out(hs, trump, 0)[0]
			for i in p:
				xty[i] += f[i] * y
				for j in p:
					xtx[i][j] += f[i] * f[j]
			rows.append([f, y])
		if d % 2000 == 1999:
			printerr("  %d / %d dağıtım (%.0f sn)" % [d + 1, deals, (Time.get_ticks_msec() - t0) / 1000.0])
	var w := _solve(xtx, xty)
	# Tahmin hatası
	var se := 0.0
	var buckets := {}
	for r in rows:
		var mu := _dot(w, r[0])
		var e: float = r[1] - mu
		se += e * e
		var b := int(floor(mu))
		if not buckets.has(b):
			buckets[b] = [0, 0.0, 0.0]
		buckets[b][0] += 1
		buckets[b][1] += r[1]
		buckets[b][2] += e * e
	var sigma := sqrt(se / rows.size())
	print("MOD: %s, örnek: %d el x 4 koz = %d" % ["GÖMMELİ" if buried else "NORMAL", deals, rows.size()])
	print("Katsayılar:")
	for i in p:
		print("  %+.4f  %s" % [w[i], HandAnalysis.FEATURE_NAMES[i]])
	var lit: PackedStringArray = []
	for x in w:
		lit.append("%.4f" % x)
	print("GDScript: [%s]" % ", ".join(lit))
	print("Genel hata sapması (sigma): %.4f" % sigma)
	var keys := buckets.keys()
	keys.sort()
	print("Tahmin kovası → ortalama gerçek, kova sigması:")
	# σ(μ) = s0 + s1·μ : kova sigmalarına örnek sayısıyla ağırlıklı doğru.
	var sw := 0.0; var sx := 0.0; var sy := 0.0; var sxx := 0.0; var sxy := 0.0
	for k in keys:
		var b: Array = buckets[k]
		var sg: float = sqrt(b[2] / b[0])
		print("  μ∈[%d,%d) → gerçek %.2f, σ=%.3f  (n=%d)" % [k, k + 1, b[1] / b[0], sg, b[0]])
		var x: float = k + 0.5
		sw += b[0]; sx += b[0] * x; sy += b[0] * sg; sxx += b[0] * x * x; sxy += b[0] * x * sg
	var s1 := (sw * sxy - sx * sy) / (sw * sxx - sx * sx)
	var s0 := (sy - s1 * sx) / sw
	print("σ(μ) = %.4f + %.4f·μ" % [s0, s1])
	quit()


static func _dot(w: PackedFloat64Array, f: PackedFloat32Array) -> float:
	var s := 0.0
	for i in w.size():
		s += w[i] * f[i]
	return s


## Gauss eliminasyonu (küçük ridge düzenlemesiyle; nadir özelliklerde kararlılık için).
static func _solve(a_in: Array, b_in: PackedFloat64Array) -> PackedFloat64Array:
	var n := b_in.size()
	var a: Array = []
	for i in n:
		var row: PackedFloat64Array = a_in[i].duplicate()
		row[i] += 1e-3
		a.append(row)
	var b := b_in.duplicate()
	for col in n:
		var piv := col
		for r in range(col + 1, n):
			if absf(a[r][col]) > absf(a[piv][col]):
				piv = r
		var tmp = a[col]; a[col] = a[piv]; a[piv] = tmp
		var tb := b[col]; b[col] = b[piv]; b[piv] = tb
		for r in range(col + 1, n):
			var factor: float = a[r][col] / a[col][col]
			for c2 in range(col, n):
				a[r][c2] -= factor * a[col][c2]
			b[r] -= factor * b[col]
	var x := PackedFloat64Array()
	x.resize(n)
	for i in range(n - 1, -1, -1):
		var s := b[i]
		for j in range(i + 1, n):
			s -= a[i][j] * x[j]
		x[i] = s / a[i][i]
	return x
