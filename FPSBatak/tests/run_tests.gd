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
