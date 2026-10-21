class_name TableController
extends Node
## Masadaki akışı yönetir:
##   maç ayarları → [dağıt → ihale → göm → koz söyle → yerdeki kartları al →
##   löveler → puan] x el sayısı → maç sonu.
##
## Kurallar BatakRules/BidManager/ScoreManager'da, kararlar AIPlayer'da,
## varyant ayarları GameRules'ta. Bu sınıf yalnızca sırayı yürütür ve
## sonuçları görsellere (Card3D, HandView, HUD) aktarır.

const DEAL_INTERVAL := 0.028
const DEAL_FLIGHT := 0.28
const PLAY_FLIGHT := 0.3
const AI_THINK_MIN := 0.45
const AI_THINK_MAX := 0.95
const ANNOUNCE_PAUSE := 0.8
const TRICK_PAUSE := 0.35
const WINNER_HIGHLIGHT_TIME := 0.55
const COLLECT_FLIGHT := 0.32
const COLLECT_STAGGER := 0.04
const KITTY_FLIGHT := 0.35
const KITTY_SPACING := 0.045
## Kartların keçe içine gömülmemesi için masa yüzeyinden yükseklik.
const TABLE_LIFT := 0.002
const TRICK_LAYER_STEP := 0.0008
const PILE_STEP := 0.0009
const PLAY_YAW_JITTER := 0.12
## Oyuncunun kartı ekrandan 3D'ye geçerken kameradan uzaklığı (m).
const HAND_TO_WORLD_DEPTH := 0.45
const NO_SEAT := -1

## Akış olayları (görsel/oyun davranışını etkilemez; doğrulama ve ileride
## istatistik/karakter tepkileri için dinlenebilir).
signal round_dealt
signal bidding_finished(bm: BidManager)
signal trick_finished(trick: Array[CardData], seats: Array[int], winner_seat: int)
signal round_finished(deltas: Array[int])
signal match_finished(winners: Array[int])

@export var table: Node3D
@export var seats_root: SeatLayout
@export var camera: SeatedCamera
@export var faces: CardFaceRenderer
@export var hud: GameHUD
@export var sfx: Sfx
@export var ai_difficulty := AIPlayer.Difficulty.NORMAL

## Oynanan modun kuralları (Normal İhaleli / Gömmeli İhaleli). Maç başında
## seçilen moda göre değişir.
var rules: GameRules
var settings: MatchSettings
var rounds_played := 0
var deck := DeckManager.new()
var scores: ScoreManager
var hands: Array = []
var kitty: Array[CardData] = []
var trump: int = NO_SEAT
var trump_broken := false
var bidder: int = NO_SEAT
var bid := 0
var dealer := 0
var tricks_won: Array[int] = []
## Kart oynama AI'larının ortak açık bilgi kaydı (yalnızca masada görülenler).
var _tracker: CardTracker
## İhale sahibinin gömdüğü kartlar; yalnızca ihale sahibinin AI'sına verilir.
var _buried: Array[CardData] = []

var _n := 3
var _layout: TableLayout
var _seat_names: Array[String] = []
var _ai := {}               # koltuk -> AIPlayer
var _opponent_hands := {}   # koltuk -> OpponentHandView
var _pile_counts: Array[int] = []
var _table_cards: Node3D
var _kitty_cards: Array[Card3D] = []
## Geliştirme: `-- --autoplay` ile oyuncunun kararlarını da AI verir.
var _autoplay := "--autoplay" in OS.get_cmdline_user_args()
var _autoplay_ai := AIPlayer.new(Seat.LOCAL_PLAYER)


func _ready() -> void:
	_table_cards = Node3D.new()
	_table_cards.name = "TableCards"
	add_child(_table_cards)
	# Menü arka planında da son seçilen modun masası görünsün.
	_apply_rules(GameRules.for_mode(MatchSettings.load_saved().mode))
	hud.next_round_requested.connect(_on_next_round)
	hud.start_requested.connect(_start_match)
	hud.new_game_requested.connect(_show_setup)
	faces.build()  # kart dokuları menü açıkken hazırlanır


## Oyunu başlatır (ana menüden "Oyuna Başla" ile çağrılır).
func begin() -> void:
	if not faces.is_ready:
		await faces.textures_ready
	_show_setup()


