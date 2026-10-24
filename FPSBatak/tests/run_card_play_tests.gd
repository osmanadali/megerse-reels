extends SceneTree
## Kart oynama AI'sı testleri (CardTracker, PlayContext, PlayPolicy).
## Çalıştırma: godot --headless --path FPSBatak -s res://tests/run_card_play_tests.gd
##
## Kurallar sert kısıttır: her testte AI'nın seçtiği kartın
## BatakRules.legal_cards() listesinde olduğu da ayrıca kontrol edilir.

const S := CardData.Suit

var _failures := 0
var _checks := 0


func _init() -> void:
	test_tracker_records_plays()
	test_tracker_void_detection()
	test_tracker_suit_cap()
	test_tracker_remaining_cards()
	test_context_roles_and_hidden_info()
	test_rule_follow_suit()
	test_rule_mandatory_raise()
	test_rule_trump_obligation()
	test_rule_trump_raise()
	test_rule_no_trump_lead_before_broken()
	test_scenarios_a_to_j()
	test_endgame_decisions()
	test_decision_uses_only_public_info()
	test_old_api_unchanged()
	test_random_full_games_legal_and_complete()
	print("\n%d kontrol, %d hata" % [_checks, _failures])
	quit(1 if _failures > 0 else 0)


func check(cond: bool, msg: String) -> void:
	_checks += 1
	if not cond:
		_failures += 1
		push_error("FAIL: " + msg)


# --- Yardımcılar -------------------------------------------------------------------

func c(id: String) -> CardData:
	var parts := id.split("_")
	var suit_map := {"S": S.SPADES, "H": S.HEARTS, "D": S.DIAMONDS, "C": S.CLUBS}
	var rank_map := {"A": 14, "K": 13, "Q": 12, "J": 11}
	var rank: int = rank_map[parts[1]] if rank_map.has(parts[1]) else int(parts[1])
	return CardData.create(suit_map[parts[0]], rank)


func cards(ids: String) -> Array[CardData]:
	var out: Array[CardData] = []
	for id in ids.split(" ", false):
		out.append(c(id))
	return out


## Bir senaryo: `history` önceki löveler ("koltuk:kart" dizileri, her biri bir löve),
## `current` mevcut lövede oynananlar. Tracker bunları açık bilgi olarak kaydeder.
class Scene:
	var rules: GameRules
	var tracker: CardTracker
	var trick: Array[CardData] = []
	var trick_seats: Array[int] = []


func scene(rules: GameRules, trump: int, bidder: int, bid: int, history: Array, current: String,
		hidden_buried := 0) -> Scene:
	var sc := Scene.new()
	sc.rules = rules
	sc.tracker = CardTracker.new(rules.player_count, trump, bidder, bid, rules.cards_per_player, hidden_buried)
	for t in history:
		var played: Array[CardData] = []
		var seats: Array[int] = []
		for e in t.split(" ", false):
			var p: PackedStringArray = e.split(":")
			sc.tracker.record_play(int(p[0]), c(p[1]))
			played.append(c(p[1]))
			seats.append(int(p[0]))
		sc.tracker.record_trick_end(seats[BatakRules.trick_winner(played, trump)])
	for e in current.split(" ", false):
		var p: PackedStringArray = e.split(":")
		sc.tracker.record_play(int(p[0]), c(p[1]))
		sc.trick.append(c(p[1]))
		sc.trick_seats.append(int(p[0]))
	return sc


func pick(sc: Scene, seat: int, hand_ids: String, difficulty := AIPlayer.Difficulty.NORMAL,
		buried: Array[CardData] = []) -> CardData:
	var hand := cards(hand_ids)
	var legal := BatakRules.legal_cards(hand, sc.trick, sc.tracker.trump, sc.tracker.trump_broken)
	var ctx := PlayContext.build(sc.rules, seat, hand, legal, sc.trick, sc.trick_seats, sc.tracker, buried)
	var chosen := AIPlayer.new(seat, difficulty).choose_card_in_context(ctx)
	check(legal.has(chosen), "seçilen kart yasal olmalı (%s)" % chosen.get_id())
	return chosen


