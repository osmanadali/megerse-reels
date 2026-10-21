class_name TableController
extends Node
## Masadaki akışı yönetir: dağıt → 13 löve → el sonu.
##
## Kurallar BatakRules'ta, kararlar AIPlayer'da, veriler DeckManager'da;
## bu sınıf yalnızca sırayı yürütür ve görsellere (Card3D, HandView) aktarır.
##
## Prototip notu: İhale ve gömme henüz yok (Faz 7-8). Şimdilik koz Maça ve
## ilk löveyi dağıtanın sağındaki oyuncu açar.

const DEAL_INTERVAL := 0.03
const DEAL_FLIGHT := 0.28
const PLAY_FLIGHT := 0.3
const AI_THINK_MIN := 0.45
const AI_THINK_MAX := 0.95
const TRICK_PAUSE := 0.35
const WINNER_HIGHLIGHT_TIME := 0.55
const COLLECT_FLIGHT := 0.32
const COLLECT_STAGGER := 0.04
## Kartların keçe içine gömülmemesi için masa yüzeyinden yükseklik.
const TABLE_LIFT := 0.002
const TRICK_LAYER_STEP := 0.0008
const PILE_STEP := 0.0009
const PLAY_YAW_JITTER := 0.12
## Oyuncunun kartı ekrandan 3D'ye geçerken kameradan uzaklığı (m).
const HAND_TO_WORLD_DEPTH := 0.45
## Deste, dağıtanın önünde masa merkezi ile koltuk arasında bu oranda durur.
const DECK_TOWARD_DEALER := 0.42

@export var table: Node3D
@export var seats_root: Node3D
@export var camera: SeatedCamera
@export var faces: CardFaceRenderer
@export var hud: GameHUD
@export var sfx: Sfx
@export var ai_difficulty := AIPlayer.Difficulty.NORMAL

var deck := DeckManager.new()
var hands: Array = []
var trump: int = CardData.Suit.SPADES
var trump_broken := false
var dealer: int = Seat.Position.WEST
var tricks_won: Array[int] = [0, 0, 0, 0]

var _seat_nodes: Array[Node3D] = []
var _seat_names: Array[String] = []
var _ai := {}               # koltuk -> AIPlayer
var _opponent_hands := {}   # koltuk -> OpponentHandView
var _trick_slots: Array[Node3D] = []
var _piles: Array[Node3D] = []
var _pile_counts: Array[int] = [0, 0, 0, 0]
var _table_cards: Node3D
var _deck_stack: Node3D
## Geliştirme: `-- --autoplay` ile oyuncunun kartlarını da AI seçer.
var _autoplay := "--autoplay" in OS.get_cmdline_user_args()
var _autoplay_ai := AIPlayer.new(Seat.LOCAL_PLAYER)


func _ready() -> void:
	_collect_scene_refs()
	hud.restart_requested.connect(_on_restart)
	if not faces.is_ready:
		await faces.build()
	_play_round()


func _collect_scene_refs() -> void:
	for i in Seat.COUNT:
		var seat_node: Node3D = seats_root.get_child(i)
		_seat_nodes.append(seat_node)
		var name_tr: String = Seat.NAMES_TR[i]
		for child in seat_node.get_children():
			if child is OpponentPlaceholder:
				name_tr = child.display_name
				var view := OpponentHandView.new()
				child.get_hand_anchor().add_child(view)
				_opponent_hands[i] = view
				_ai[i] = AIPlayer.new(i, ai_difficulty)
		_seat_names.append(name_tr)
	var play_area := table.get_node("PlayArea")
	for i in Seat.COUNT:
		_trick_slots.append(play_area.get_node("TrickSlots").get_child(i))
		_piles.append(play_area.get_node("TrickPiles").get_child(i))
	_table_cards = Node3D.new()
	_table_cards.name = "TableCards"
	add_child(_table_cards)


func _play_round() -> void:
	hud.hide_round_end()
	_clear_table()
	trump_broken = false
	tricks_won = [0, 0, 0, 0]
	hud.update_tricks(_seat_names, tricks_won)
	hud.show_status("Kartlar dağıtılıyor…")
	await _deal_animated()
	var leader := Seat.next(dealer)
	for trick_no in DeckManager.CARDS_PER_PLAYER:
		leader = await _play_trick(leader)
	hud.show_status("")
	hud.show_round_end(_seat_names, tricks_won)
	if _autoplay:
		await get_tree().create_timer(1.5).timeout
		hud.restart_requested.emit()


func _on_restart() -> void:
	dealer = Seat.next(dealer)
	_play_round()


# --- Dağıtım -----------------------------------------------------------------

func _deal_animated() -> void:
	deck.build_deck()
	deck.shuffle()
	var first := Seat.next(dealer)
	hands = deck.deal(Seat.COUNT, DeckManager.CARDS_PER_PLAYER, first)
	var deck_pos := _deck_position()
	_deck_stack = _make_deck_stack(deck_pos)
	var deck_screen := camera.unproject_position(deck_pos)
	var total := Seat.COUNT * DeckManager.CARDS_PER_PLAYER
	var dealt := 0
	for round_index in DeckManager.CARDS_PER_PLAYER:
		for offset in Seat.COUNT:
			var seat := (first + offset) % Seat.COUNT
			if seat == Seat.LOCAL_PLAYER:
				var card: CardData = hands[seat][round_index]
				hud.hand.add_card(card, faces.get_face(card), deck_screen)
			else:
				var c3d := _spawn_card(null, Transform3D(Card3D.table_basis(false), deck_pos))
				_opponent_hands[seat].receive(c3d, DEAL_FLIGHT)
			dealt += 1
			_deck_stack.scale.y = max(1.0 - float(dealt) / total, 0.02)
			sfx.play("card_deal")
			await get_tree().create_timer(DEAL_INTERVAL).timeout
	_deck_stack.queue_free()
	await get_tree().create_timer(DEAL_FLIGHT).timeout


