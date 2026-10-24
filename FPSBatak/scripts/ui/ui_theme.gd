class_name UiTheme
extends RefCounted
## Oyunun ortak arayüz teması: koyu zemin + altın/bakır vurgular.
## Ana menü ve oyun içi HUD aynı görünsün diye tek yerde tanımlıdır.

const GOLD := Color(0.95, 0.77, 0.4)
const TEXT := Color(0.92, 0.88, 0.8)
const PANEL_BG := Color(0.06, 0.045, 0.035, 0.86)
const BUTTON_BG := Color(0.16, 0.11, 0.07, 0.95)
const BUTTON_HOVER := Color(0.32, 0.21, 0.1, 0.98)


static func make() -> Theme:
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


## Gölgeli (outline'lı) etiket.
static func label(font_size: int, color: Color = TEXT) -> Label:
	var l := Label.new()
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", color)
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.85))
	l.add_theme_constant_override("outline_size", 8)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


static func button(text: String, on_pressed: Callable, min_size: Vector2) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = min_size
	b.pressed.connect(on_pressed)
	return b