func std() -> GameRules:
	return GameRules.standard_bidding()


func bur() -> GameRules:
	return GameRules.buried_bidding()


# --- CardTracker -------------------------------------------------------------------

func test_tracker_records_plays() -> void:
	var sc := scene(std(), S.SPADES, 0, 6, ["0:H_10 1:H_A 2:H_2 3:H_3"], "1:D_5 2:D_9")
	var tr := sc.tracker
	check(tr.is_played(c("H_A")) and tr.played["H_A"].trick == 0 and tr.played["H_A"].seat == 1,
		"oynanan kart, oynayan ve löve numarası tutulur")
	check(tr.played["D_9"].trick == 1, "mevcut lövenin kartı 1. lövede")
	check(tr.trick_winners == ([1] as Array[int]) and tr.tricks_won[1] == 1, "löveyi kim aldı")
	check(tr.leader == 1, "löveyi alan açar")
	check(tr.remaining_tricks() == 12, "kalan löve")
	check(tr.hand_size(1) == 11 and tr.hand_size(3) == 12, "oyuncu başına kalan kart")
	check(tr.tricks_needed() == 6, "ihale sahibinin gereken lövesi")
	check(not tr.trump_broken, "koz oynanmadıkça kırılmaz")
	check(tr.history.size() == 6, "oynanma geçmişi sırayla")
	check(tr.current_trick_seats() == ([1, 2] as Array[int]), "mevcut lövede oynayanlar")
	var sc2 := scene(std(), S.SPADES, 0, 6, ["0:H_10 1:H_A 2:S_2 3:H_3"], "")
	check(sc2.tracker.trump_broken and sc2.tracker.tricks_won[2] == 1 and sc2.tracker.tricks_needed() == 6,
		"koz kırıldı ve kesen aldı")


func test_tracker_void_detection() -> void:
	var tr := scene(std(), S.SPADES, 0, 6, ["0:H_10 1:S_2 2:D_4 3:H_3"], "").tracker
	check(tr.voids[1][S.HEARTS], "renge uymayan o renkte boş")
	check(not tr.voids[1][S.SPADES], "koz atan kozda boş sayılmaz")
	check(tr.voids[2][S.HEARTS] and tr.voids[2][S.SPADES], "uymayan ve koz atmayan kozda da boş")
	check(not tr.voids[3][S.HEARTS] and not tr.voids[0][S.HEARTS], "uyanlar boş sayılmaz")
	check(not tr.could_hold(2, c("H_K")) and not tr.could_hold(2, c("S_A")), "boş oyuncu o kartı tutamaz")


func test_tracker_suit_cap() -> void:
	# Mecburi yükseltme: H_J üstüne H_5 veren oyuncuda J'den büyük ♥ yok.
	var tr := scene(std(), S.SPADES, 0, 6, ["0:H_J 1:H_5 2:H_A 3:H_2"], "").tracker
	check(tr.suit_cap[1][S.HEARTS] == 11, "yükseltmeyen oyuncunun üst sınırı")
	check(not tr.could_hold(1, c("H_Q")) and tr.could_hold(1, c("H_9")), "üst sınır olasılıkları sınırlar")
	check(tr.suit_cap[3][S.HEARTS] == 14, "As'ın altında kalan: As'tan büyük yok (sınır yok)")
	# Masa kozlanınca renkte yükseltme zorunlu değil: çıkarım yapılmaz.
	var tr2 := scene(std(), S.SPADES, 0, 6, ["0:H_J 1:S_3 2:H_4 3:H_2"], "").tracker
	check(tr2.suit_cap[2][S.HEARTS] == 15, "kozlanmış lövede küçük kart sınır koymaz")
	# Kozda yükseltme: S_9 üstüne S_4 atan boş oyuncuda 9'dan büyük koz yok.
	var tr3 := scene(std(), S.SPADES, 0, 6, ["0:H_J 1:S_9 2:S_4 3:H_2"], "").tracker
	check(tr3.voids[2][S.HEARTS] and tr3.suit_cap[2][S.SPADES] == 9, "kozda yükseltemeyenin koz sınırı")


