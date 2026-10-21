class_name HandView
extends Control
## Oyuncunun elini ekranın altında İKİ SIRA hâlinde gösterir (13 → 7+6,
## 16 → 8+8). Satır/sütun hesabı rakip elleriyle ortaktır (TwoRowLayout).
##
## Okunabilirlik ve dokunma kuralları:
## - Kart yüksekliği ekran yüksekliğine oranlıdır (mobilde de büyük kalır).
## - Sıra içindeki adım, sol üst köşedeki değer+sembol her zaman görünecek
##   kadar geniştir (MIN_VISIBLE_RATIO); üst sıra, köşesi alt sıranın üstünde
##   kalacak kadar yukarıdadır (TOP_ROW_RAISE_RATIO).
## - Dokunma alanı = görünen alan: alt sıra üst sıranın, sıra içinde sağdaki
##   kart soldakinin önünde çizilir (çocuk sırası); en üstteki kart girişi
##   alır. Böylece görünen şeride dokunmak hep o kartı seçer, komşuyu değil.
##
## Etkileşim: fareyle üzerine gelince kart kalkar, tıklayınca oynanır.
## Dokunmatik ekranda ilk dokunuş kartı seçer (kaldırır), ikincisi oynar.
## Gömme sırasında çoklu seçim modu: tıklanan kartlar seçilir/bırakılır.

signal card_chosen(card: CardData)
signal selection_changed(count: int)

const CARD_HEIGHT_RATIO := 0.245      # ekran yüksekliğine göre (değer+sembol mobilde okunur)
const CARD_ASPECT := 256.0 / 358.0
const MAX_SPREAD_RATIO := 0.62        # iki sıralı bloğun kaplayabileceği en fazla genişlik
const MAX_STEP_RATIO := 0.74          # az kart varken kartlar arası en fazla aralık
const MIN_VISIBLE_RATIO := 0.54       # her kartın en az bu kadarı görünür (dokunma şeridi)
const HIDDEN_BELOW_RATIO := 0.42      # alt sıranın ekran altına taşan kısmı
const TOP_ROW_RAISE_RATIO := 0.38     # üst sıranın alt sıradan yüksekliği: köşedeki değer+sembol (kartın ~%37si) görünür
const FAN_DEG_PER_CARD := 1.1
const FAN_CURVE_RATIO := 0.004        # kenarlara doğru aşağı inme miktarı

@export var tap_to_select := false

var _cards: Array[HandCard] = []
var _input_enabled := false
## > 0 iken çoklu seçim modundayız (en fazla bu kadar kart seçilebilir).
var _multi_select_max := 0


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


## Gömme için çoklu seçimi başlatır.
func begin_multi_select(max_count: int) -> void:
	_multi_select_max = max_count
	_input_enabled = true
	for hc in _cards:
		hc.selected = false
		hc.playable = true
	selection_changed.emit(0)


## Çoklu seçimi bitirir ve seçilen kartları döndürür.
func end_multi_select() -> Array[CardData]:
	var out: Array[CardData] = []
	for hc in _cards:
		if hc.selected:
			out.append(hc.card)
		hc.selected = false
	_multi_select_max = 0
	_input_enabled = false
	return out


func selected_count() -> int:
	return _cards.filter(func(hc: HandCard): return hc.selected).size()


func _on_card_pressed(hc: HandCard) -> void:
	if not _input_enabled:
		return
	if _multi_select_max > 0:
		if hc.selected or selected_count() < _multi_select_max:
			hc.selected = not hc.selected
		else:
			hc.shake()
		selection_changed.emit(selected_count())
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
	var ext := TwoRowLayout.extent(n)
	var span := ext.y - ext.x
	var step := cs.x * MAX_STEP_RATIO
	if span > 0.0:
		step = minf(step, (vp.x * MAX_SPREAD_RATIO - cs.x) / span)
	step = maxf(step, cs.x * MIN_VISIBLE_RATIO)
	var mid := (ext.x + ext.y) * 0.5
	var bottom_y := vp.y - cs.y * (1.0 - HIDDEN_BELOW_RATIO)
	var single_row := TwoRowLayout.row_counts(n).y == 0   # tek kart: aşağıda dursun
	for i in n:
		var hc := _cards[i]
		var sl := TwoRowLayout.slot(i, n)
		var c: float = sl.center
		var y := bottom_y if (sl.row == 1 or single_row) else bottom_y - cs.y * TOP_ROW_RAISE_RATIO
		hc.set_card_size(cs)
		hc.target_position = Vector2(vp.x * 0.5 + (sl.offset - mid) * step - cs.x * 0.5,
			y + c * c * FAN_CURVE_RATIO * cs.y)
		hc.target_rotation = deg_to_rad(c * FAN_DEG_PER_CARD)
		hc.target_scale = 1.0
