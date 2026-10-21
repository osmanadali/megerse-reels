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
	test_match_end()
	test_player_stats()
	test_buried_mode_unchanged()
	# Normal İhaleli (4 kişi)
	test_std_deal_13_each()
	test_std_min_bid_5()
	test_std_max_bid_13()
	test_std_rejects_below_5()
	test_std_rejects_above_13()
	test_std_pass_is_final()
	test_std_must_outbid()
	test_std_all_pass_gives_4_to_dealer_right()
	test_std_winner_chooses_trump()
	test_std_starts_with_52_cards()
	test_mode_persists_across_restart()
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
	check(GameRules.buried_bidding().is_valid(), "3 kişi gömmeli kural seti tutarlı")
	check(GameRules.standard_bidding().is_valid(), "4 kişi ihaleli kural seti tutarlı")


func test_three_player_deal() -> void:
	var rules := GameRules.buried_bidding()
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
	var bm := BidManager.new(GameRules.buried_bidding(), 2)  # dağıtan 2 → ilk konuşan 0
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
	var bm := BidManager.new(GameRules.buried_bidding(), 1)
	bm.pass_turn(); bm.pass_turn(); bm.pass_turn()
	check(bm.is_finished() and bm.current_holder == 2 and bm.current_bid == 7, "herkes pas: dağıtanın yanındaki 7 ile alır")
	var top := BidManager.new(GameRules.buried_bidding(), 0)
	top.bid(16)
	check(top.is_finished() and top.current_holder == 1, "16 (en yüksek) ihaleyi hemen bitirir")


func test_scores() -> void:
	var sm := ScoreManager.new(3)
	var made: Array[int] = [8, 5, 3]
	check(sm.apply_round(0, 7, made) == [8, 5, 3], "ihale tuttu: alınan el yazılır")
	var failed: Array[int] = [6, 6, 4]
	check(sm.apply_round(0, 7, failed) == [-7, 6, 4], "ihale battı: -ihale")
	var zero: Array[int] = [9, 7, 0]
	check(sm.apply_round(1, 8, zero) == [9, -8, -8], "sıfır alan ihaleye batar (ihaleyi alan da 7/8 battı)")
	check(sm.totals == [10, 3, -1], "toplam puan")


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


func test_match_end() -> void:
	var m := MatchSettings.new()
	m.rounds = 5
	m.target_score = 51
	var low: Array[int] = [10, 20, 5]
	check(not m.is_match_over(4, low), "4/5 el, hedef yok: devam")
	check(m.is_match_over(5, low), "5/5 el: maç biter")
	var high: Array[int] = [10, 51, 5]
	check(m.is_match_over(2, high), "hedef puana ulaşan maçı bitirir")
	check(MatchSettings.winners(high) == [1], "en yüksek puan kazanır")
	var tie: Array[int] = [30, 30, -7]
	check(MatchSettings.winners(tie) == [0, 1], "eşitlikte berabere")
	check(MatchSettings.ROUND_OPTIONS == [5, 7, 9, 11] and MatchSettings.TARGET_OPTIONS == [51, 71, 91, 101], "seçenekler")


func test_player_stats() -> void:
	var path := "user://test_stats.cfg"
	DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	var st := PlayerStats.load_from(path)
	check(st.matches_played == 0, "boş istatistik")
	st.record_round(true, true)
	st.record_round(true, false)
	st.record_round(false, false)
	st.record_match(true, 42)
	st.save()
	var again := PlayerStats.load_from(path)
	check(again.rounds_played == 3 and again.bids_taken == 2 and again.bids_made == 1, "tur/ihale sayıları")
	check(again.matches_played == 1 and again.matches_won == 1 and again.best_match_score == 42, "maç kaydı kalıcı")
	check(again.summary_lines()[3].contains("%50"), "ihale başarı oranı")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(path))


# --- Gömmeli İhaleli kurallarının korunduğu --------------------------------------