func test_tracker_remaining_cards() -> void:
	var tr := scene(std(), S.SPADES, 0, 6, ["0:H_A 1:H_2 2:H_3 3:H_4"], "").tracker
	check(tr.highest_unplayed(S.HEARTS) == 13, "♥A çıktı, en büyük ♥K")
	check(tr.is_master(c("H_K"), cards("H_K D_2")), "♥K artık en büyük")
	check(not tr.is_master(c("H_Q"), cards("H_Q")), "♥K dışarıdayken ♥Q en büyük değil")
	check(tr.is_master(c("H_Q"), cards("H_Q H_K")), "♥K kendi elindeyse ♥Q de kesin")
	var unseen := tr.unseen(cards("H_K D_2"))
	check(unseen.size() == 52 - 4 - 2, "görünmeyen = deste − oynanan − kendi el")
	check(not unseen.any(func(x): return x.get_id() == "H_A" or x.get_id() == "H_K"), "oynanan ve eldeki görünmez değil")
	check(tr.unseen_trumps(cards("S_A S_K")) == 11, "rakiplerde olabilecek koz sayısı")
	# Gömmelide ihale sahibi gömdüğünü bilir, savunan bilmez.
	var bt := scene(bur(), S.SPADES, 0, 8, [], "", 4).tracker
	check(bt.unseen(cards("S_A"), cards("C_2 C_3 C_4 C_5")).size() == 52 - 1 - 4, "ihale sahibi gömdüklerini görür")
	check(bt.unseen(cards("S_A")).size() == 51, "savunan gömülenleri görmez")


func test_context_roles_and_hidden_info() -> void:
	var sc := scene(bur(), S.SPADES, 0, 8, [], "", 4)
	var buried := cards("C_2 C_3 C_4 C_5")
	var hand := cards("S_A H_2")
	var legal := BatakRules.legal_cards(hand, sc.trick, S.SPADES, false)
	var bctx := PlayContext.build(sc.rules, 0, hand, legal, sc.trick, sc.trick_seats, sc.tracker, buried)
	var dctx := PlayContext.build(sc.rules, 1, hand, legal, sc.trick, sc.trick_seats, sc.tracker, buried)
	check(bctx.is_bidder() and not dctx.is_bidder(), "rol: ihale sahibi / savunan")
	check(bctx.own_buried.size() == 4 and bctx.unknown_buried() == 0, "ihale sahibi gömdüklerini bilir")
	check(dctx.own_buried.is_empty() and dctx.unknown_buried() == 4, "savunana gömülen kartlar verilmez")
	check(bctx.mode() == GameRules.Mode.BURIED_BIDDING, "mod bağlamdan okunur")
	check(bctx.tricks_needed() == 8 and bctx.remaining_tricks() == 16, "hedef ve kalan löve")
	check(dctx.opponents().size() == 2 and dctx.player_count() == 3, "3 oyunculu gömmeli")
	var s4 := scene(std(), S.SPADES, 2, 7, [], "2:H_5")
	var ctx4 := PlayContext.build(s4.rules, 3, cards("H_9"), cards("H_9"), s4.trick, s4.trick_seats, s4.tracker)
	check(ctx4.players_after() == ([0, 1] as Array[int]) and ctx4.unknown_buried() == 0 and ctx4.mode() == GameRules.Mode.STANDARD_BIDDING, "normal modda arkadakiler, gömülü yok")


# --- Kurallar (sert kısıt) ---------------------------------------------------------

