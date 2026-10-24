class_name OpponentHandView
extends Node3D
## Rakibin elinde tuttuğu kapalı kartları İKİ SIRA hâlinde gösterir.
##
## Tek sıra 13–16 kart, mobil ekranda karakterin yüzünü ve gövdesini kapatan
## geniş bir yelpaze oluşturuyordu. İki sıra (13 → 7+6, 16 → 8+8) aynı kartları
## yarı genişlikte tutar: karakter, eller ve kartlar birlikte okunur. Üst sıra
## arkada ve biraz yukarıda, alt sıra öndedir; kartlar hafif üst üste biner ve
## sıra içinde küçük açı farklarıyla açılır. Yalnızca görsel düzen: kart
## sayısı ve oyun mantığı değişmez.
##
## Bu düğüm karakterin "el" noktasına (HandAnchor) eklenir. Kartların yüzü
## rakibe (+Z), arkası oyuncuya bakar. Kart kimlikleri burada tutulmaz:
## rakibin ne tuttuğunu görsel katman bile bilmez, kart oynanınca açılır.

const CARD_SCALE := 0.55
## Sıra içinde kartlar arası yatay adım (m): kart genişliğinin ~%45'i, yani
## kartlar yarıdan fazla üst üste biner ama kenarları okunur.
const ROW_STEP := 0.032
## Sıra içindeki küçük yelpaze açısı (derece/kart) ve kenarlara doğru düşüş.
const ROW_FAN_DEG := 2.6
const ROW_CURVE := 0.55
## Üst sıranın yüksekliği ve alt sıranın oyuncuya doğru öne alınması.
const ROW_GAP := 0.048
const ROW_DEPTH := 0.006
## Kartların birbirine geçmemesi için her kartı biraz öne alırız.
const LAYER_OFFSET := 0.0012
const RELAYOUT_TIME := 0.15

## Bir kart oynanmak üzere elden çekildi (karakterin kısa el jesti için; görsel).
signal card_taken

var _cards: Array[Card3D] = []


## Desteden uçarak gelen kapalı kartı ele ekler.
func receive(card3d: Card3D, flight_time: float) -> void:
	card3d.reparent(self, true)
	_cards.append(card3d)
	var index := _cards.size() - 1
	card3d.move_to(global_transform * _slot_transform(index, _cards.size()), flight_time, 0.08)
	_relayout(index)


## Elden bir kart çeker (oynamak için). Kart dünya konumunu korur.
func take_card(new_parent: Node3D) -> Card3D:
	if _cards.is_empty():
		return null
	var index := _cards.size() / 2
	var card3d := _cards[index]
	_cards.remove_at(index)
	card3d.reparent(new_parent, true)
	_relayout(-1)
	card_taken.emit()
	return card3d


func count() -> int:
	return _cards.size()


func clear() -> void:
	for c in _cards:
		c.queue_free()
	_cards.clear()


func _relayout(skip_index: int) -> void:
	for i in _cards.size():
		if i == skip_index:
			continue
		var t := create_tween()
		t.tween_property(_cards[i], "transform", _slot_transform(i, _cards.size()), RELAYOUT_TIME)


## Eldeki i. kartın bu düğüme göre dönüşümü (iki sıralı düzen, TwoRowLayout).
func _slot_transform(i: int, n: int) -> Transform3D:
	var sl := TwoRowLayout.slot(i, n)
	var ext := TwoRowLayout.extent(n)
	var bottom: bool = sl.row == 1
	var c: float = sl.center
	# Blok, tuğla kaydırmasından bağımsız olarak elin ortasında kalsın.
	var x: float = (sl.offset - (ext.x + ext.y) * 0.5) * ROW_STEP
	var single_row := TwoRowLayout.row_counts(n).y == 0   # tek kart: alt sıra yüksekliğinde
	var y := (0.0 if bottom or single_row else ROW_GAP) - c * c * ROW_CURVE * 0.0015
	# Yüzler +Z'de rakibe bakar; alt sıra oyuncuya (−Z) doğru biraz öndedir.
	var z: float = sl.index * LAYER_OFFSET - (ROW_DEPTH if bottom else 0.0)
	var angle := deg_to_rad(c * ROW_FAN_DEG)
	var b := Basis(Vector3.FORWARD, angle).scaled(Vector3.ONE * CARD_SCALE)
	return Transform3D(b, Vector3(x, y, z))
