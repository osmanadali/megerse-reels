extends SceneTree
## Başsız (headless) birim testleri.
## Çalıştırma: godot --headless --path FPSBatak -s res://tests/run_tests.gd

var _failures := 0
var _checks := 0


func _init() -> void:
	test_card_data()
	test_deck_build()
	test_shuffle_is_seeded_and_complete()
	test_deal()
	test_played_tracking()
	test_rules_leading()
	test_rules_follow_and_raise()
	test_rules_trump_obligation()
	test_trick_winner()
	test_ai_uses_only_legal_cards()
	test_rules_presets()
	test_three_player_deal()
	test_bidding_flow()
	test_bidding_all_pass()
	test_scores()
	test_ai_bid_trump_bury()
	print("\n%d kontrol, %d hata" % [_checks, _failures])
	quit(1 if _failures > 0 else 0)


func check(cond: bool, msg: String) -> void:
	_checks += 1
	if not cond:
		_failures += 1
		push_error("FAIL: " + msg)


func test_card_data() -> void:
	var c := CardData.create(CardData.Suit.SPADES, CardData.Rank.ACE)
	check(c.get_id() == "S_A", "id S_A")
	check(c.get_short_label() == "A♠", "kısa etiket")
	check(c.get_display_name() == "Maça As", "Türkçe ad")
	check(c.get_value() == 14, "As değeri 14")
	check(not c.is_red(), "maça siyah")
	var h := CardData.create(CardData.Suit.HEARTS, CardData.Rank.TEN)
	check(h.get_id() == "H_10" and h.is_red(), "kupa 10 kırmızı")
	check(CardData.create(CardData.Suit.CLUBS, CardData.Rank.TWO).get_value() == 2, "2 değeri")


func test_deck_build() -> void:
	var d := DeckManager.new(1)
	check(d.cards_remaining() == 52, "52 kart")
	var ids := {}
	while d.cards_remaining() > 0:
		ids[d.draw_card().get_id()] = true
	check(ids.size() == 52, "52 benzersiz kimlik")
	check(d.draw_card() == null, "boş desteden null")


func _order(d: DeckManager) -> String:
	var parts: PackedStringArray = []
	while d.cards_remaining() > 0:
		parts.append(d.draw_card().get_id())
	return ",".join(parts)


func test_shuffle_is_seeded_and_complete() -> void:
	var a := DeckManager.new(42); a.shuffle()
	var b := DeckManager.new(42); b.shuffle()
	var c := DeckManager.new(7); c.shuffle()
	var plain := DeckManager.new(1)
	var oa := _order(a)
	check(oa == _order(b), "aynı tohum aynı sıra")
	check(oa != _order(c), "farklı tohum farklı sıra")
	check(oa != _order(plain), "karıştırma sırayı değiştirir")
	check(oa.split(",").size() == 52, "karıştırma sonrası 52 kart")


func test_deal() -> void:
	var d := DeckManager.new(3)
	d.shuffle()
	var hands := d.deal()
	check(hands.size() == 4, "4 el")
	var seen := {}
	for hand in hands:
		check(hand.size() == 13, "elde 13 kart")
		for card in hand:
			seen[card.get_id()] = true
		for i in range(1, hand.size()):
			check(not CardData.sort_for_hand(hand[i], hand[i - 1]), "el sıralı")
	check(seen.size() == 52, "dağıtılan 52 kart benzersiz")
	check(d.cards_remaining() == 0, "deste bitti")


func test_played_tracking() -> void:
	var d := DeckManager.new(5)
	var card := d.draw_card()
	check(not d.is_played(card), "oynanmamış")
	d.register_played(card)
	check(d.is_played(card), "oynandı olarak kayıtlı")
	check(d.get_played_cards().size() == 1, "1 oynanan kart")


const S := CardData.Suit
const R := CardData.Rank


## Kısa yazım: c("S_A") -> Maça As.
func c(id: String) -> CardData:
	var parts := id.split("_")
	var suit_map := {"S": S.SPADES, "H": S.HEARTS, "D": S.DIAMONDS, "C": S.CLUBS}
	var rank_map := {"A": R.ACE, "K": R.KING, "Q": R.QUEEN, "J": R.JACK}
	var rank: int = rank_map[parts[1]] if rank_map.has(parts[1]) else int(parts[1])
	return CardData.create(suit_map[parts[0]], rank)


func cards(ids: String) -> Array[CardData]:
	var out: Array[CardData] = []
	for id in ids.split(" ", false):
		out.append(c(id))
	return out


func ids_of(list: Array[CardData]) -> String:
	var parts: PackedStringArray = []
	for card in list:
		parts.append(card.get_id())
	parts.sort()
	return " ".join(parts)


func expect_legal(hand: String, trick: String, broken: bool, expected: String, msg: String) -> void:
	var got := ids_of(BatakRules.legal_cards(cards(hand), cards(trick), S.SPADES, broken))
	var want := ids_of(cards(expected))
	check(got == want, "%s: beklenen [%s], gelen [%s]" % [msg, want, got])


func test_rules_leading() -> void:
	expect_legal("S_A H_2 D_5", "", false, "H_2 D_5", "koz kırılmadan koz açılmaz")
	expect_legal("S_A H_2 D_5", "", true, "S_A H_2 D_5", "koz kırıldıysa serbest")
	expect_legal("S_A S_3", "", false, "S_A S_3", "elde sadece koz varsa koz açılır")


func test_rules_follow_and_raise() -> void:
	expect_legal("H_3 H_Q D_A", "H_10", false, "H_Q", "takıma uy ve yükselt")
	expect_legal("H_3 H_5 D_A", "H_10", false, "H_3 H_5", "yükseltemiyorsa takımdan herhangi")
	expect_legal("H_3 H_Q", "H_10 S_2", true, "H_3 H_Q", "koz girmişse yükseltme gerekmez")


