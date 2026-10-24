extends Node
## Geliştirme aracı: gerçek oyun sahnesini otomatik oynatırken her turu denetler.
##
## Kullanım (başsız, hızlandırılmış):
##   godot --headless --path FPSBatak -- --autoplay \
##       --validate=standard:tur:5,buried:hedef:51 [--expect-saved-mode=buried]
## Her girdi "mod:tur:N" (N tur oyna) veya "mod:hedef:N" (N puana ulaşan kazanır);
## maçlar sırayla oynanır (aralarında mod değişir).
## Son maçtan sonra rapor yazar ve hata sayısını çıkış koduyla bildirir.
## Normal oyunda bu düğüm hiç oluşturulmaz.

const TIME_SCALE := 25.0

var c: TableController
var _plan: Array = []          # [{mode, rounds, target}]
var _match_index := 0
var _failures := 0
var _checks := 0
var _log: PackedStringArray = []

# Tur içi izleme
var _expected_dealer := -1
var _prev_totals: Array[int] = []
var _round_winners: Array[int] = []
var _last_winner := -1
var _forced_count := 0
var _rounds_checked := 0
var _tricks_checked := 0
var _match_over_seen := false


func setup(controller: TableController, plan_arg: String) -> void:
	c = controller
	for entry in plan_arg.split(","):
		var p := entry.split(":")
		var by_rounds := p[1] == "tur"
		_plan.append({
			"mode": GameRules.Mode.STANDARD_BIDDING if p[0] == "standard" else GameRules.Mode.BURIED_BIDDING,
			"end": MatchSettings.EndCondition.ROUNDS if by_rounds else MatchSettings.EndCondition.TARGET,
			"rounds": int(p[2]) if by_rounds else 7,
			"target": 71 if by_rounds else int(p[2]),
		})
	Engine.time_scale = TIME_SCALE
	_check_saved_mode_on_start()
	_save_plan_entry(0)
	c.round_dealt.connect(_on_round_dealt)
	c.bidding_finished.connect(_on_bidding_finished)
	c.trick_finished.connect(_on_trick_finished)
	c.round_finished.connect(_on_round_finished)
	c.match_finished.connect(_on_match_finished)
	_watchdog()


## İlerleme durursa (gerçek zamanda 20 sn hiç löve/tur olayı yoksa) oyunun
## hangi aşamada beklediğini yazdırır.
var _events := 0
func _watchdog() -> void:
	var last := -1
	while true:
		await get_tree().create_timer(20.0, true, false, true).timeout
		if _events == last:
			var tw := c._table_cards.get_children().filter(func(x): return not x.is_queued_for_deletion())
			var views: PackedStringArray = []
			for seat in c._opponent_hands:
				views.append("%d:%d" % [seat, c._opponent_hands[seat].count()])
			push_error("TAKILMA: tur %d, ihale %d/%d, koz %d, löveler %s, eller %s, oyuncu eli %d, rakip elleri %s, masada %d düğüm" % [
				c.rounds_played + 1, c.bidder, c.bid, c.trump, c.tricks_won,
				c.hands.map(func(h): return h.size()), c.hud.hand._cards.size(), ", ".join(views), tw.size()])
		last = _events


func check(cond: bool, msg: String) -> void:
	_checks += 1
	if not cond:
		_failures += 1
		push_error("DOĞRULAMA HATASI: " + msg)


## "Oyundan çıkıp tekrar girince" seçilen mod doğru yükleniyor mu?
func _check_saved_mode_on_start() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--expect-saved-mode="):
			var want := GameRules.Mode.STANDARD_BIDDING if arg.ends_with("standard") \
				else GameRules.Mode.BURIED_BIDDING
			check(MatchSettings.load_saved().mode == want, "kayıtlı mod okunamadı")
			check(c.rules.mode == want, "açılışta masa kayıtlı moda göre kurulmadı")
			check(c._n == c.rules.player_count and c._seat_names.size() == c._n,
				"açılışta koltuk sayısı moda uymuyor")
			_log.append("Açılış: kayıtlı mod (%s) doğru yüklendi" % c.rules.display_name)


## Sıradaki maçın ayarlarını kaydeder; autoplay yeni maçta bunları okur.
func _save_plan_entry(i: int) -> void:
	var s := MatchSettings.new()
	s.mode = _plan[i].mode
	s.end_condition = _plan[i].end
	s.rounds = _plan[i].rounds
	s.target_score = _plan[i].target
	s.save()  # tur/hedef, ayar ekranındaki seçeneklerden biri olmalı (5/7/9/11, 51/71/91/101)


func _plan_entry() -> Dictionary:
	return _plan[_match_index]


# --- Tur başı ---------------------------------------------------------------------

