class_name HandCard
extends TextureRect
## Oyuncunun elindeki tek bir kart (2D).
##
## Konum/dönüş/ölçek hedeflerine her karede yumuşakça yaklaşır; böylece
## yerleşim değişiklikleri, üzerine gelme ve dağıtım animasyonları birbiriyle
## çakışmadan aynı mekanizmayla çalışır.

signal pressed(hand_card: HandCard)

## Hedefe yaklaşma hızı (1/sn). Büyük = daha çevik.
const FOLLOW_SPEED := 14.0
const HOVER_LIFT_RATIO := 0.12
const SELECT_LIFT_RATIO := 0.18
const DIM_COLOR := Color(0, 0, 0, 0.45)
const OUTLINE_COLOR := Color(1.0, 0.8, 0.3)
const CORNER_RADIUS_RATIO := 0.07

var card: CardData
var target_position := Vector2.ZERO
var target_rotation := 0.0
var target_scale := 1.0
var hovered := false
var selected := false:
	set(v):
		selected = v
		queue_redraw()
var playable := true:
	set(v):
		playable = v
		queue_redraw()


func _init(p_card: CardData, tex: Texture2D, card_size: Vector2) -> void:
	card = p_card
	texture = tex
	expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	stretch_mode = TextureRect.STRETCH_SCALE
	size = card_size
	pivot_offset = Vector2(card_size.x * 0.5, card_size.y)
	mouse_filter = Control.MOUSE_FILTER_STOP
	mouse_entered.connect(func(): hovered = true)
	mouse_exited.connect(func(): hovered = false)


func set_card_size(card_size: Vector2) -> void:
	size = card_size
	pivot_offset = Vector2(card_size.x * 0.5, card_size.y)


func _process(delta: float) -> void:
	var lift := 0.0
	if selected:
		lift = SELECT_LIFT_RATIO
	elif hovered and playable:
		lift = HOVER_LIFT_RATIO
	var goal := target_position + Vector2(0, -lift * size.y).rotated(target_rotation)
	var k := 1.0 - exp(-FOLLOW_SPEED * delta)  # kare hızından bağımsız yumuşatma
	position = position.lerp(goal, k)
	rotation = lerp_angle(rotation, target_rotation, k)
	scale = scale.lerp(Vector2.ONE * target_scale, k)


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		pressed.emit(self)
		accept_event()


## Doku üstüne: seçili kartta altın çerçeve, oynanamayan kartta karartma.
func _draw() -> void:
	var r := int(size.x * CORNER_RADIUS_RATIO)
	if not playable:
		var dim := StyleBoxFlat.new()
		dim.bg_color = DIM_COLOR
		dim.set_corner_radius_all(r)
		draw_style_box(dim, Rect2(Vector2.ZERO, size))
	if selected:
		var outline := StyleBoxFlat.new()
		outline.draw_center = false
		outline.set_border_width_all(5)
		outline.border_color = OUTLINE_COLOR
		outline.set_corner_radius_all(r)
		draw_style_box(outline, Rect2(Vector2.ZERO, size))


## Oynanamayan karta tıklanınca kısa bir "hayır" sallanması.
func shake() -> void:
	var t := create_tween()
	for dx in [10.0, -10.0, 6.0, 0.0]:
		t.tween_property(self, "target_position:x", target_position.x + dx, 0.04)