## Maç başı: kayıtlı ayarlarla masa ayarları panelini açar.
func _show_setup() -> void:
	_clear_table()
	hud.show_status("")
	# Önceki maçın el/puan bilgisi ayar ekranında görünmesin.
	hud.clear_info()
	for seat in range(1, _n):
		seats_root.get_opponent(seat).set_info("")
	settings = MatchSettings.load_saved()
	if _autoplay:
		_apply_dev_args(settings)
		_start_match(settings)
	else:
		hud.show_setup(settings)


func _start_match(s: MatchSettings) -> void:
	settings = s
	if rules.mode != s.mode:
		_apply_rules(GameRules.for_mode(s.mode))
	scores = ScoreManager.new(_n)
	rounds_played = 0
	dealer = _n - 1  # ilk elde ihaleyi oyuncu açsın
	_play_round()


## Kural setini uygular: oyuncu sayısına göre koltukları, rakipleri ve
## masa yerleşimini (yeniden) kurar.
func _apply_rules(r: GameRules) -> void:
	assert(r.is_valid(), "Kural seti tutarsız")
	rules = r
	_n = rules.player_count
	scores = ScoreManager.new(_n)
	var center: Vector3 = table.get_node("PlayArea").global_position
	_layout = TableLayout.new(center, _n)
	seats_root.build(_n, center)
	_seat_names.clear()
	_ai.clear()
	_opponent_hands.clear()
	for i in _n:
		var opp := seats_root.get_opponent(i)
		if opp == null:
			_seat_names.append("Sen")
			continue
		_seat_names.append(opp.display_name)
		var view := OpponentHandView.new()
		opp.get_hand_anchor().add_child(view)
		_opponent_hands[i] = view
		_ai[i] = AIPlayer.new(i, ai_difficulty)


func _play_round() -> void:
	hud.hide_round_end()
	_clear_table()
	trump = NO_SEAT
	trump_broken = false
	bidder = NO_SEAT
	bid = 0
	_buried.clear()
	tricks_won.clear()
	_pile_counts.clear()
	for i in _n:
		tricks_won.append(0)
		_pile_counts.append(0)
	_refresh_info()

	hud.show_status("Kartlar dağıtılıyor…")
	await _deal_animated()
	round_dealt.emit()
	await _run_bidding()
	_refresh_info()
	# İhaleden sonraki aşamalar moda göre: Normal İhaleli'de yalnızca koz;
	# Gömmeli'de önce elden göm, kozu söyle, sonra yeri al.
	var ai_trump := AIPlayer.choose_trump(hands[bidder], rules)  # AI kozunu gömmeden önce belirler
	for phase in rules.phases_after_bid():
		match phase:
			GameRules.PHASE_BURY:
				await _bury(ai_trump)
			GameRules.PHASE_TRUMP:
				await _choose_trump(ai_trump)
				_refresh_info()
			GameRules.PHASE_TAKE_KITTY:
				await _take_kitty()

	_tracker = CardTracker.new(_n, trump, bidder, bid, rules.cards_per_player, _buried.size())
	var leader := bidder
	for trick_no in rules.cards_per_player:
		leader = await _play_trick(leader)
	_finish_round()


func _finish_round() -> void:
	var deltas := scores.apply_round(bidder, bid, tricks_won)
	rounds_played += 1
	_refresh_info()
	round_finished.emit(deltas)
	var made := tricks_won[bidder] >= bid
	var who := "SEN" if bidder == Seat.LOCAL_PLAYER else _seat_names[bidder].to_upper()
	var verb := ("İHALEYİ YAPTIN" if made else "BATTIN") if bidder == Seat.LOCAL_PLAYER \
		else (who + " İHALEYİ YAPTI" if made else who + " BATTI")
	var summary := "%s  (%d / %d)" % [verb, tricks_won[bidder], bid]
	if not _autoplay:  # geliştirme koşuları istatistiği kirletmesin
		var stats := PlayerStats.load_from()
		stats.record_round(bidder == Seat.LOCAL_PLAYER, made)
		stats.save()
	hud.show_status("")
	if settings.is_match_over(rounds_played, scores.totals):
		_show_match_end(summary)
		return
	hud.show_round_end(summary, _seat_names, tricks_won, deltas, scores.totals, "SONRAKİ TUR")
	if _autoplay:
		await _wait(1.5)
		hud.next_round_requested.emit()