func _on_round_dealt() -> void:
	_events += 1
	print("[doğrulama] dağıtıldı")
	var r := c.rules
	var n := c._n
	var e := _plan_entry()
	var tag := "[%s maç %d tur %d]" % [r.display_name, _match_index + 1, c.rounds_played + 1]

	# Mod / maç ayarları
	check(r.mode == e.mode, tag + " yanlış mod")
	check(n == r.player_count and c._seat_names.size() == n, tag + " oyuncu sayısı moda uymuyor")
	check(c._opponent_hands.size() == n - 1 and c._ai.size() == n - 1, tag + " rakip sayısı yanlış")
	check(c.scores.totals.size() == n, tag + " skor dizisi oyuncu sayısına uymuyor")

	# Dağıtıcı sırası
	if c.rounds_played == 0:
		check(not _match_over_seen, tag + " önceki maç bitmeden yeni maç başladı")
		_expected_dealer = n - 1
		var zeros: Array[int] = []
		zeros.resize(n)
		zeros.fill(0)
		check(c.scores.totals == zeros, tag + " yeni maçta skorlar sıfırlanmadı (eski mod/maç taşındı)")
		_prev_totals = zeros
	else:
		_expected_dealer = Seat.next(_expected_dealer, n)
		check(c.scores.totals == _prev_totals, tag + " turlar arasında skor değişti/sıfırlandı")
	check(c.dealer == _expected_dealer, tag + " dağıtıcı %d, beklenen %d" % [c.dealer, _expected_dealer])

	# Deste: tam ve tekrarsız dağıtım
	check(c.hands.size() == n, tag + " el sayısı yanlış")
	var ids := {}
	var total := 0
	for h in c.hands:
		check(h.size() == r.cards_per_player, tag + " elde %d kart (beklenen %d)" % [h.size(), r.cards_per_player])
		for card in h:
			ids[card.get_id()] = true
			total += 1
	check(c.kitty.size() == r.buried_cards, tag + " yerde %d kart (beklenen %d)" % [c.kitty.size(), r.buried_cards])
	for card in c.kitty:
		ids[card.get_id()] = true
		total += 1
	check(total == 52 and ids.size() == 52, tag + " deste eksik/tekrarlı: %d kart, %d benzersiz" % [total, ids.size()])
	check(c.deck.cards_remaining() == 0 and c.deck.get_played_cards().is_empty(), tag + " destede artık kart var")

	# Önceki turdan kalıntı yok
	check(c.trump == TableController.NO_SEAT and not c.trump_broken, tag + " koz durumu önceki turdan kaldı")
	check(c.bidder == TableController.NO_SEAT and c.bid == 0, tag + " ihale durumu önceki turdan kaldı")
	check(c.tricks_won.all(func(t): return t == 0), tag + " alınan el sayıları sıfırlanmadı")
	check(c._pile_counts.all(func(t): return t == 0), tag + " löve yığınları sıfırlanmadı")
	check(c.hud.hand._cards.size() == r.cards_per_player, tag + " oyuncunun elinde eski kart kaldı")
	for seat in c._opponent_hands:
		check(c._opponent_hands[seat].count() == r.cards_per_player, tag + " rakip elinde eski kart kaldı")
	var live := c._table_cards.get_children().filter(func(x): return x is Card3D and not x.is_queued_for_deletion())
	check(live.size() == r.buried_cards, tag + " masada eski turdan %d kart kaldı" % (live.size() - r.buried_cards))

	_round_winners.clear()
	_last_winner = -1


# --- İhale ------------------------------------------------------------------------

func _on_bidding_finished(bm: BidManager) -> void:
	_events += 1
	var r := c.rules
	var right := BidManager.dealer_right(c.dealer, c._n)
	check(c.bidder >= 0 and c.bidder < c._n, "ihaleyi alan geçersiz")
	if bm.forced:
		_forced_count += 1
		check(c.bid == r.all_pass_bid and c.bidder == right,
			"herkes pas: ihale %d/%d olmalıydı, %d/%d" % [r.all_pass_bid, right, c.bid, c.bidder])
		check(bm.last_call.all(func(x): return x == BidManager.PASS), "zorunlu ihalede pas demeyen var")
	else:
		check(c.bid >= r.min_bid and c.bid <= r.max_bid, "ihale aralık dışı: %d" % c.bid)
		check(bm.last_call[c.bidder] == c.bid, "ihaleyi alanın son sözü ihale değil")
		for seat in c._n:
			if seat != c.bidder:
				check(bm.last_call[seat] == BidManager.PASS or bm.last_call[seat] < c.bid,
					"daha yüksek teklif veren biri ihaleyi alamadı")


# --- Löve -------------------------------------------------------------------------