func test_buried_mode_unchanged() -> void:
	var r := GameRules.buried_bidding()
	check(r.mode == GameRules.Mode.BURIED_BIDDING and r.player_count == 3, "gömmeli: 3 oyuncu")
	check(r.cards_per_player == 16 and r.buried_cards == 4, "gömmeli: 16 kart + 4 kapalı")
	check(r.min_bid == 7 and r.max_bid == 16 and r.all_pass_bid == 7, "gömmeli: ihale 7..16, zorunlu 7")
	check(r.phases_after_bid() == [GameRules.PHASE_BURY, GameRules.PHASE_TRUMP, GameRules.PHASE_TAKE_KITTY],
		"gömmeli: göm → koz → yeri al")


# --- Normal İhaleli (4 kişi) -----------------------------------------------------

## Dağıtan 3 → dağıtanın sağındaki (ilk konuşan) 0.
func std_bm(dealer := 3) -> BidManager:
	return BidManager.new(GameRules.standard_bidding(), dealer)


func test_std_deal_13_each() -> void:
	var r := GameRules.standard_bidding()
	var d := DeckManager.new(21)
	d.shuffle()
	var hands := d.deal(r.player_count, r.cards_per_player)
	check(r.player_count == 4 and hands.size() == 4, "normal: 4 oyuncu")
	check(hands.all(func(h): return h.size() == 13), "normal: her oyuncuya 13 kart")
	check(d.take_remaining().is_empty() and r.buried_cards == 0, "normal: ortada kapalı kart yok, gömme yok")


func test_std_min_bid_5() -> void:
	var bm := std_bm()
	check(GameRules.standard_bidding().min_bid == 5, "normal: kuralda en az 5")
	check(bm.valid_bids()[0] == 5, "normal: ilk geçerli teklif 5")
	check(bm.bid(5) and bm.current_bid == 5, "normal: 5 kabul edilir")


func test_std_max_bid_13() -> void:
	var bm := std_bm()
	check(GameRules.standard_bidding().max_bid == 13, "normal: kuralda en çok 13")
	check(bm.valid_bids()[-1] == 13, "normal: son geçerli teklif 13")
	check(bm.bid(13) and bm.is_finished() and bm.current_holder == 0, "normal: 13 en yüksek, ihaleyi bitirir")


func test_std_rejects_below_5() -> void:
	var bm := std_bm()
	for low in [0, 1, 4]:
		check(not bm.bid(low), "normal: %d reddedilir" % low)
	check(bm.current_bid == 0 and bm.current_seat() == 0 and not bm.is_finished(), "normal: red durumu değiştirmez")


func test_std_rejects_above_13() -> void:
	var bm := std_bm()
	check(not bm.bid(14) and not bm.bid(52), "normal: 13'ten büyük reddedilir")
	check(bm.current_bid == 0 and bm.current_seat() == 0, "normal: red durumu değiştirmez")


func test_std_pass_is_final() -> void:
	var bm := std_bm()
	bm.pass_turn()          # 0 pas
	bm.bid(6)               # 1
	bm.bid(7)               # 2
	bm.bid(8)               # 3
	check(bm.has_passed(0) and bm.current_seat() == 1, "normal: pas diyen 0 atlanır, sıra 1'de")
	bm.bid(9)               # 1
	check(bm.current_seat() == 2, "normal: 0 tekrar ihaleye giremez")
	bm.pass_turn(); bm.pass_turn()
	check(bm.is_finished() and bm.current_holder == 1 and bm.current_bid == 9, "normal: ihale 1'de 9")


func test_std_must_outbid() -> void:
	var bm := std_bm()
	bm.bid(7)
	check(not bm.bid(7) and not bm.bid(6), "normal: eşit veya düşük teklif reddedilir")
	check(bm.valid_bids()[0] == 8, "normal: sıradaki en az 8 demeli")
	check(bm.bid(8) and bm.current_holder == 1, "normal: daha yüksek teklif kabul")


