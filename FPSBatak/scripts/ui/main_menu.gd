class_name MainMenu
extends CanvasLayer
## Ana menü ve duraklatma menüsü.
##
## Menü, arka planda dönen kahvehane sahnesinin üstüne çizilir: solda başlık ve
## butonlar, sağda seçilen bölümün paneli. Henüz hazır olmayan bölümler
## (Karakterler, Masalar) "Yakında" panelidir.

signal start_requested
signal resume_requested
signal main_menu_requested

const COLUMN_WIDTH := 460.0
const BUTTON_SIZE := Vector2(420, 68)

@export var faces: CardFaceRenderer

var _theme: Theme
var _main_root: Control
var _side_panel: PanelContainer
var _side_box: VBoxContainer
var _pause_panel: PanelContainer
var _pause_dim: ColorRect
var _settings := UserSettings.load_saved()


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS  # duraklatılmışken de çalışsın
	_theme = UiTheme.make()
	_build_main()
	_build_side_panel()
	_build_pause_panel()


func show_main() -> void:
	_main_root.visible = true
	_side_panel.visible = false
	_set_pause_visible(false)


func hide_all() -> void:
	_main_root.visible = false
	_side_panel.visible = false
	_set_pause_visible(false)


func show_pause() -> void:
	_side_panel.visible = false
	_set_pause_visible(true)


func _set_pause_visible(on: bool) -> void:
	_pause_dim.visible = on
	_pause_panel.visible = on


func is_pause_open() -> bool:
	return _pause_panel.visible


## Açık bir alt panel varsa kapatır; kapattıysa true döner (Esc için).
func close_side_panel() -> bool:
	if _side_panel.visible:
		_side_panel.visible = false
		return true
	return false


# --- Ana sütun -----------------------------------------------------------------

func _build_main() -> void:
	_main_root = Control.new()
	_main_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_main_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_main_root.theme = _theme
	add_child(_main_root)

	# Soldan sağa açılan karartma: yazılar okunur, sahne sağda görünür kalır.
	var shade := TextureRect.new()
	var grad := Gradient.new()
	grad.set_color(0, Color(0, 0, 0, 0.88))
	grad.set_color(1, Color(0, 0, 0, 0.0))
	var tex := GradientTexture2D.new()
	tex.gradient = grad
	tex.fill_to = Vector2(1, 0)
	shade.texture = tex
	shade.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	shade.stretch_mode = TextureRect.STRETCH_SCALE
	shade.set_anchors_preset(Control.PRESET_LEFT_WIDE)
	shade.offset_right = COLUMN_WIDTH * 2.0
	shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_main_root.add_child(shade)

	var col := VBoxContainer.new()
	col.set_anchors_preset(Control.PRESET_LEFT_WIDE)
	col.offset_left = 90
	col.offset_right = 90 + COLUMN_WIDTH
	col.alignment = BoxContainer.ALIGNMENT_CENTER
	col.add_theme_constant_override("separation", 12)
	_main_root.add_child(col)

	var title := UiTheme.label(92, UiTheme.GOLD)
	title.text = "FPS BATAK"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	col.add_child(title)
	var slogan := UiTheme.label(28)
	slogan.text = "MASAYA OTUR. KARTINI OYNA."
	slogan.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	col.add_child(slogan)
	var gap := Control.new()
	gap.custom_minimum_size = Vector2(0, 36)
	col.add_child(gap)

	var start := _menu_button("OYUNA BAŞLA", func(): start_requested.emit())
	start.add_theme_font_size_override("font_size", 34)
	col.add_child(start)
	col.add_child(_menu_button("KARAKTERLER", _open_characters))
	col.add_child(_menu_button("MASALAR", _open_tables))
	col.add_child(_menu_button("KARTLAR", _open_cards))
	col.add_child(_menu_button("İSTATİSTİKLER", _open_stats))
	col.add_child(_menu_button("AYARLAR", _open_settings))
	if not OS.has_feature("mobile") and not OS.has_feature("web"):
		col.add_child(_menu_button("ÇIKIŞ", func(): get_tree().quit()))

	var footer := UiTheme.label(16, Color(UiTheme.TEXT, 0.55))
	footer.text = "Prototip · Tamamen offline · Gerçek para yok"
	footer.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT)
	footer.offset_left = 90
	footer.offset_top = -44
	footer.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	_main_root.add_child(footer)


func _menu_button(text: String, on_pressed: Callable) -> Button:
	var b := UiTheme.button(text, on_pressed, BUTTON_SIZE)
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.add_theme_font_size_override("font_size", 28)
	return b


# --- Sağ panel (alt bölümler) ----------------------------------------------------

func _build_side_panel() -> void:
	_side_panel = PanelContainer.new()
	_side_panel.theme = _theme
	_side_panel.set_anchors_preset(Control.PRESET_CENTER_RIGHT)
	_side_panel.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	_side_panel.grow_vertical = Control.GROW_DIRECTION_BOTH
	_side_panel.offset_right = -110
	_side_panel.custom_minimum_size = Vector2(640, 0)
	_side_panel.visible = false
	_side_box = VBoxContainer.new()
	_side_box.add_theme_constant_override("separation", 14)
	_side_panel.add_child(_side_box)
	add_child(_side_panel)


