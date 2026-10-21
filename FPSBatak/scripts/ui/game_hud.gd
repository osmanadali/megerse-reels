class_name GameHUD
extends CanvasLayer
## Oyun içi arayüz. Sade tutulur ve kartların önüne geçmez:
## karar panelleri elin hemen üstünde, masanın ön kısmında belirir.
## Koyu zemin + altın/bakır vurgular.

signal next_round_requested
signal start_requested(settings: MatchSettings)
signal new_game_requested
signal bid_chosen(amount: int)   # BidManager.PASS = pas
signal trump_chosen(suit: int)
signal bury_confirmed

const GOLD := Color(0.95, 0.77, 0.4)
const TEXT := Color(0.92, 0.88, 0.8)
const PANEL_BG := Color(0.06, 0.045, 0.035, 0.86)
const BUTTON_BG := Color(0.16, 0.11, 0.07, 0.95)
const BUTTON_HOVER := Color(0.32, 0.21, 0.1, 0.98)
## Karar panellerinin dikey konumu (ekran yüksekliğine oran, panelin altı).
const ACTION_BOTTOM_RATIO := 0.74

var hand: HandView
var _theme: Theme
var _turn_banner: Label
var _status: Label
var _info: Label
var _end_panel: PanelContainer
var _end_label: Label
var _bid_panel: PanelContainer
var _bid_title: Label
var _bid_sub: Label
var _bid_buttons: HFlowContainer
var _bury_panel: PanelContainer
var _bury_label: Label
var _bury_button: Button
var _bury_count := 4
var _trump_panel: PanelContainer
var _end_button: Button
var _setup_panel: PanelContainer
var _setup_settings: MatchSettings
var _match_panel: PanelContainer
var _match_label: Label


func _ready() -> void:
	_theme = _make_theme()
	hand = HandView.new()
	add_child(hand)
	move_child(hand, 0)  # el, diğer HUD öğelerinin altında
	hand.selection_changed.connect(_on_selection_changed)

	_turn_banner = _make_label(40, GOLD)
	_turn_banner.text = "SIRA SENDE"
	_place_above_hand(_turn_banner, 600, 56)
	_turn_banner.visible = false
	add_child(_turn_banner)

	_status = _make_label(22, Color(TEXT, 0.92))
	_place_above_hand(_status, 900, 34)
	add_child(_status)

	_info = _make_label(20, TEXT)
	# Üst orta: rakiplerin isimleriyle çakışmayan boş alan (pencere).
	_info.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_info.offset_left = -260
	_info.offset_right = 260
	_info.offset_top = 14
	add_child(_info)

	_build_bid_panel()
	_build_bury_panel()
	_build_trump_panel()
	_build_end_panel()
	_build_setup_panel()
	_build_match_panel()


# --- Genel ---------------------------------------------------------------------

func show_turn(on: bool) -> void:
	_turn_banner.visible = on


func show_status(text: String) -> void:
	_status.text = text


## Üst ortadaki bilgi: tur/hedef, ihale, koz, alınan eller ve toplam puan.
func update_info(header: String, names: Array, tricks: Array, totals: Array, bidder: int, bid: int,
		trump: int) -> void:
	var lines: PackedStringArray = [header]
	if bidder >= 0:
		lines.append("İHALE: %s — %d" % [names[bidder], bid])
	if trump >= 0:
		lines.append("KOZ: %s %s" % [CardData.SUIT_SYMBOLS[trump], CardData.SUIT_NAMES_TR[trump]])
	lines.append("")
	for i in names.size():
		lines.append("%s   el %d   puan %d" % [names[i], tricks[i], totals[i]])
	_info.text = "\n".join(lines)


# --- İhale ---------------------------------------------------------------------

## Oyuncuya ihale panelini gösterir. `valid` söylenebilecek değerler.
func show_bidding(valid: Array[int], current_text: String) -> void:
	_bid_sub.text = current_text
	for b in _bid_buttons.get_children():
		b.queue_free()
	_bid_buttons.add_child(_make_button("PAS", func(): _pick_bid(BidManager.PASS), Vector2(120, 64)))
	for v in valid:
		_bid_buttons.add_child(_make_button(str(v), func(): _pick_bid(v), Vector2(72, 64)))
	_bid_panel.visible = true


func _pick_bid(amount: int) -> void:
	_bid_panel.visible = false
	bid_chosen.emit(amount)


func _build_bid_panel() -> void:
	_bid_panel = _make_panel()
	var box := _panel_box(_bid_panel)
	_bid_title = _make_label(40, GOLD)
	_bid_title.text = "İHALE SENDE"
	box.add_child(_bid_title)
	_bid_sub = _make_label(22, TEXT)
	box.add_child(_bid_sub)
	_bid_buttons = HFlowContainer.new()
	_bid_buttons.alignment = FlowContainer.ALIGNMENT_CENTER
	_bid_buttons.custom_minimum_size = Vector2(820, 0)
	_bid_buttons.add_theme_constant_override("h_separation", 8)
	_bid_buttons.add_theme_constant_override("v_separation", 8)
	box.add_child(_bid_buttons)
	_add_action_panel(_bid_panel)