func _deck_position() -> Vector3:
	var center: Vector3 = table.get_node("PlayArea").global_position
	var toward := _seat_nodes[dealer].global_position
	toward.y = center.y
	return center.lerp(toward, DECK_TOWARD_DEALER) + Vector3.UP * TABLE_LIFT


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


# --- Löve ---------------------------------------------------------------------

## Bir löveyi oynatır ve kazanan koltuğu döndürür.
func _play_trick(leader: int) -> int:
	var trick: Array[CardData] = []
	var trick_seats: Array[int] = []
	var placed: Array[Card3D] = []
	var seat := leader
	for i in Seat.COUNT:
		var hand: Array[CardData] = hands[seat]
		var legal := BatakRules.legal_cards(hand, trick, trump, trump_broken)
		var card: CardData
		if seat == Seat.LOCAL_PLAYER:
			hud.show_status("")
			hud.show_turn(true)
			hud.hand.set_input_enabled(true, legal)
			if _autoplay:
				await get_tree().create_timer(AI_THINK_MAX).timeout
				card = _autoplay_ai.choose_card(legal, trick, trump)
			else:
				card = await hud.hand.card_chosen
			hud.show_turn(false)
			hud.hand.set_input_enabled(false)
		else:
			hud.show_status("%s düşünüyor…" % _seat_names[seat])
			await get_tree().create_timer(randf_range(AI_THINK_MIN, AI_THINK_MAX)).timeout
			card = _ai[seat].choose_card(legal, trick, trump)
		hand.erase(card)
		deck.register_played(card)
		if card.suit == trump:
			trump_broken = true
		trick.append(card)
		trick_seats.append(seat)
		placed.append(await _animate_play(seat, card, i))
		seat = Seat.next(seat)
	hud.show_status("")

	var w := BatakRules.trick_winner(trick, trump)
	var winner_seat := trick_seats[w]
	await get_tree().create_timer(TRICK_PAUSE).timeout
	placed[w].set_highlighted(true)
	hud.show_status("Löveyi %s aldı" % ("sen" if winner_seat == Seat.LOCAL_PLAYER else _seat_names[winner_seat]))
	await get_tree().create_timer(WINNER_HIGHLIGHT_TIME).timeout
	placed[w].set_highlighted(false)
	await _collect_trick(placed, winner_seat)
	tricks_won[winner_seat] += 1
	hud.update_tricks(_seat_names, tricks_won)
	return winner_seat


## Kartı oyuncunun elinden/rakibin elinden masadaki yuvasına uçurur.
func _animate_play(seat: int, card: CardData, order_in_trick: int) -> Card3D:
	var c3d: Card3D
	if seat == Seat.LOCAL_PLAYER:
		var screen_pos := hud.hand.remove_card(card)
		var start := Transform3D(camera.global_basis, camera.project_position(screen_pos, HAND_TO_WORLD_DEPTH))
		c3d = _spawn_card(card, start)
		camera.nudge()
	else:
		c3d = _opponent_hands[seat].take_card(_table_cards)
		c3d.setup(card, faces)
	var slot_pos := _trick_slots[seat].global_position
	slot_pos.y += TABLE_LIFT + order_in_trick * TRICK_LAYER_STEP
	var yaw := randf_range(-PLAY_YAW_JITTER, PLAY_YAW_JITTER)
	await c3d.move_to(Transform3D(Card3D.table_basis(true, yaw), slot_pos), PLAY_FLIGHT, 0.06).finished
	sfx.play("card_place")
	return c3d


## Löve kartlarını kapalı olarak kazananın önündeki yığına toplar.
func _collect_trick(cards: Array[Card3D], winner_seat: int) -> void:
	var pile := _piles[winner_seat]
	sfx.play("trick_collect")
	var last: Tween
	for c3d in cards:
		var pos := pile.global_position + Vector3.UP * (TABLE_LIFT + _pile_counts[winner_seat] * PILE_STEP)
		_pile_counts[winner_seat] += 1
		var target := Transform3D(Card3D.table_basis(false, pile.global_rotation.y), pos)
		last = c3d.move_to(target, COLLECT_FLIGHT, 0.03)
		await get_tree().create_timer(COLLECT_STAGGER).timeout
	await last.finished


func _spawn_card(card: CardData, world_transform: Transform3D) -> Card3D:
	var c3d := Card3D.new()
	_table_cards.add_child(c3d)
	c3d.setup(card, faces)
	c3d.global_transform = world_transform
	return c3d


func _clear_table() -> void:
	for child in _table_cards.get_children():
		child.queue_free()
	for view in _opponent_hands.values():
		view.clear()
	hud.hand.clear()
	_pile_counts = [0, 0, 0, 0]