## Sağ paneli başlık + içerikle açar. `fill` içeriği kutuya ekleyen fonksiyondur.
func _open_side(title_text: String, fill: Callable) -> void:
	for c in _side_box.get_children():
		c.queue_free()
	var title := UiTheme.label(40, UiTheme.GOLD)
	title.text = title_text
	_side_box.add_child(title)
	fill.call(_side_box)
	var close := UiTheme.button("KAPAT", func(): _side_panel.visible = false, Vector2(220, 56))
	close.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	_side_box.add_child(close)
	_side_panel.visible = true


func _text_lines(box: VBoxContainer, lines: Array, size := 24) -> void:
	for line in lines:
		var l := UiTheme.label(size)
		l.text = line
		box.add_child(l)


func _open_characters() -> void:
	_open_side("KARAKTERLER", func(box: VBoxContainer):
		_text_lines(box, ["YAKINDA", ""], 28)
		_text_lines(box, [
			"Dinozor · Kurt · Tilki · Ayı · Robot",
			"Goblin · Ork · Vampir · Korsan · Ejderha",
			"Uzaylı · Ninja · Canavar",
			"",
			"Her rakibin kendi kişiliği, ihale tarzı",
			"ve masadaki tepkileri olacak.",
		], 22))


func _open_tables() -> void:
	_open_side("MASALAR", func(box: VBoxContainer):
		_text_lines(box, ["✔  Gece Kahvehanesi", ""], 28)
		_text_lines(box, [
			"YAKINDA:",
			"Modern Kafe · Korsan Gemisi · Dinozor Mağarası",
			"Uzay Gemisi · Orta Çağ Tavernası",
			"Korku Tavernası · Cyberpunk Masa",
		], 22))


func _open_cards() -> void:
	_open_side("KARTLAR", func(box: VBoxContainer):
		_text_lines(box, ["✔  Klasik Deste"], 28)
		if faces and faces.is_ready:
			var row := HBoxContainer.new()
			row.alignment = BoxContainer.ALIGNMENT_CENTER
			row.add_theme_constant_override("separation", 10)
			for id in [["S", 14], ["H", 13], ["D", 12], ["C", 11]]:
				var suit := {"S": CardData.Suit.SPADES, "H": CardData.Suit.HEARTS,
					"D": CardData.Suit.DIAMONDS, "C": CardData.Suit.CLUBS}[id[0]] as int
				var tr := TextureRect.new()
				tr.texture = faces.get_face(CardData.create(suit, id[1]))
				tr.custom_minimum_size = Vector2(128, 179)
				tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
				tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
				row.add_child(tr)
			var back := TextureRect.new()
			back.texture = faces.get_back()
			back.custom_minimum_size = Vector2(128, 179)
			back.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			back.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
			row.add_child(back)
			box.add_child(row)
		_text_lines(box, ["Yeni kart tasarımları yakında."], 22))


func _open_stats() -> void:
	_open_side("İSTATİSTİKLER", func(box: VBoxContainer):
		_text_lines(box, PlayerStats.load_from().summary_lines(), 24))


func _open_settings() -> void:
	_open_side("AYARLAR", func(box: VBoxContainer):
		var vol_label := UiTheme.label(24)
		box.add_child(vol_label)
		var slider := HSlider.new()
		slider.min_value = 0
		slider.max_value = 100
		slider.step = 5
		slider.custom_minimum_size = Vector2(480, 32)
		slider.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		slider.value = _settings.master_volume * 100.0
		vol_label.text = "Ses: %d%%" % slider.value
		slider.value_changed.connect(func(v: float):
			vol_label.text = "Ses: %d%%" % v
			_settings.master_volume = v / 100.0
			_settings.apply()
			_settings.save())
		box.add_child(slider)
		if not OS.has_feature("mobile") and not OS.has_feature("web"):
			var fs := CheckButton.new()
			fs.text = "Tam ekran"
			fs.add_theme_font_size_override("font_size", 24)
			fs.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
			fs.button_pressed = _settings.fullscreen
			fs.toggled.connect(func(on: bool):
				_settings.fullscreen = on
				_settings.apply()
				_settings.save())
			box.add_child(fs))


# --- Duraklatma ----------------------------------------------------------------

func _build_pause_panel() -> void:
	# Arkadaki oyunu karartır ve alttaki butonlara tıklanmasını engeller.
	_pause_dim = ColorRect.new()
	_pause_dim.color = Color(0, 0, 0, 0.78)
	_pause_dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	_pause_dim.mouse_filter = Control.MOUSE_FILTER_STOP
	_pause_dim.visible = false
	add_child(_pause_dim)
	_pause_panel = PanelContainer.new()
	_pause_panel.theme = _theme
	_pause_panel.set_anchors_preset(Control.PRESET_CENTER)
	_pause_panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_pause_panel.grow_vertical = Control.GROW_DIRECTION_BOTH
	_pause_panel.visible = false
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 14)
	_pause_panel.add_child(box)
	var title := UiTheme.label(40, UiTheme.GOLD)
	title.text = "DURAKLATILDI"
	box.add_child(title)
	box.add_child(UiTheme.button("DEVAM", _on_resume, Vector2(340, 64)))
	box.add_child(UiTheme.button("ANA MENÜ", func(): main_menu_requested.emit(), Vector2(340, 64)))
	if not OS.has_feature("mobile") and not OS.has_feature("web"):
		box.add_child(UiTheme.button("ÇIKIŞ", func(): get_tree().quit(), Vector2(340, 64)))
	add_child(_pause_panel)


func _on_resume() -> void:
	_set_pause_visible(false)
	resume_requested.emit()