func test_rule_follow_suit() -> void:
	for d in AIPlayer.Difficulty.values():
		var p := pick(scene(std(), S.SPADES, 0, 6, [], "0:H_10"), 1, "H_2 S_A D_A C_A", d)
		check(p.get_id() == "H_2", "renge uyma zorunlu (zorluk %d)" % d)


func test_rule_mandatory_raise() -> void:
	for d in AIPlayer.Difficulty.values():
		var p := pick(scene(std(), S.SPADES, 0, 6, [], "0:H_10"), 1, "H_J H_Q H_A H_4 S_9 D_7", d)
		check(p.suit == S.HEARTS and p.rank > 10, "mecburi yükseltme (zorluk %d)" % d)


func test_rule_trump_obligation() -> void:
	for d in AIPlayer.Difficulty.values():
		var p := pick(scene(std(), S.SPADES, 0, 6, [], "0:H_10"), 1, "S_3 S_9 D_7 C_5", d)
		check(p.suit == S.SPADES, "renk yoksa koz zorunlu (zorluk %d)" % d)


func test_rule_trump_raise() -> void:
	for d in AIPlayer.Difficulty.values():
		var p := pick(scene(std(), S.SPADES, 0, 6, [], "0:H_10 1:S_7"), 2, "S_3 S_9 S_K D_7", d)
		check(p.get_id() == "S_9" or p.get_id() == "S_K", "kozda yükseltme zorunlu (zorluk %d)" % d)


func test_rule_no_trump_lead_before_broken() -> void:
	for d in AIPlayer.Difficulty.values():
		var p := pick(scene(std(), S.SPADES, 0, 6, [], ""), 0, "S_A S_K S_Q H_2", d)
		check(p.get_id() == "H_2", "koz kırılmadan koz açılmaz (zorluk %d)" % d)


# --- Senaryolar (analiz raporundaki A–J) -------------------------------------------