func _on_next_round() -> void:
	dealer = Seat.next(dealer, _n)
	_play_round()


## Maç sonu: kazananı ilan eder ve sıralamayı gösterir.
func _show_match_end(last_round_summary: String) -> void:
	var winners := MatchSettings.winners(scores.totals)
	if not _autoplay:
		var stats := PlayerStats.load_from()
		stats.record_match(winners.size() == 1 and winners[0] == Seat.LOCAL_PLAYER,
			scores.totals[Seat.LOCAL_PLAYER])
		stats.save()
	var title: String
	if winners.size() > 1:
		title = "BERABERE!"
	elif winners[0] == Seat.LOCAL_PLAYER:
		title = "KAZANDIN!"
	else:
		title = "KAZANAN: %s" % _seat_names[winners[0]].to_upper()
	var order: Array = range(_n)
	order.sort_custom(func(a: int, b: int): return scores.totals[a] > scores.totals[b])
	var lines: Array[String] = ["Son el: " + last_round_summary, ""]
	for place in order.size():
		var seat: int = order[place]
		lines.append("%d.  %s — %d puan" % [place + 1, _seat_names[seat], scores.totals[seat]])
	hud.show_match_end("OYUN BİTTİ — " + title, lines)
	match_finished.emit(winners)
	if _autoplay:
		print("[autoplay] maç bitti, oyun süresi %.1f sn" % (Time.get_ticks_msec() / 1000.0 * Engine.time_scale))
		await _wait(20.0)
		hud.new_game_requested.emit()


## Geliştirme: `--rounds=N` (tur oyunu) / `--target=M` (hedef oyunu) ve
## `--mode=standard|buried` ile ayar panelini atlamak için.
static func _apply_dev_args(s: MatchSettings) -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--rounds="):
			s.rounds = int(arg.trim_prefix("--rounds="))
			s.end_condition = MatchSettings.EndCondition.ROUNDS
		elif arg.begins_with("--target="):
			s.target_score = int(arg.trim_prefix("--target="))
			s.end_condition = MatchSettings.EndCondition.TARGET
		elif arg == "--mode=standard":
			s.mode = GameRules.Mode.STANDARD_BIDDING
		elif arg == "--mode=buried":
			s.mode = GameRules.Mode.BURIED_BIDDING


# --- Dağıtım -----------------------------------------------------------------

func _deal_animated() -> void:
	deck.build_deck()
	deck.shuffle()
	var first := Seat.next(dealer, _n)
	hands = deck.deal(_n, rules.cards_per_player, first)
	kitty = deck.take_remaining()
	var deck_pos := _layout.deck_spot(dealer) + Vector3.UP * TABLE_LIFT
	var stack := _make_deck_stack(deck_pos)
	var deck_screen := camera.unproject_position(deck_pos)
	var total := DeckManager.FULL_DECK_SIZE
	var dealt := 0
	for round_index in rules.cards_per_player:
		for offset in _n:
			var seat := (first + offset) % _n
			if seat == Seat.LOCAL_PLAYER:
				var card: CardData = hands[seat][round_index]
				hud.hand.add_card(card, faces.get_face(card), deck_screen)
			else:
				var c3d := _spawn_card(null, Transform3D(Card3D.table_basis(false), deck_pos))
				_opponent_hands[seat].receive(c3d, DEAL_FLIGHT)
			dealt += 1
			stack.scale.y = max(1.0 - float(dealt) / total, 0.02)
			sfx.play("card_deal")
			await _wait(DEAL_INTERVAL)
	# Yer kartları ortaya kapalı dizilir.
	for i in kitty.size():
		var c3d := _spawn_card(null, Transform3D(Card3D.table_basis(false), deck_pos))
		var x := (i - (kitty.size() - 1) * 0.5) * KITTY_SPACING
		var target := _layout.kitty_spot() + Vector3(x, TABLE_LIFT + i * TRICK_LAYER_STEP, 0)
		c3d.move_to(Transform3D(Card3D.table_basis(false, 0.05 * (i - 1.5)), target), DEAL_FLIGHT, 0.04)
		_kitty_cards.append(c3d)
		sfx.play("card_deal")
		await _wait(DEAL_INTERVAL * 2.0)
	stack.queue_free()
	await _wait(DEAL_FLIGHT)