# --- Gömme ---------------------------------------------------------------------

func show_bury(count: int) -> void:
	_bury_count = count
	_on_selection_changed(0)
	_bury_panel.visible = true


func hide_bury() -> void:
	_bury_panel.visible = false


func _on_selection_changed(count: int) -> void:
	_bury_label.text = "GÖMECEĞİN %d KARTI SEÇ   (%d/%d)" % [_bury_count, count, _bury_count]
	_bury_button.disabled = count != _bury_count


func _build_bury_panel() -> void:
	_bury_panel = _make_panel()
	var box := _panel_box(_bury_panel)
	_bury_label = _make_label(28, GOLD)
	box.add_child(_bury_label)
	_bury_button = _make_button("GÖM", func(): bury_confirmed.emit(), Vector2(260, 64))
	box.add_child(_bury_button)
	_add_action_panel(_bury_panel)


# --- Koz -----------------------------------------------------------------------

func show_trump_choice() -> void:
	_trump_panel.visible = true


func _pick_trump(suit: int) -> void:
	_trump_panel.visible = false
	trump_chosen.emit(suit)


func _build_trump_panel() -> void:
	_trump_panel = _make_panel()
	var box := _panel_box(_trump_panel)
	var title := _make_label(36, GOLD)
	title.text = "KOZU SEÇ"
	box.add_child(title)
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 12)
	box.add_child(row)
	for suit in CardData.Suit.values():
		var label := "%s  %s" % [CardData.SUIT_SYMBOLS[suit], CardData.SUIT_NAMES_TR[suit]]
		var b := _make_button(label, func(): _pick_trump(suit), Vector2(170, 72))
		var red: bool = suit == CardData.Suit.HEARTS or suit == CardData.Suit.DIAMONDS
		b.add_theme_color_override("font_color", Color(1, 0.45, 0.4) if red else TEXT)
		row.add_child(b)
	_add_action_panel(_trump_panel)


# --- El sonu -------------------------------------------------------------------

func show_round_end(title: String, names: Array, tricks: Array, deltas: Array, totals: Array,
		button_text: String) -> void:
	var lines: PackedStringArray = [title, ""]
	for i in names.size():
		lines.append("%s — %d el   %+d   (toplam %d)" % [names[i], tricks[i], deltas[i], totals[i]])
	_end_label.text = "\n".join(lines)
	_end_button.text = button_text
	_end_panel.visible = true


func hide_round_end() -> void:
	_end_panel.visible = false


func _build_end_panel() -> void:
	_end_panel = _make_panel()
	_end_panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_end_panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_end_panel.grow_vertical = Control.GROW_DIRECTION_BOTH
	var box := _panel_box(_end_panel)
	_end_label = _make_label(28, GOLD)
	box.add_child(_end_label)
	_end_button = _make_button("SONRAKİ TUR", func(): next_round_requested.emit(), Vector2(320, 64))
	box.add_child(_end_button)
	add_child(_end_panel)


# --- Masa ayarları (maç başı) ----------------------------------------------------

## Maç başı ayar panelini gösterir; seçim `start_requested` ile döner.
func show_setup(current: MatchSettings) -> void:
	_setup_settings = current
	_setup_panel.visible = true
	# Kayıtlı seçimleri butonlara yansıt.
	for row in _setup_panel.find_children("Row*", "HBoxContainer", true, false):
		for b: Button in row.get_children():
			b.button_pressed = b.get_meta("value") == (
				current.rounds if row.name == "RowRounds" else current.target_score)


func _build_setup_panel() -> void:
	_setup_panel = _make_panel()
	_setup_panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_setup_panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_setup_panel.grow_vertical = Control.GROW_DIRECTION_BOTH
	var box := _panel_box(_setup_panel)
	var title := _make_label(54, GOLD)
	title.text = "FPS BATAK"
	box.add_child(title)
	var slogan := _make_label(22, TEXT)
	slogan.text = "Masaya Otur. Kartını Oyna."
	box.add_child(slogan)
	box.add_child(_option_row("TUR SAYISI", "RowRounds", MatchSettings.ROUND_OPTIONS,
		func(v: int): _setup_settings.rounds = v))
	box.add_child(_option_row("HEDEF PUAN", "RowTarget", MatchSettings.TARGET_OPTIONS,
		func(v: int): _setup_settings.target_score = v))
	var note := _make_label(18, Color(TEXT, 0.7))
	note.text = "Tur sayısı dolunca ya da biri hedef puana ulaşınca oyun biter."
	box.add_child(note)
	box.add_child(_make_button("MASAYA OTUR", _on_setup_confirmed, Vector2(340, 72)))
	add_child(_setup_panel)