func _on_trick_finished(trick: Array[CardData], seats: Array[int], winner_seat: int) -> void:
	_events += 1
	_tricks_checked += 1
	var n := c._n
	check(c.trump >= 0, "koz seçilmeden löve oynandı")
	check(trick.size() == n and seats.size() == n, "lövede %d kart" % trick.size())
	var leader := c.bidder if _round_winners.is_empty() else _last_winner
	check(seats[0] == leader, "löveyi açan %d, beklenen %d (ilk lövede ihaleyi alan)" % [seats[0], leader])
	for i in n:
		check(seats[i] == (leader + i) % n, "oynama sırası yanlış")
	var ids := {}
	for card in trick:
		ids[card.get_id()] = true
	check(ids.size() == n, "aynı kart lövede iki kez")
	check(winner_seat == seats[BatakRules.trick_winner(trick, c.trump)], "löve yanlış oyuncuya yazıldı")
	if c.rules.buried_cards > 0 and _round_winners.is_empty():
		var buried := c.deck.get_played_cards().size() - n
		check(buried == c.rules.buried_cards, "gömülen kart sayısı %d" % buried)
	_round_winners.append(winner_seat)
	_last_winner = winner_seat


# --- Tur sonu ---------------------------------------------------------------------

func _on_round_finished(deltas: Array[int]) -> void:
	_rounds_checked += 1
	var r := c.rules
	var n := c._n
	var tag := "[%s maç %d tur %d sonu]" % [r.display_name, _match_index + 1, c.rounds_played]
	check(_round_winners.size() == r.cards_per_player, tag + " löve sayısı %d" % _round_winners.size())
	var sum := 0
	for seat in n:
		check(c.tricks_won[seat] == _round_winners.count(seat), tag + " el sayısı yanlış oyuncuya yazıldı")
		sum += c.tricks_won[seat]
	check(sum == r.cards_per_player, tag + " toplam el %d" % sum)
	check(c.hands.all(func(h): return h.is_empty()), tag + " elde kart kaldı")
	check(c.hud.hand._cards.is_empty(), tag + " oyuncunun elinde görsel kart kaldı")
	var played := c.deck.get_played_cards()
	var ids := {}
	for card in played:
		ids[card.get_id()] = true
	check(played.size() == 52 and ids.size() == 52, tag + " oynanan+gömülen kartlar 52 değil (%d)" % ids.size())
	var pile_sum := 0
	for p in c._pile_counts:
		pile_sum += p
	check(pile_sum == n * r.cards_per_player, tag + " yığınlarda %d kart" % pile_sum)
	var expected := ScoreManager.round_scores(c.bidder, c.bid, c.tricks_won)
	check(deltas == expected, tag + " tur puanı %s, beklenen %s" % [deltas, expected])
	for seat in n:
		check(c.scores.totals[seat] == _prev_totals[seat] + deltas[seat], tag + " toplam puan yanlış oyuncuya yazıldı")
	_prev_totals = c.scores.totals.duplicate()
	print("[doğrulama] %s tur bitti" % tag)
	var over := c.settings.is_match_over(c.rounds_played, c.scores.totals)
	_match_over_seen = over
	_log.append("%s ihale %s %d%s, el %s, puan %s, toplam %s%s" % [tag, c._seat_names[c.bidder], c.bid,
		" (zorunlu)" if c.bid == r.all_pass_bid and r.all_pass_bid < r.min_bid else "",
		c.tricks_won, deltas, c.scores.totals, "  → MAÇ BİTTİ" if over else ""])


# --- Maç sonu ---------------------------------------------------------------------

func _on_match_finished(winners: Array[int]) -> void:
	var e := _plan_entry()
	var totals := c.scores.totals
	check(_match_over_seen, "maç bitme koşulu sağlanmadan bitti")
	check(c.settings.end_condition == e.end, "yanlış oyun türü")
	if e.end == MatchSettings.EndCondition.ROUNDS:
		check(c.rounds_played == e.rounds, "tur oyunu %d turda bitti, beklenen %d" % [c.rounds_played, e.rounds])
	else:
		check(totals.max() >= e.target, "hedef oyunu hedefe ulaşılmadan bitti")
	check(winners == MatchSettings.winners(totals), "kazanan yanlış")
	var kind := "%d tur oyunu" % e.rounds if e.end == MatchSettings.EndCondition.ROUNDS \
		else "%d hedef oyunu" % e.target
	_log.append("MAÇ %d (%s, %s) bitti: %d tur oynandı, toplam %s, kazanan %s" % [_match_index + 1,
		c.rules.display_name, kind, c.rounds_played, totals, winners])
	_match_over_seen = false
	_match_index += 1
	if _match_index < _plan.size():
		_save_plan_entry(_match_index)  # autoplay "YENİ OYUN" bunu okuyup modu değiştirir
		return
	await get_tree().create_timer(0.5).timeout
	_report()


func _report() -> void:
	print("\n===== UÇTAN UCA DOĞRULAMA =====")
	for line in _log:
		print(line)
	print("Maç: %d, tur: %d, löve: %d, zorunlu ihale: %d" % [_plan.size(), _rounds_checked,
		_tricks_checked, _forced_count])
	print("%d kontrol, %d hata" % [_checks, _failures])
	get_tree().quit(1 if _failures > 0 else 0)
