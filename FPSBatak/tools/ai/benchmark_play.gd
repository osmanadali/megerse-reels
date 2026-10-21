extends SceneTree
## Geliştirme aracı: kart oynama AI'sını önce/sonra ölçer (oyunda kullanılmaz).
##
##   godot --headless --path FPSBatak -s res://tools/ai/benchmark_play.gd -- <standard|buried> <dağıtım> <tohum> <politika>
## politika: old | normal | hard | newbidder (yeni ihale sahibi, eski savunanlar)
##           | newdefenders (eski ihale sahibi, yeni savunanlar)
##           | "<ihale_sahibi>/<savunanlar>" her biri old|new|hard|newlead|newfollow
##             (newlead: yeni motor yalnızca açılışta, newfollow: yalnızca takipte)
## Sonraki argümanlar ağırlık denemesi: FUTURE_DISCOUNT=0.6 gibi (PlayPolicy.W).
##
## Aynı tohum → aynı dağıtımlar ve aynı ihaleler (ihale AI'sı kart oynamadan
## bağımsızdır). Bütün koltuklar aynı kart AI'sıyla oynar. Ölçütleri her şeyi
## gören bir GÖZLEMCİ sayar; AI'ların kararlarına hiçbir şekilde karışmaz.
## AI'lar yalnızca CardTracker'daki açık bilgiyi ve kendi ellerini görür.

const Sim := preload("res://tools/ai/sim_common.gd")

var m := {}

func inc(k: String, v := 1.0) -> void:
	m[k] = m.get(k, 0.0) + v


func _init() -> void:
	var a := OS.get_cmdline_user_args()
	var rules := GameRules.buried_bidding() if a[0] == "buried" else GameRules.standard_bidding()
	var deals := int(a[1])
	var rng := RandomNumberGenerator.new()
	rng.seed = int(a[2])
	var policy: String = a[3]
	if policy == "newbidder":
		policy = "new/old"
	elif policy == "newdefenders":
		policy = "old/new"
	elif not "/" in policy:
		policy = "%s/%s" % [policy, policy]
	for kv in a.slice(4):
		var p := kv.split("=")
		PlayPolicy.W[p[0]] = float(p[1])
	var n := rules.player_count
	var ais: Array = []
	for i in n:
		ais.append(AIPlayer.new(i))
	var t0 := Time.get_ticks_msec()
	for d in deals:
		var deck := DeckManager.new(rng.randi())
		deck.shuffle()
		var hands := deck.deal(n, rules.cards_per_player)
		var kitty := deck.take_remaining()
		var bm := BidManager.new(rules, d % n)
		while not bm.is_finished():
			var s := bm.current_seat()
			var ch: int = ais[s].choose_bid_in_context(hands[s], BidContext.from_bid_manager(bm, rules))
			if ch == BidManager.PASS or not bm.bid(ch):
				bm.pass_turn()
		var dec := bm.current_holder
		var bid := bm.current_bid
		var mu: float = TrickEstimator.best(hands[dec], rules).mu
		var trump := AIPlayer.choose_trump(hands[dec], rules)
		var buried: Array[CardData] = []
		if rules.buried_cards > 0:
			var h0: Array[CardData] = hands[dec]
			buried = AIPlayer.choose_bury(h0, rules.buried_cards, trump)
			for c in buried:
				h0.erase(c)
			h0.append_array(kitty)
		_play(rules, hands, trump, dec, bid, buried, ais, policy)
		inc("el")
		inc("tahmin edilen löve (ihale sahibi)", mu)
	var N: float = m["el"]
	print("KART AI ÖLÇÜMÜ %s %s n=%d tohum=%s (%.0f sn)" % ["GÖMMELİ" if a[0] == "buried" else "NORMAL",
		policy.to_upper(), deals, a[2], (Time.get_ticks_msec() - t0) / 1000.0])
	var keys := m.keys()
	keys.sort()
	for k in keys:
		if k == "el" or k.begins_with("_"):
			continue
		print("  %-58s %8.3f" % [k, m[k] / N])
	print("  %-58s %8.1f%%" % ["ihale tutma oranı", 100.0 * m.get("_tuttu", 0.0) / N])
	print("  %-58s %8.1f%%" % ["ihale batırma oranı", 100.0 - 100.0 * m.get("_tuttu", 0.0) / N])
	print("  %-58s %8.1f%%" % ["savunanın sıfır löve oranı (savunan-el başına)",
		100.0 * m.get("_sıfır", 0.0) / m.get("_savunan", 1.0)])
	print("  %-58s %8.1f%%" % ["açılış kalitesi: açılan löveyi açanın alması (ihale sahibi)",
		100.0 * m.get("_açılış_kazandı_i", 0.0) / maxf(m.get("_açılış_i", 1.0), 1.0)])
	print("  %-58s %8.1f%%" % ["açılış kalitesi: açılan löveyi açanın alması (savunan)",
		100.0 * m.get("_açılış_kazandı_s", 0.0) / maxf(m.get("_açılış_s", 1.0), 1.0)])
	print("  %-58s %8d" % ["kural ihlali (yasal olmayan kart seçimi)", int(m.get("_ihlal", 0.0))])
	quit()


