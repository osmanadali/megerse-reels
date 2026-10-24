extends SceneTree
## Geliştirme aracı: ihale AI'sını önce/sonra ölçer.
##
##   godot --headless --path FPSBatak -s res://tools/ai/benchmark_bidding.gd -- <standard|buried> <dağıtım> <tohum> <old|new> [eşik] [zorunlu_eşik] [oldplay]
##
## Her dağıtımda gerçek BidManager ile tam ihale turu oynanır (bütün koltuklar
## aynı AI), ihaleyi alan kendi kozunu seçer (gömmelide gömer + yeri alır) ve
## el, oyundaki kart oynama AI'sıyla (CardTracker + PlayPolicy) sonuna kadar
## oynanır; `oldplay` verilirse eski bağlamsız kart oynamayla. Aynı tohum aynı
## elleri verir; karşılaştırmalar birebir aynı dağıtımlarla yapılır.

const Sim := preload("res://tools/ai/sim_common.gd")
const Legacy := preload("res://tools/ai/legacy_bidding.gd")

func _init() -> void:
	var raw := OS.get_cmdline_user_args()
	var old_play := "oldplay" in raw
	var a := PackedStringArray(Array(raw).filter(func(x): return x != "oldplay"))
	var buried := a[0] == "buried"
	var deals := int(a[1])
	var rng := RandomNumberGenerator.new()
	rng.seed = int(a[2])
	var use_new := a[3] == "new"
	if a.size() > 4:
		BidStrategy.override_threshold = float(a[4])
	if a.size() > 5:
		BidStrategy.override_recipient_threshold = float(a[5])
	var rules := GameRules.buried_bidding() if buried else GameRules.standard_bidding()
	var n := rules.player_count
	var ais: Array = []
	for i in n:
		ais.append(AIPlayer.new(i))
	var forced := 0
	var sum_mu := 0.0; var sum_act := 0.0; var sum_abs := 0.0
	var made := 0; var vol := 0; var vol_made := 0; var f_made := 0
	var sum_bid := 0.0; var sum_vol_bid := 0.0
	var ge := {5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
	var bid_hist := {}
	var bid_made := {}       # teklif -> tutulan
	var bid_p := {}          # teklif -> tahmini tutma olasılıkları toplamı
	var sum_over := 0.0      # gerçek - ihale
	var vol_p := 0.0         # gönüllü tekliflerde tahmini P(tutar) toplamı
	var cal := {}  # tahmin kovası -> [n, gerçek toplamı]
	for d in deals:
		var deck := DeckManager.new(rng.randi())
		deck.shuffle()
		var hands := deck.deal(n, rules.cards_per_player)
		var kitty := deck.take_remaining()
		var dealer := d % n
		var bm := BidManager.new(rules, dealer)
		while not bm.is_finished():
			var s := bm.current_seat()
			var choice: int
			if use_new:
				choice = ais[s].choose_bid_in_context(hands[s], BidContext.from_bid_manager(bm, rules))
			else:
				choice = Legacy.choose_bid(hands[s], bm.valid_bids(), rules.buried_cards)
			if choice == BidManager.PASS or not bm.bid(choice):
				bm.pass_turn()
		var dec := bm.current_holder
		var bid := bm.current_bid
		var h: Array[CardData] = hands[dec]
		var trump: int
		var mu: float
		var sigma := 1.0
		if use_new:
			var e := TrickEstimator.best(h, rules)
			trump = e.trump
			mu = e.mu
			sigma = e.sigma
		else:
			trump = Legacy.choose_trump(h)
			mu = Legacy.estimate_tricks(h) + rules.buried_cards * Legacy.KITTY_TRICK_VALUE
		var hs := Sim.copy_hands(hands)
		var buried_cards: Array[CardData] = []
		if buried:
			buried_cards = Sim.apply_bury_and_kitty(hs[dec], kitty, trump)
		var got: int = Sim.play_out(hs, trump, dec)[dec] if old_play \
			else Sim.play_out_current(rules, hs, trump, dec, bid, buried_cards)[dec]
		var p_ok := TrickEstimator.prob_at_least(bid, mu, sigma)
		sum_over += got - bid
		bid_p[bid] = bid_p.get(bid, 0.0) + p_ok
		sum_mu += mu; sum_act += got; sum_abs += absf(got - mu)
		var k := int(floor(mu))
		if not cal.has(k):
			cal[k] = [0, 0.0]
		cal[k][0] += 1; cal[k][1] += got
		for g in ge:
			if got >= g:
				ge[g] += 1
		sum_bid += bid
		bid_hist[bid] = bid_hist.get(bid, 0) + 1
		var ok := got >= bid
		if ok:
			made += 1
			bid_made[bid] = bid_made.get(bid, 0) + 1
		if bm.forced:
			forced += 1
			if ok:
				f_made += 1
		else:
			vol += 1
			sum_vol_bid += bid
			vol_p += p_ok
			if ok:
				vol_made += 1
	var N := float(deals)
	print("SONUÇ %s %s%s n=%d tohum=%s eşik=%s zorunlu_eşik=%s" % ["GÖMMELİ" if buried else "NORMAL",
		"YENİ" if use_new else "ESKİ", " (eski kart oynama)" if old_play else "", deals, a[2],
		a[4] if a.size() > 4 else "-", a[5] if a.size() > 5 else "-"])
	print("  herkes pas (zorunlu ihale)     : %5.1f%%" % (100.0 * forced / N))
	print("  tahmin edilen löve (ort.)      : %5.2f" % (sum_mu / N))
	print("  gerçek löve (ort.)             : %5.2f" % (sum_act / N))
	print("  sapma (gerçek − tahmin)        : %+5.2f" % ((sum_act - sum_mu) / N))
	print("  ortalama |hata| (MAE)          : %5.2f" % (sum_abs / N))
	print("  gerçek − ihale (üstü/altı)     : %+5.2f" % (sum_over / N))
	print("  ihale tutma (tümü)             : %5.1f%%" % (100.0 * made / N))
	print("  ihale tutma (gönüllü teklif)   : %5.1f%%  (n=%d)  tahmini P ort. %5.1f%%" % [
		100.0 * vol_made / maxi(vol, 1), vol, 100.0 * vol_p / maxi(vol, 1)])
	print("  ihale tutma (zorunlu)          : %5.1f%%  (n=%d)" % [100.0 * f_made / maxi(forced, 1), forced])
	print("  ortalama ihale (tümü / gönüllü): %5.2f / %5.2f" % [sum_bid / N, sum_vol_bid / maxi(vol, 1)])
	print("  ihaleyi alanın 5+/6+/7+/8+/9+/10+: %4.1f%% / %4.1f%% / %4.1f%% / %4.1f%% / %4.1f%% / %4.1f%%" % [
		100.0 * ge[5] / N, 100.0 * ge[6] / N, 100.0 * ge[7] / N, 100.0 * ge[8] / N, 100.0 * ge[9] / N,
		100.0 * ge[10] / N])
	var keys := bid_hist.keys(); keys.sort()
	var parts: PackedStringArray = []
	for b in keys:
		parts.append("%d:%.1f%%" % [b, 100.0 * bid_hist[b] / N])
	print("  ihale dağılımı                 : " + "  ".join(parts))
	var sparts: PackedStringArray = []
	for b in keys:
		sparts.append("%d:%.1f%%(P%.0f%%,n=%d)" % [b, 100.0 * bid_made.get(b, 0) / bid_hist[b],
			100.0 * bid_p[b] / bid_hist[b], bid_hist[b]])
	print("  teklife göre tutma (tahmini P)  : " + "  ".join(sparts))
	var ck := cal.keys(); ck.sort()
	var cparts: PackedStringArray = []
	for c in ck:
		if cal[c][0] >= 30:
			cparts.append("%d→%.2f" % [c, cal[c][1] / cal[c][0]])
	print("  kalibrasyon floor(tahmin)→gerçek: " + "  ".join(cparts))
	quit()
