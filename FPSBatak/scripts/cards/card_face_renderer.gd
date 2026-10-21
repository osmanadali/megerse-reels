class_name CardFaceRenderer
extends Node
## 52 kart yüzü ve kart arkası için dokuları oyun açılışında bir kez üretir.
##
## Harici görsel dosyası gerektirmez. Bir CardData'nın `face_texture` alanı
## doluysa o kullanılır, böylece ileride hazır bir deste teması bu sınıfa
## dokunmadan eklenebilir. Dokular hem 2D eldeki kartlarda hem 3D masadaki
## kartlarda ortak kullanılır.

signal textures_ready

## Kart en-boy oranı gerçek iskambil kartıyla aynı (63x88 mm).
const FACE_SIZE := Vector2i(256, 358)

var _faces := {}            # kart kimliği -> Texture2D
var _back: Texture2D
var is_ready := false


func get_face(card: CardData) -> Texture2D:
	if card.face_texture:
		return card.face_texture
	return _faces.get(card.get_id())


func get_back() -> Texture2D:
	return _back


## Dokuları üretir. Her kart için bir SubViewport aynı karede çizilir,
## görüntüleri alınır ve viewport'lar silinir.
func build() -> void:
	if DisplayServer.get_name() == "headless":
		# Başsız çalışmada (testler) hiç kare çizilmez; frame_post_draw beklemek
		# sonsuza kadar sürer. Görüntüsüz yer tutucu dokularla hemen hazır ol.
		for s in CardData.Suit.values():
			for r in CardData.Rank.values():
				_faces[CardData.create(s, r).get_id()] = PlaceholderTexture2D.new()
		_back = PlaceholderTexture2D.new()
		is_ready = true
		textures_ready.emit.call_deferred()
		return
	var jobs := {}  # kimlik -> SubViewport
	for s in CardData.Suit.values():
		for r in CardData.Rank.values():
			var card := CardData.create(s, r)
			jobs[card.get_id()] = _make_viewport(_CardCanvas.new(card))
	var back_vp := _make_viewport(_CardCanvas.new(null))

	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw

	for id in jobs:
		_faces[id] = _grab(jobs[id])
	_back = _grab(back_vp)
	is_ready = true
	textures_ready.emit()


func _make_viewport(canvas: Control) -> SubViewport:
	var vp := SubViewport.new()
	vp.size = FACE_SIZE
	vp.transparent_bg = true
	vp.render_target_update_mode = SubViewport.UPDATE_ONCE
	canvas.size = FACE_SIZE
	vp.add_child(canvas)
	add_child(vp)
	return vp


func _grab(vp: SubViewport) -> Texture2D:
	var img := vp.get_texture().get_image()
	vp.queue_free()
	if img == null:  # başsız (headless) çalışmada görüntü alınamaz
		return PlaceholderTexture2D.new()
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)