func _play(rules: GameRules, hands: Array, trump: int, dec: int, bid: int, buried: Array[CardData],
		ais: Array, policy: String) -> void:
	var n := hands.size()
	var tr := CardTracker.new(n, trump, dec, bid, hands[0].size(), buried.size())
	var total: int = hands[0].size()
	var leader := dec
	for t in total:
		var trick: Array[CardData] = []
		var seats: Array[int] = []
		var winning_at_play := {}
		var seat := leader
		for k in n:
			var h: Array[CardData] = hands[seat]
			var legal := BatakRules.legal_cards(h, trick, trump, tr.trump_broken)
			var card: CardData
			var mine: String = policy.split("/")[0 if seat == dec else 1]
			var use_old := mine == "old" or (mine == "newlead" and not trick.is_empty()) \
				or (mine == "newfollow" and trick.is_empty())
			ais[seat].difficulty = AIPlayer.Difficulty.HARD if mine == "hard" else AIPlayer.Difficulty.NORMAL
			if use_old:
				card = ais[seat].choose_card(legal, trick, trump)
			else:
				var ctx := PlayContext.build(rules, seat, h, legal, trick, seats, tr,
					buried if seat == dec else ([] as Array[CardData]))
				card = ais[seat].choose_card_in_context(ctx)
			if not legal.has(card):
				inc("_ihlal")
			_observe(card, seat, trick, seats, hands, trump, dec, tr, legal, total - t)
			if not trick.is_empty():
				var cur: CardData = trick[BatakRules.trick_winner(trick, trump)]
				if BatakRules.beats(card, cur, trick[0].suit, trump) and k < n - 1:
					winning_at_play[seat] = card
			h.erase(card)
			tr.record_play(seat, card)
			trick.append(card)
			seats.append(seat)
			seat = (seat + 1) % n
		var w := BatakRules.trick_winner(trick, trump)
		var ws := seats[w]
		tr.record_trick_end(ws)
		# Kazanmak için oynanıp sonra geçilen kartlar
		for s2 in winning_at_play:
			if s2 != ws:
				var c2: CardData = winning_at_play[s2]
				inc("kazanırken oynanıp sonra kaybedilen kart")
				if c2.suit != trump and c2.rank >= 12:
					inc("gereksiz yüksek kart harcama (geçilen Q/K/A)")
		for i in n:
			var c3: CardData = trick[i]
			if c3.suit == trump and trick[0].suit != trump and seats[i] != ws:
				inc("gereksiz koz harcama (kesip kaybedilen koz)")
		var led := trick[0]
		var role := "i" if seats[0] == dec else "s"
		inc("_açılış_" + role)
		if ws == seats[0]:
			inc("_açılış_kazandı_" + role)
		if seats[0] != dec and ws == dec and trick[w].suit == trump and led.suit != trump:
			inc("rakibe (ihale sahibine) verilen ucuz löve: savunanın açtığı renkte kesme")
		if ws == dec and _was_master_at_play(trick[w], tr, hands, ws):
			inc("ihale sahibinin kesin (renginin en büyüğü) kartla aldığı löve")
		if total - t <= 3:
			inc("son 3 lövede ihale sahibinin aldığı löve", 1.0 if ws == dec else 0.0)
		leader = ws
	inc("ihale sahibinin gerçek lövesi", tr.tricks_won[dec])
	if tr.tricks_won[dec] >= bid:
		inc("_tuttu")
	for s in n:
		if s != dec:
			inc("_savunan")
			if tr.tricks_won[s] == 0:
				inc("_sıfır")


## Kaçan kesin löve: açan oyuncu elinde (gözlemciye göre) kesin kazanacak bir yan
## kart varken başka bir kart açıp löveyi kaybettiyse sonradan sayılır.
func _observe(card: CardData, seat: int, trick: Array[CardData], _seats: Array[int], hands: Array,
		trump: int, _dec: int, tr: CardTracker, legal: Array[CardData], _left: int) -> void:
	if not trick.is_empty():
		return
	var h: Array[CardData] = hands[seat]
	var sure := legal.filter(func(c): return c.suit != trump and _sure_winner(c, seat, hands, trump, tr))
	if not sure.is_empty() and not sure.has(card):
		inc("kaçan kesin löve (kesin kazanan varken başka kart açma)")


## Gözlemci (tam bilgi): bu kart açılırsa kesin kazanır mı? (Daha büyük kart
## kimsede yok ve o renkte boş olup kozu olan rakip yok.)
func _sure_winner(c: CardData, seat: int, hands: Array, trump: int, _tr: CardTracker) -> bool:
	for s in hands.size():
		if s == seat:
			continue
		var hs: Array[CardData] = hands[s]
		var has_suit := false
		for x in hs:
			if x.suit == c.suit:
				has_suit = true
				if x.rank > c.rank:
					return false
		if not has_suit and hs.any(func(x): return x.suit == trump):
			return false
	return true


func _was_master_at_play(c: CardData, tr: CardTracker, _hands: Array, _seat: int) -> bool:
	for r in range(c.rank + 1, 15):
		var h := CardData.create(c.suit, r)
		if not tr.is_played(h):
			return false
	return true
