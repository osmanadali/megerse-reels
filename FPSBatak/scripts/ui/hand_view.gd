class_name HandView
extends Control
## Oyuncunun elini ekranın altında yelpaze şeklinde gösterir.
##
## Okunabilirlik kuralları:
## - Kart yüksekliği ekran yüksekliğine oranlıdır (mobilde de büyük kalır).
## - Kartlar arası aralık, sol üst köşedeki değer+sembol her zaman görünecek
##   kadar geniş tutulur (MIN_VISIBLE_RATIO).
##
## Etkileşim: fareyle üzerine gelince kart kalkar, tıklayınca oynanır.
## Dokunmatik ekranda ilk dokunuş kartı seçer (kaldırır), ikincisi oynar.

signal card_chosen(card: CardData)

const CARD_HEIGHT_RATIO := 0.28       # ekran yüksekliğine göre
const CARD_ASPECT := 256.0 / 358.0
const MAX_SPREAD_RATIO := 0.80        # elin kaplayabileceği en fazla genişlik
const MAX_STEP_RATIO := 0.72          # az kart varken kartlar arası en fazla aralık
const MIN_VISIBLE_RATIO := 0.40       # her kartın en az bu kadarı görünür
const HIDDEN_BELOW_RATIO := 0.30      # kartın ekran altına taşan kısmı
const FAN_DEG_PER_CARD := 1.5
const FAN_CURVE_RATIO := 0.006        # kenarlara doğru aşağı inme miktarı

@export var tap_to_select := false

var _cards: Array[HandCard] = []
var _input_enabled := false


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	tap_to_select = tap_to_select or OS.has_feature("mobile")
	get_viewport().size_changed.connect(_layout)


func card_size() -> Vector2:
	var h := get_viewport_rect().size.y * CARD_HEIGHT_RATIO
	return Vector2(h * CARD_ASPECT, h)


## Ele kart ekler; kart `from_screen_pos` noktasından küçük başlayıp yerine süzülür.
func add_card(card: CardData, tex: Texture2D, from_screen_pos: Vector2) -> void:
	var hc := HandCard.new(card, tex, card_size())
	hc.position = from_screen_pos - hc.size * 0.5
	hc.scale = Vector2.ONE * 0.25
	hc.pressed.connect(_on_card_pressed)
	_cards.append(hc)
	_cards.sort_custom(func(a: HandCard, b: HandCard): return CardData.sort_for_hand(a.card, b.card))
	add_child(hc)
	for i in _cards.size():
		move_child(_cards[i], i)
	_layout()


## Kartı elden çıkarır ve ekrandaki merkez konumunu döndürür (3D'ye geçiş için).
func remove_card(card: CardData) -> Vector2:
	for hc in _cards:
		if hc.card.same_as(card):
			var center := hc.get_global_rect().get_center()
			_cards.erase(hc)
			hc.queue_free()
			_layout()
			return center
	return get_viewport_rect().size * Vector2(0.5, 0.85)


func clear() -> void:
	for hc in _cards:
		hc.queue_free()
	_cards.clear()


## Oyuncunun kart seçebilmesini açar/kapatır. `legal` dışındaki kartlar karartılır.
func set_input_enabled(enabled: bool, legal: Array[CardData] = []) -> void:
	_input_enabled = enabled
	for hc in _cards:
		hc.selected = false
		hc.playable = not enabled or legal.any(func(c: CardData): return c.same_as(hc.card))


func _on_card_pressed(hc: HandCard) -> void:
	if not _input_enabled:
		return
	if not hc.playable:
		hc.shake()
		return
	if tap_to_select and not hc.selected:
		for other in _cards:
			other.selected = other == hc
		return
	_input_enabled = false
	card_chosen.emit(hc.card)


func _layout() -> void:
	var n := _cards.size()
	if n == 0:
		return
	var vp := get_viewport_rect().size
	var cs := card_size()
	var max_spread := vp.x * MAX_SPREAD_RATIO
	var step := cs.x * MAX_STEP_RATIO
	if n > 1:
		step = min(step, (max_spread - cs.x) / (n - 1))
	step = max(step, cs.x * MIN_VISIBLE_RATIO)
	var total := cs.x + step * (n - 1)
	var left := (vp.x - total) * 0.5
	var base_y := vp.y - cs.y * (1.0 - HIDDEN_BELOW_RATIO)
	var mid := (n - 1) * 0.5
	for i in n:
		var hc := _cards[i]
		hc.set_card_size(cs)
		var off := i - mid
		hc.target_position = Vector2(left + step * i, base_y + off * off * FAN_CURVE_RATIO * cs.y)
		hc.target_rotation = deg_to_rad(off * FAN_DEG_PER_CARD)
		hc.target_scale = 1.0