func _make_deck_stack(pos: Vector3) -> Node3D:
	var stack := Node3D.new()
	_table_cards.add_child(stack)
	stack.global_position = pos
	var box := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = Vector3(Card3D.SIZE.x, 0.02, Card3D.SIZE.y)
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.92, 0.9, 0.84)
	mesh.material = mat
	box.mesh = mesh
	box.position.y = 0.01
	stack.add_child(box)
	var top := Card3D.new()
	top.setup(null, faces)
	stack.add_child(top)
	top.transform = Transform3D(Card3D.table_basis(false), Vector3.UP * 0.0205)
	return stack


# --- İhale ---------------------------------------------------------------------

## İhale turunu oynatır. Herkes pas derse ihale kurala göre zorunlu verilir.
func _run_bidding() -> void:
	var bm := BidManager.new(rules, dealer)
	while not bm.is_finished():
		var seat := bm.current_seat()
		var choice: int
		if seat == Seat.LOCAL_PLAYER:
			hud.show_status("")
			var current := "Henüz ihale yok — en az %d" % rules.min_bid if bm.current_holder < 0 \
				else "En yüksek: %s — %d" % [_seat_names[bm.current_holder], bm.current_bid]
			if _autoplay:
				await _wait(AI_THINK_MAX)
				choice = _autoplay_ai.choose_bid_in_context(hands[seat], BidContext.from_bid_manager(bm, rules))
			else:
				hud.show_bidding(bm.valid_bids(), current)
				choice = await hud.bid_chosen
		else:
			hud.show_status("%s düşünüyor…" % _seat_names[seat])
			await _wait(randf_range(AI_THINK_MIN, AI_THINK_MAX))
			choice = _ai[seat].choose_bid_in_context(hands[seat], BidContext.from_bid_manager(bm, rules))
		if choice == BidManager.PASS or not bm.bid(choice):
			choice = BidManager.PASS
			bm.pass_turn()
		_announce(seat, "PAS" if choice == BidManager.PASS else str(choice))
	bidder = bm.current_holder
	bid = bm.current_bid
	var who := "Sen" if bidder == Seat.LOCAL_PLAYER else _seat_names[bidder]
	if bm.forced:  # herkes pas: yeni tur yok, dağıtanın sağındakine zorunlu
		hud.show_status("Herkes pas dedi — ihale zorunlu olarak %s'de: %d" % [who, bid])
	else:
		hud.show_status("İhale %s'de: %d" % [who, bid])
	bidding_finished.emit(bm)
	await _wait(ANNOUNCE_PAUSE)


## Bir oyuncunun sözünü gösterir: rakipte baş üstü balon, oyuncuda durum yazısı.
func _announce(seat: int, text: String) -> void:
	var opp := seats_root.get_opponent(seat)
	if opp:
		opp.say(text)
	else:
		hud.show_status("Sen: %s" % text)


# --- Yer kartları ve gömme -------------------------------------------------------

## İhaleyi alan, gömüp kozu söyledikten sonra yerdeki kartları eline alır
## (rakipse kapalı kalır).
func _take_kitty() -> void:
	hands[bidder].append_array(kitty)
	for i in _kitty_cards.size():
		var c3d := _kitty_cards[i]
		if bidder == Seat.LOCAL_PLAYER:
			var card := kitty[i]
			var screen := camera.unproject_position(c3d.global_position)
			c3d.queue_free()
			hud.hand.add_card(card, faces.get_face(card), screen)
		else:
			_opponent_hands[bidder].receive(c3d, KITTY_FLIGHT)
		sfx.play("card_deal")
		await _wait(0.08)
	_kitty_cards.clear()
	await _wait(KITTY_FLIGHT)