func _on_setup_confirmed() -> void:
	_setup_panel.visible = false
	_setup_settings.save()
	start_requested.emit(_setup_settings)


## Başlık + tek seçimli buton satırı.
func _option_row(caption: String, row_name: String, values: Array[int], on_pick: Callable) -> VBoxContainer:
	var wrap := VBoxContainer.new()
	wrap.add_theme_constant_override("separation", 6)
	var label := _make_label(22, GOLD)
	label.text = caption
	wrap.add_child(label)
	var row := HBoxContainer.new()
	row.name = row_name
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 10)
	var group := ButtonGroup.new()
	for v in values:
		var b := _make_button(str(v), func(): on_pick.call(v), Vector2(96, 60))
		b.toggle_mode = true
		b.button_group = group
		b.set_meta("value", v)
		row.add_child(b)
	wrap.add_child(row)
	return wrap


# --- Maç sonu --------------------------------------------------------------------

func show_match_end(title: String, lines: Array[String]) -> void:
	_match_label.text = title + "\n\n" + "\n".join(lines)
	_match_panel.visible = true


func _build_match_panel() -> void:
	_match_panel = _make_panel()
	_match_panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_match_panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_match_panel.grow_vertical = Control.GROW_DIRECTION_BOTH
	var box := _panel_box(_match_panel)
	_match_label = _make_label(30, GOLD)
	box.add_child(_match_label)
	box.add_child(_make_button("YENİ OYUN", _on_new_game, Vector2(320, 68)))
	add_child(_match_panel)


func _on_new_game() -> void:
	_match_panel.visible = false
	new_game_requested.emit()


# --- Yardımcılar ----------------------------------------------------------------

## Karar panelini elin üstüne, yatayda ortalı yerleştirir.
func _add_action_panel(panel: PanelContainer) -> void:
	var vp_h := get_viewport().get_visible_rect().size.y
	panel.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	panel.grow_vertical = Control.GROW_DIRECTION_BEGIN
	panel.offset_bottom = -vp_h * (1.0 - ACTION_BOTTOM_RATIO)
	panel.offset_top = panel.offset_bottom
	add_child(panel)


func _place_above_hand(label: Label, width: float, height: float) -> void:
	var vp_h := get_viewport().get_visible_rect().size.y
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	label.offset_top = -vp_h * (1.0 - ACTION_BOTTOM_RATIO) - height
	label.offset_bottom = label.offset_top + height
	label.offset_left = -width * 0.5
	label.offset_right = width * 0.5


func _make_panel() -> PanelContainer:
	var p := PanelContainer.new()
	p.theme = _theme
	p.visible = false
	return p


func _panel_box(panel: PanelContainer) -> VBoxContainer:
	var box := VBoxContainer.new()
	box.alignment = BoxContainer.ALIGNMENT_CENTER
	box.add_theme_constant_override("separation", 14)
	panel.add_child(box)
	return box


func _make_button(text: String, on_pressed: Callable, min_size: Vector2) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = min_size
	b.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	b.pressed.connect(on_pressed)
	return b


func _make_label(font_size: int, color: Color) -> Label:
	var l := Label.new()
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", color)
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.85))
	l.add_theme_constant_override("outline_size", 8)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


func _make_theme() -> Theme:
	var t := Theme.new()
	var panel := StyleBoxFlat.new()
	panel.bg_color = PANEL_BG
	panel.set_border_width_all(2)
	panel.border_color = GOLD
	panel.set_corner_radius_all(14)
	panel.set_content_margin_all(22)
	t.set_stylebox("panel", "PanelContainer", panel)
	for state in ["normal", "hover", "pressed", "hover_pressed", "disabled", "focus"]:
		var sb := StyleBoxFlat.new()
		sb.bg_color = BUTTON_HOVER if state == "hover" else BUTTON_BG
		if state in ["pressed", "hover_pressed"]:  # seçili (toggle) buton
			sb.bg_color = Color(0.55, 0.36, 0.12, 0.98)
		sb.set_border_width_all(3 if state in ["pressed", "hover_pressed"] else 2)
		sb.border_color = GOLD if state != "disabled" else Color(GOLD, 0.3)
		sb.set_corner_radius_all(10)
		sb.set_content_margin_all(8)
		if state == "focus":
			sb.draw_center = false
		t.set_stylebox(state, "Button", sb)
	t.set_font_size("font_size", "Button", 28)
	t.set_color("font_color", "Button", TEXT)
	t.set_color("font_hover_color", "Button", GOLD)
	t.set_color("font_pressed_color", "Button", Color(1, 0.95, 0.85))
	t.set_color("font_hover_pressed_color", "Button", Color(1, 0.95, 0.85))
	t.set_color("font_disabled_color", "Button", Color(TEXT, 0.35))
	return t