func test_scenarios_a_to_j() -> void:
	# A) Savunan 2. sırada, mecburi yükseltme: en küçük kazananla girer (ihale sahibi arkada).
	var a := pick(scene(std(), S.SPADES, 3, 6, [], "0:H_10"), 1, "H_J H_Q H_A H_4 S_9 D_7")
	check(a.get_id() == "H_J", "A) savunan en küçük kazananla yükseltir (gelen %s)" % a.get_id())

	# B) 3. sırada ♥K dışarıda, ♥A ile ♥Q var: As harcanmaz.
	var b := pick(scene(std(), S.SPADES, 3, 6, [], "0:H_10 1:H_J"), 2, "H_A H_Q H_3 S_9 C_4")
	check(b.get_id() == "H_Q", "B) As saklanır, Q ile yükseltilir (gelen %s)" % b.get_id())

	# B2) Son sırada ihale sahibi: Q yeterli, As boşa harcanmaz.
	var b2 := pick(scene(std(), S.SPADES, 3, 6, [], "0:H_10 1:H_J 2:H_2"), 3, "H_A H_Q H_3 S_9 C_4")
	check(b2.get_id() == "H_Q", "B2) son sırada yeterli en küçük kazanan (gelen %s)" % b2.get_id())

	# C) Kazanamıyor: en küçük kartı verir.
	var cc := pick(scene(std(), S.SPADES, 0, 6, [], "0:H_J"), 1, "H_2 H_5 H_9 S_9 D_7")
	check(cc.get_id() == "H_2", "C) kazanamayınca en küçük (gelen %s)" % cc.get_id())

	# D2) Son sırada üstüne koz: en küçük yeterli koz.
	var d2 := pick(scene(std(), S.SPADES, 0, 6, [], "1:H_10 2:S_7 3:H_2"), 0, "S_3 S_9 S_K D_7 C_5")
	check(d2.get_id() == "S_9", "D2) son sırada en küçük yeterli koz (gelen %s)" % d2.get_id())

	# E2) Renk de koz da yok: korumalı büyük kartlar atılmaz.
	var e2 := pick(scene(std(), S.SPADES, 0, 6, [], "0:H_10"), 1, "D_K D_2 C_Q C_J C_3")
	check(e2.rank < 11, "E2) atışta büyük kart korunur (gelen %s)" % e2.get_id())

	# G) İhale sahibi açıyor; ♥A çıktı, ♥K artık kesin: kesin löveyi alır.
	var g := pick(scene(std(), S.SPADES, 0, 6, ["1:H_A 2:H_2 3:H_3 0:H_4", "1:C_2 2:C_A 3:C_3 0:C_4"], "", 0),
		0, "H_K H_6 D_9 D_4 C_8")
	check(g.get_id() == "H_K", "G) ♥A çıkınca kesinleşen ♥K açılır (gelen %s)" % g.get_id())

	# H) Savunan açıyor; ihale sahibi ♣'da kesin boş ve kozlu: ♣ açıp kozunu eritir.
	var h := pick(scene(std(), S.SPADES, 0, 6, ["1:C_2 2:C_4 3:C_5 0:S_2"], ""), 1, "C_K C_9 C_3 D_Q D_5 H_8")
	check(h.suit == S.CLUBS, "H) savunan ihale sahibini kozla kesmeye zorlar (gelen %s)" % h.get_id())

	# I) Son 2 löve: ♥A çıktı, ♥K en büyük → ihale sahibi ♥K açar.
	var i := pick(scene(std(), S.SPADES, 0, 6, ["1:H_A 2:H_2 3:H_3 0:H_4"], ""), 0, "H_K D_4")
	check(i.get_id() == "H_K", "I) oyun sonunda kesin kart açılır (gelen %s)" % i.get_id())

	# J) İlk açılış: koz kırılmadı → koz açılmaz.
	var j := pick(scene(std(), S.HEARTS, 0, 6, [], ""), 0, "S_K S_4 H_A H_K H_9 H_6 D_A D_10 C_8 C_2")
	check(j.suit != S.HEARTS, "J) koz kırılmadan koz açılmaz (gelen %s)" % j.get_id())


func test_endgame_decisions() -> void:
	# Tek yasal kart → o oynanır (zorluk fark etmez).
	for d in AIPlayer.Difficulty.values():
		var only := pick(scene(std(), S.SPADES, 0, 6, [], "0:H_10"), 1, "H_2 D_9", d)
		check(only.get_id() == "H_2", "tek yasal kart (zorluk %d)" % d)
	# Son löve, son sırada kazanan varsa alır (savunan sıfır löveden kaçar).
	var last := pick(scene(std(), S.SPADES, 0, 6, [], "1:D_9 2:D_2 3:D_3"), 0, "D_10")
	check(last.get_id() == "D_10", "son löve")
	# İhale sahibi son sırada: kazanabiliyorsa kazanır.
	var bl := pick(scene(std(), S.SPADES, 0, 6, [], "1:D_9 2:D_2 3:D_3"), 0, "D_10 D_4 H_7")
	check(bl.get_id() == "D_10", "ihale sahibi son sırada löveyi alır (gelen %s)" % bl.get_id())
	# Savunan son sırada ihale sahibinin kartını geçebiliyorsa geçer.
	var dl := pick(scene(std(), S.SPADES, 2, 6, [], "3:D_5 0:D_7 2:D_J"), 1, "D_Q D_2 H_7")
	check(dl.get_id() == "D_Q", "savunan ihale sahibinin lövesini keser (gelen %s)" % dl.get_id())
	# Savunan, kendisinden sonra oynayacak ihale sahibi yokken başka savunan kazanıyorsa büyüğünü harcamaz.
	var df := pick(scene(std(), S.SPADES, 0, 6, [], "0:D_5 1:D_K 2:D_2"), 3, "D_A D_3 H_7")
	check(df.get_id() == "D_A", "mecburi yükseltme son sırada da geçerli (gelen %s)" % df.get_id())