## İhaleyi alan, yerdeki kartları görmeden kendi elinden gömer.
func _bury(ai_trump: int) -> void:
	var count := rules.buried_cards
	var to_bury: Array[CardData]
	if bidder == Seat.LOCAL_PLAYER and not _autoplay:
		hud.show_status("")
		hud.show_bury(count)
		hud.hand.begin_multi_select(count)
		await hud.bury_confirmed
		hud.hide_bury()
		to_bury = hud.hand.end_multi_select()
	else:
		if bidder != Seat.LOCAL_PLAYER:
			hud.show_status("%s kart gömüyor…" % _seat_names[bidder])
		await _wait(AI_THINK_MAX)
		to_bury = AIPlayer.choose_bury(hands[bidder], count, ai_trump)
	_buried = to_bury.duplicate()
	var spot := _layout.bury_spot(bidder)
	var yaw := _layout.seat_yaw(bidder)
	for i in to_bury.size():
		var card := to_bury[i]
		hands[bidder].erase(card)
		deck.register_played(card)
		var c3d: Card3D
		if bidder == Seat.LOCAL_PLAYER:
			var screen_pos := hud.hand.remove_card(card)
			c3d = _spawn_card(card, _camera_card_transform(screen_pos))
		else:
			c3d = _opponent_hands[bidder].take_card(_table_cards)  # kapalı kalır
		var pos := spot + Vector3.UP * (TABLE_LIFT + i * PILE_STEP)
		c3d.move_to(Transform3D(Card3D.table_basis(false, yaw), pos), PLAY_FLIGHT, 0.05)
		sfx.play("card_place")
		await _wait(0.1)
	await _wait(PLAY_FLIGHT)


func _choose_trump(ai_trump: int) -> void:
	if bidder == Seat.LOCAL_PLAYER and not _autoplay:
		hud.show_status("")
		hud.show_trump_choice()
		trump = await hud.trump_chosen
	else:
		await _wait(AI_THINK_MIN)
		trump = ai_trump
	var text := "Koz %s" % CardData.SUIT_SYMBOLS[trump]
	_announce(bidder, text)
	if bidder != Seat.LOCAL_PLAYER:
		hud.show_status("%s: %s %s" % [_seat_names[bidder], text, CardData.SUIT_NAMES_TR[trump]])
	await _wait(ANNOUNCE_PAUSE)


# --- Löve ---------------------------------------------------------------------

## Bir löveyi oynatır ve kazanan koltuğu döndürür.
func _play_trick(leader: int) -> int:
	var trick: Array[CardData] = []
	var trick_seats: Array[int] = []
	var placed: Array[Card3D] = []
	var seat := leader
	for i in _n:
		var hand: Array[CardData] = hands[seat]
		var legal := BatakRules.legal_cards(hand, trick, trump, trump_broken)
		var card: CardData
		if seat == Seat.LOCAL_PLAYER:
			hud.show_status("")
			hud.show_turn(true)
			if _autoplay:
				await _wait(AI_THINK_MAX)
				card = _autoplay_ai.choose_card_in_context(_context(seat, legal, trick, trick_seats))
			else:
				hud.hand.set_input_enabled(true, legal)
				card = await hud.hand.card_chosen
			hud.show_turn(false)
			hud.hand.set_input_enabled(false)
		else:
			hud.show_status("%s düşünüyor…" % _seat_names[seat])
			await _wait(randf_range(AI_THINK_MIN, AI_THINK_MAX))
			card = _ai[seat].choose_card_in_context(_context(seat, legal, trick, trick_seats))
		hand.erase(card)
		deck.register_played(card)
		_tracker.record_play(seat, card)
		if card.suit == trump:
			trump_broken = true
		trick.append(card)
		trick_seats.append(seat)
		placed.append(await _animate_play(seat, card, i))
		seat = Seat.next(seat, _n)
	hud.show_status("")

	var w := BatakRules.trick_winner(trick, trump)
	var winner_seat := trick_seats[w]
	await _wait(TRICK_PAUSE)
	placed[w].set_highlighted(true)
	hud.show_status("Löveyi %s aldı" % ("sen" if winner_seat == Seat.LOCAL_PLAYER else _seat_names[winner_seat]))
	await _wait(WINNER_HIGHLIGHT_TIME)
	placed[w].set_highlighted(false)
	await _collect_trick(placed, winner_seat)
	tricks_won[winner_seat] += 1
	_tracker.record_trick_end(winner_seat)
	_refresh_info()
	trick_finished.emit(trick, trick_seats, winner_seat)
	return winner_seat