func test_rules_trump_obligation() -> void:
	expect_legal("S_4 S_9 D_A", "H_10", false, "S_4 S_9", "takım yoksa koz zorunlu")
	expect_legal("S_4 S_9 D_A", "H_10 S_7", true, "S_9", "koz varsa büyük koz")
	expect_legal("S_4 S_5 D_A", "H_10 S_7", true, "S_4 S_5", "büyütemiyorsa küçük koz da olur")
	expect_legal("D_2 C_A", "H_10", false, "D_2 C_A", "ne takım ne koz: serbest")


func test_trick_winner() -> void:
	check(BatakRules.trick_winner(cards("H_10 H_A H_2 D_A"), S.SPADES) == 1, "takımın en büyüğü alır")
	check(BatakRules.trick_winner(cards("H_10 H_A S_2 S_3"), S.SPADES) == 3, "en büyük koz alır")
	check(BatakRules.trick_winner(cards("H_10 D_A C_A H_2"), S.SPADES) == 0, "başka takım alamaz")


func test_ai_uses_only_legal_cards() -> void:
	for difficulty in AIPlayer.Difficulty.values():
		var ai := AIPlayer.new(1, difficulty)
		for trial in 20:
			var d := DeckManager.new(trial)
			d.shuffle()
			var hands := d.deal()
			var trick: Array[CardData] = [hands[0][0]]
			var hand: Array[CardData] = hands[1]
			var legal := BatakRules.legal_cards(hand, trick, S.SPADES, false)
			var chosen := ai.choose_card(legal, trick, S.SPADES)
			check(legal.has(chosen), "AI yasal kart oynar")


func test_rules_presets() -> void:
	check(GameRules.three_player_gommeli().is_valid(), "3 kişi gömmeli kural seti tutarlı")
	check(GameRules.four_player_ihaleli().is_valid(), "4 kişi ihaleli kural seti tutarlı")


func test_three_player_deal() -> void:
	var rules := GameRules.three_player_gommeli()
	var d := DeckManager.new(11)
	d.shuffle()
	var hands := d.deal(rules.player_count, rules.cards_per_player)
	var kitty := d.take_remaining()
	check(hands.size() == 3 and hands[2].size() == 16, "3 x 16 kart")
	check(kitty.size() == 4, "yerde 4 kart")
	var ids := {}
	for h in hands:
		for card in h:
			ids[card.get_id()] = true
	for card in kitty:
		ids[card.get_id()] = true
	check(ids.size() == 52, "eller + yer = 52 benzersiz kart")


func test_bidding_flow() -> void:
	var bm := BidManager.new(GameRules.three_player_gommeli(), 2)  # dağıtan 2 → ilk konuşan 0
	check(bm.current_seat() == 0, "ihaleyi dağıtanın sağındaki açar")
	check(bm.valid_bids()[0] == 7 and bm.valid_bids()[-1] == 16, "ihale aralığı 7..16")
	bm.bid(7)
	check(bm.current_seat() == 1 and bm.valid_bids()[0] == 8, "sonraki en az 8 der")
	bm.pass_turn()
	bm.bid(8)
	check(bm.current_seat() == 0, "pas diyen atlanır")
	bm.pass_turn()
	check(bm.is_finished() and bm.current_holder == 2 and bm.current_bid == 8, "ihale 2'de 8")


func test_bidding_all_pass() -> void:
	var bm := BidManager.new(GameRules.three_player_gommeli(), 1)
	bm.pass_turn(); bm.pass_turn(); bm.pass_turn()
	check(bm.is_finished() and bm.current_holder == 2 and bm.current_bid == 7, "herkes pas: dağıtanın yanındaki 7 ile alır")
	var top := BidManager.new(GameRules.three_player_gommeli(), 0)
	top.bid(16)
	check(top.is_finished() and top.current_holder == 1, "16 (en yüksek) ihaleyi hemen bitirir")


func test_scores() -> void:
	var sm := ScoreManager.new(3)
	var made: Array[int] = [8, 5, 3]
	check(sm.apply_round(0, 7, made) == [8, 5, 3], "ihale tuttu: alınan el yazılır")
	var failed: Array[int] = [6, 6, 4]
	check(sm.apply_round(0, 7, failed) == [-7, 6, 4], "ihale battı: -ihale")
	check(sm.totals == [1, 11, 7], "toplam puan")


func test_ai_bid_trump_bury() -> void:
	var strong := cards("S_A S_K S_Q S_J S_10 S_9 S_8 H_A H_K D_A D_K C_A C_K H_2 D_2 C_2")
	var weak := cards("S_2 S_3 S_4 H_2 H_3 H_4 H_5 D_2 D_3 D_4 D_5 C_2 C_3 C_4 C_5 C_6")
	var ai := AIPlayer.new(1, AIPlayer.Difficulty.NORMAL)
	var valid: Array[int] = [7, 8, 9, 10]
	check(ai.choose_bid(strong, valid, 4) == 7, "güçlü el ihaleye girer")
	check(ai.choose_bid(weak, valid, 4) == BidManager.PASS, "zayıf el pas der")
	check(AIPlayer.choose_trump(strong) == S.SPADES, "uzun ve güçlü takım koz")
	var buried := AIPlayer.choose_bury(strong, 4, AIPlayer.choose_trump(strong))
	check(buried.size() == 4, "4 kart gömülür")
	check(not buried.any(func(c: CardData): return c.suit == S.SPADES or c.rank == R.ACE), "koz ve As gömülmez")