## AI yalnızca açık bilgiyi kullanır: rakip elleri ne olursa olsun aynı açık
## durumda aynı kararı verir (bağlamda başka oyuncunun eli yoktur).
func test_decision_uses_only_public_info() -> void:
	var props := PlayContext.new().get_property_list().map(func(p): return p.name)
	check(not props.has("hands") and not props.has("all_hands"), "bağlamda rakip elleri yok")
	var p1 := pick(scene(std(), S.SPADES, 0, 6, ["1:C_2 2:C_4 3:C_5 0:C_9"], ""), 1, "C_K C_3 D_Q D_5 H_8")
	var p2 := pick(scene(std(), S.SPADES, 0, 6, ["1:C_2 2:C_4 3:C_5 0:C_9"], ""), 1, "C_K C_3 D_Q D_5 H_8")
	check(p1.get_id() == p2.get_id(), "aynı açık durum → aynı karar (deterministik)")


func test_old_api_unchanged() -> void:
	var ai := AIPlayer.new(1)
	var legal := cards("H_2 H_A D_3")
	var empty: Array[CardData] = []
	check(ai.choose_card(legal, empty, S.SPADES).get_id() == "H_A", "eski API: As açar")
	var trick := cards("H_10")
	check(ai.choose_card(cards("H_J H_A"), trick, S.SPADES).get_id() == "H_J", "eski API: en küçük kazanan")


## Rastgele tam eller: her zorlukta, iki modda, AI hiç yasal olmayan kart
## seçmez ve el her zaman bitene kadar oynanır (akış kilitlenmez).
func test_random_full_games_legal_and_complete() -> void:
	var illegal := 0
	var incomplete := 0
	var games := 0
	for mode_rules in [std(), bur()]:
		var rules: GameRules = mode_rules
		var n := rules.player_count
		for g in 60:
			var deck := DeckManager.new(1000 + g)
			deck.shuffle()
			var hands := deck.deal(n, rules.cards_per_player)
			var kitty := deck.take_remaining()
			var bidder := g % n
			var trump := AIPlayer.choose_trump(hands[bidder], rules)
			var buried: Array[CardData] = []
			if rules.buried_cards > 0:
				var h0: Array[CardData] = hands[bidder]
				buried = AIPlayer.choose_bury(h0, rules.buried_cards, trump)
				for x in buried:
					h0.erase(x)
				h0.append_array(kitty)
			var ais: Array = []
			for s in n:
				ais.append(AIPlayer.new(s, (g + s) % AIPlayer.Difficulty.size()))
			var tr := CardTracker.new(n, trump, bidder, rules.min_bid, rules.cards_per_player, buried.size())
			var leader := bidder
			for t in rules.cards_per_player:
				var trick: Array[CardData] = []
				var seats: Array[int] = []
				var seat := leader
				for k in n:
					var hand: Array[CardData] = hands[seat]
					var legal := BatakRules.legal_cards(hand, trick, trump, tr.trump_broken)
					var ctx := PlayContext.build(rules, seat, hand, legal, trick, seats, tr,
						buried if seat == bidder else ([] as Array[CardData]))
					var card: CardData = ais[seat].choose_card_in_context(ctx)
					if not legal.has(card):
						illegal += 1
					hand.erase(card)
					tr.record_play(seat, card)
					trick.append(card)
					seats.append(seat)
					seat = (seat + 1) % n
				var w := seats[BatakRules.trick_winner(trick, trump)]
				tr.record_trick_end(w)
				leader = w
			if tr.trick_index != rules.cards_per_player or hands.any(func(h): return not h.is_empty()):
				incomplete += 1
			games += 1
	check(illegal == 0, "rastgele %d elde yasal olmayan seçim: %d" % [games, illegal])
	check(incomplete == 0, "rastgele %d elde yarım kalan el: %d" % [games, incomplete])