## AI'nın karar bağlamı: kendi eli, yasal kartlar, masadaki açık kartlar ve
## tracker. Gömülen kartlar yalnızca ihale sahibine verilir (hile yok).
func _context(seat: int, legal: Array[CardData], trick: Array[CardData], trick_seats: Array[int]) -> PlayContext:
	return PlayContext.build(rules, seat, hands[seat], legal, trick, trick_seats, _tracker,
		_buried if seat == bidder else ([] as Array[CardData]))


## Kartı oyuncunun elinden/rakibin elinden masadaki yuvasına uçurur.
func _animate_play(seat: int, card: CardData, order_in_trick: int) -> Card3D:
	var c3d: Card3D
	if seat == Seat.LOCAL_PLAYER:
		c3d = _spawn_card(card, _camera_card_transform(hud.hand.remove_card(card)))
		camera.nudge()
	else:
		c3d = _opponent_hands[seat].take_card(_table_cards)
		c3d.setup(card, faces)
	var slot_pos := _layout.trick_slot(seat)
	slot_pos.y += TABLE_LIFT + order_in_trick * TRICK_LAYER_STEP
	var yaw := randf_range(-PLAY_YAW_JITTER, PLAY_YAW_JITTER)
	await c3d.move_to(Transform3D(Card3D.table_basis(true, yaw), slot_pos), PLAY_FLIGHT, 0.06).finished
	sfx.play("card_place")
	return c3d


## Löve kartlarını kapalı olarak kazananın önündeki yığına toplar.
func _collect_trick(cards: Array[Card3D], winner_seat: int) -> void:
	var spot := _layout.pile_spot(winner_seat)
	var yaw := _layout.seat_yaw(winner_seat)
	sfx.play("trick_collect")
	var last: Tween
	for c3d in cards:
		var pos := spot + Vector3.UP * (TABLE_LIFT + _pile_counts[winner_seat] * PILE_STEP)
		_pile_counts[winner_seat] += 1
		last = c3d.move_to(Transform3D(Card3D.table_basis(false, yaw), pos), COLLECT_FLIGHT, 0.03)
		await _wait(COLLECT_STAGGER)
	# Uzun bir kare (takılma, yavaş cihaz) sırasında son animasyon bu bekleme
	# içinde bitmiş olabilir; bitmiş bir Tween'in `finished` sinyalini beklemek
	# oyunu sonsuza kadar dondurur. Yalnızca hâlâ çalışıyorsa bekle.
	if last.is_valid() and last.is_running():
		await last.finished


# --- Yardımcılar ----------------------------------------------------------------

## Eldeki 2D kartın ekrandaki yerine denk gelen, kameraya bakan 3D dönüşüm.
func _camera_card_transform(screen_pos: Vector2) -> Transform3D:
	return Transform3D(camera.global_basis, camera.project_position(screen_pos, HAND_TO_WORLD_DEPTH))


func _spawn_card(card: CardData, world_transform: Transform3D) -> Card3D:
	var c3d := Card3D.new()
	_table_cards.add_child(c3d)
	c3d.setup(card, faces)
	c3d.global_transform = world_transform
	return c3d


func _refresh_info() -> void:
	var progress := "TUR %d / %d" % [rounds_played + 1, settings.rounds] \
		if settings.end_condition == MatchSettings.EndCondition.ROUNDS \
		else "TUR %d   ·   HEDEF %d" % [rounds_played + 1, settings.target_score]
	var header := "%s   ·   %s" % [rules.display_name, progress]
	var bidder_name := "" if bidder == NO_SEAT else _seat_names[bidder]
	hud.update_info(header, bidder_name, bid, trump, tricks_won[Seat.LOCAL_PLAYER],
		scores.totals[Seat.LOCAL_PLAYER])
	for seat in range(1, _n):
		seats_root.get_opponent(seat).set_info("%d el · %d puan" % [tricks_won[seat], scores.totals[seat]])


func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout


func _clear_table() -> void:
	for child in _table_cards.get_children():
		child.queue_free()
	_kitty_cards.clear()
	for view in _opponent_hands.values():
		view.clear()
	hud.hand.clear()