## Tek bir kartı (veya arkasını) çizen iç sınıf.
class _CardCanvas extends Control:
	const PAPER := Color(0.98, 0.965, 0.92)
	const RED := Color(0.78, 0.07, 0.1)
	const BLACK := Color(0.08, 0.08, 0.1)
	const GOLD := Color(0.83, 0.65, 0.3)
	const CORNER_RADIUS := 18
	const INDEX_RANK_SIZE := 70
	const INDEX_SUIT_SIZE := 54
	const PIP_SIZE := 52
	## Sayı kartlarındaki semboller için (x, y) konumları, 0..1 arası.
	## y > 0.5 olanlar ters çizilir (gerçek kartlardaki gibi).
	const PIP_LAYOUTS := {
		2: [[0.5, 0.0], [0.5, 1.0]],
		3: [[0.5, 0.0], [0.5, 0.5], [0.5, 1.0]],
		4: [[0, 0], [1, 0], [0, 1], [1, 1]],
		5: [[0, 0], [1, 0], [0.5, 0.5], [0, 1], [1, 1]],
		6: [[0, 0], [1, 0], [0, 0.5], [1, 0.5], [0, 1], [1, 1]],
		7: [[0, 0], [1, 0], [0.5, 0.25], [0, 0.5], [1, 0.5], [0, 1], [1, 1]],
		8: [[0, 0], [1, 0], [0.5, 0.25], [0, 0.5], [1, 0.5], [0.5, 0.75], [0, 1], [1, 1]],
		9: [[0, 0], [1, 0], [0, 0.333], [1, 0.333], [0.5, 0.5], [0, 0.667], [1, 0.667], [0, 1], [1, 1]],
		10: [[0, 0], [1, 0], [0.5, 0.167], [0, 0.333], [1, 0.333], [0, 0.667], [1, 0.667], [0.5, 0.833], [0, 1], [1, 1]],
	}
	## Sembollerin yerleştiği iç alan (piksel).
	const PIP_AREA := Rect2(82, 62, 92, 234)

	var card: CardData
	var font: Font

	func _init(p_card: CardData) -> void:
		card = p_card
		font = ThemeDB.fallback_font

	func _draw() -> void:
		if card == null:
			_draw_back()
			return
		var ink := RED if card.is_red() else BLACK
		_draw_paper()
		_draw_index(ink)
		draw_set_transform(size, PI, Vector2.ONE)  # alt sağ köşe: 180° döndürülmüş
		_draw_index(ink)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
		if card.rank == CardData.Rank.ACE:
			_draw_centered(card.get_suit_symbol(), size * 0.5, 170, ink)
		elif card.rank >= CardData.Rank.JACK:
			_draw_court(ink)
		else:
			_draw_pips(ink)

	func _draw_paper() -> void:
		var box := StyleBoxFlat.new()
		box.bg_color = PAPER
		box.set_corner_radius_all(CORNER_RADIUS)
		box.set_border_width_all(2)
		box.border_color = Color(0.55, 0.52, 0.47)
		draw_style_box(box, Rect2(Vector2.ZERO, size))

	## Sol üst köşe: büyük değer + sembol. Elde kartlar üst üste bindiğinde
	## görünen kısım burası olduğu için bilerek büyük tutuldu.
	func _draw_index(ink: Color) -> void:
		_draw_centered(card.get_rank_label(), Vector2(36, 46), INDEX_RANK_SIZE, ink, 60)
		_draw_centered(card.get_suit_symbol(), Vector2(36, 104), INDEX_SUIT_SIZE, ink)

	func _draw_pips(ink: Color) -> void:
		for p in PIP_LAYOUTS[int(card.rank)]:
			var pos := PIP_AREA.position + Vector2(p[0], p[1]) * PIP_AREA.size
			if p[1] > 0.5:
				draw_set_transform(pos, PI, Vector2.ONE)
				_draw_centered(card.get_suit_symbol(), Vector2.ZERO, PIP_SIZE, ink)
				draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
			else:
				_draw_centered(card.get_suit_symbol(), pos, PIP_SIZE, ink)

	## Vale/Kız/Papaz: çerçeveli büyük harf.
	func _draw_court(ink: Color) -> void:
		var frame := Rect2(70, 56, size.x - 140, size.y - 112)
		var box := StyleBoxFlat.new()
		box.bg_color = ink.lerp(PAPER, 0.88)
		box.set_border_width_all(4)
		box.border_color = GOLD
		box.set_corner_radius_all(8)
		draw_style_box(box, frame)
		var c := frame.get_center()
		_draw_centered(card.get_rank_label(), c + Vector2(0, -22), 110, ink)
		_draw_centered(card.get_suit_symbol(), c + Vector2(0, 66), 58, ink)

	func _draw_back() -> void:
		var box := StyleBoxFlat.new()
		box.bg_color = Color(0.3, 0.05, 0.06)
		box.set_corner_radius_all(CORNER_RADIUS)
		box.set_border_width_all(10)
		box.border_color = PAPER
		draw_style_box(box, Rect2(Vector2.ZERO, size))
		var inner := Rect2(Vector2(20, 20), size - Vector2(40, 40))
		var step := 22.0
		var line_col := Color(GOLD, 0.35)
		var x := -inner.size.y
		while x < inner.size.x:  # çapraz kafes deseni
			draw_line(inner.position + Vector2(x, 0), inner.position + Vector2(x + inner.size.y, inner.size.y), line_col, 2)
			draw_line(inner.position + Vector2(x + inner.size.y, 0), inner.position + Vector2(x, inner.size.y), line_col, 2)
			x += step
		var frame := StyleBoxFlat.new()
		frame.draw_center = false
		frame.set_border_width_all(3)
		frame.border_color = GOLD
		frame.set_corner_radius_all(10)
		draw_style_box(frame, inner)
		_draw_centered("♠", size * 0.5 + Vector2(0, -18), 96, GOLD)
		_draw_centered("BATAK", size * 0.5 + Vector2(0, 62), 34, GOLD)

	## Metni verilen merkez noktaya ortalar. `max_width` verilirse sığdırır ("10" için).
	func _draw_centered(text: String, center: Vector2, font_size: int, color: Color,
			max_width: float = 0.0) -> void:
		var w := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x
		if max_width > 0.0 and w > max_width:
			font_size = int(font_size * max_width / w)
			w = font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x
		var ascent := font.get_ascent(font_size)
		var descent := font.get_descent(font_size)
		var baseline := center + Vector2(-w * 0.5, (ascent - descent) * 0.5)
		draw_string(font, baseline, text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, color)
