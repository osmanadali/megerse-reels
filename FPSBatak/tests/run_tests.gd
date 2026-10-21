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
