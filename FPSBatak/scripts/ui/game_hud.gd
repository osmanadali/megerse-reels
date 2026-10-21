class_name GameHUD
extends CanvasLayer
## Oyun içi arayüz. Sade tutulur: kartların önüne geçmez.
## Koyu zemin + altın/bakır vurgular.

signal restart_requested

const GOLD := Color(0.95, 0.77, 0.4)
const PANEL_BG := Color(0.06, 0.045, 0.035, 0.82)

var hand: HandView
var _turn_banner: Label
var _status: Label
var _score: Label
var _end_panel: PanelContainer
var _end_label: Label


func _ready() -> void:
	hand = HandView.new()
	add_child(hand)
	move_child(hand, 0)  # el, diğer HUD öğelerinin altında

	_turn_banner = _make_label(40, GOLD)
	_turn_banner.text = "SIRA SENDE"
	_turn_banner.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_turn_banner.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	_turn_banner.offset_top = -0.27 * get_viewport().get_visible_rect().size.y
	_turn_banner.offset_bottom = _turn_banner.offset_top + 56
	_turn_banner.offset_left = -300
	_turn_banner.offset_right = 300
	_turn_banner.visible = false
	add_child(_turn_banner)

	_status = _make_label(22, Color(0.9, 0.86, 0.78, 0.9))
	_status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_status.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	_status.offset_top = _turn_banner.offset_top + 10
	_status.offset_bottom = _status.offset_top + 34
	_status.offset_left = -400
	_status.offset_right = 400
	add_child(_status)

	_score = _make_label(20, Color(0.9, 0.86, 0.78, 0.95))
	_score.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_score.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	_score.offset_left = -420
	_score.offset_right = -24
	_score.offset_top = 16
	add_child(_score)

	_build_end_panel()


func show_turn(on: bool) -> void:
	_turn_banner.visible = on


func show_status(text: String) -> void:
	_status.text = text


func update_tricks(names: Array, counts: Array) -> void:
	var lines: PackedStringArray = ["ALINAN EL"]
	for i in names.size():
		lines.append("%s: %d" % [names[i], counts[i]])
	_score.text = "\n".join(lines)


func show_round_end(names: Array, counts: Array) -> void:
	var lines: PackedStringArray = ["EL BİTTİ", ""]
	for i in names.size():
		lines.append("%s — %d el" % [names[i], counts[i]])
	_end_label.text = "\n".join(lines)
	_end_panel.visible = true


func hide_round_end() -> void:
	_end_panel.visible = false


func _build_end_panel() -> void:
	_end_panel = PanelContainer.new()
	var style := StyleBoxFlat.new()
	style.bg_color = PANEL_BG
	style.set_border_width_all(2)
	style.border_color = GOLD
	style.set_corner_radius_all(14)
	style.set_content_margin_all(28)
	_end_panel.add_theme_stylebox_override("panel", style)
	_end_panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_end_panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_end_panel.grow_vertical = Control.GROW_DIRECTION_BOTH
	_end_panel.visible = false
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 18)
	_end_panel.add_child(box)
	_end_label = _make_label(28, GOLD)
	_end_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box.add_child(_end_label)
	var button := Button.new()
	button.text = "YENİDEN DAĞIT"
	button.add_theme_font_size_override("font_size", 26)
	button.custom_minimum_size = Vector2(320, 64)
	button.pressed.connect(func(): restart_requested.emit())
	box.add_child(button)
	add_child(_end_panel)


func _make_label(font_size: int, color: Color) -> Label:
	var l := Label.new()
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", color)
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.85))
	l.add_theme_constant_override("outline_size", 8)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l