func test_std_all_pass_gives_4_to_dealer_right() -> void:
	for dealer in 4:
		var bm := std_bm(dealer)
		for i in 4:
			bm.pass_turn()
		var right := BidManager.dealer_right(dealer, 4)
		check(bm.is_finished() and bm.forced, "normal: herkes pas → yeni tur yok (dağıtan %d)" % dealer)
		check(bm.current_holder == right and bm.current_bid == 4,
			"normal: ihale 4 ile dağıtanın sağındakine (dağıtan %d → %d)" % [dealer, right])
	# İlk konuşan (dağıtanın sağındaki) pas dese de diğer üçü pas deyince ihale yine ona 4 ile kalır.
	var bm2 := std_bm(3)
	bm2.pass_turn(); bm2.pass_turn(); bm2.pass_turn(); bm2.pass_turn()
	check(bm2.current_holder == 0 and bm2.current_bid == 4, "normal: dağıtan 3 → zorunlu ihale 0'da 4")


func test_std_winner_chooses_trump() -> void:
	var r := GameRules.standard_bidding()
	check(r.phases_after_bid() == [GameRules.PHASE_TRUMP], "normal: ihaleden sonra yalnızca koz seçimi")
	var d := DeckManager.new(5)
	d.shuffle()
	var hands := d.deal(4, 13)
	var bm := BidManager.new(r, 3)
	bm.bid(5); bm.pass_turn(); bm.pass_turn(); bm.pass_turn()
	var winner := bm.current_holder
	var trump := AIPlayer.choose_trump(hands[winner])
	check(CardData.Suit.values().has(trump), "normal: ihaleyi alan geçerli bir koz seçer")
	# Seçilen koz kurallarda kullanılır: kazanan oyun açar, koz kırılmadan koz açamaz.
	var legal := BatakRules.legal_cards(hands[winner], [], trump, false)
	var non_trump: Array = hands[winner].filter(func(c): return c.suit != trump)
	check(non_trump.is_empty() or legal.all(func(c): return c.suit != trump), "normal: koz kurala işler")


func test_std_starts_with_52_cards() -> void:
	var r := GameRules.standard_bidding()
	check(r.is_valid(), "normal: kural seti tutarlı")
	check(r.player_count * r.cards_per_player + r.buried_cards == 52, "normal: 4 x 13 = 52")
	var d := DeckManager.new(9)
	check(d.cards_remaining() == 52, "normal: oyun 52 kartla başlar")
	d.shuffle()
	var hands := d.deal(r.player_count, r.cards_per_player)
	var ids := {}
	for h in hands:
		for card in h:
			ids[card.get_id()] = true
	check(ids.size() == 52 and d.cards_remaining() == 0, "normal: 52 kartın hepsi dağıtılır")


## Oyundan çıkıp tekrar girince seçilen mod (ve tur/hedef) aynen yüklenmeli.
func test_mode_persists_across_restart() -> void:
	var path := ProjectSettings.globalize_path(MatchSettings.SAVE_PATH)
	var backup := FileAccess.get_file_as_string(path) if FileAccess.file_exists(path) else ""
	for m in [GameRules.Mode.STANDARD_BIDDING, GameRules.Mode.BURIED_BIDDING]:
		var s := MatchSettings.new()
		s.mode = m
		s.rounds = 9
		s.target_score = 91
		s.save()
		var loaded := MatchSettings.load_saved()
		check(loaded.mode == m and loaded.rounds == 9 and loaded.target_score == 91,
			"kayıtlı mod/tur/hedef yeniden açılışta aynı (%d)" % m)
		check(GameRules.for_mode(loaded.mode).mode == m, "kayıtlı moddan doğru kural seti")
	if backup.is_empty():
		DirAccess.remove_absolute(path)
	else:
		var f := FileAccess.open(path, FileAccess.WRITE)
		f.store_string(backup)
