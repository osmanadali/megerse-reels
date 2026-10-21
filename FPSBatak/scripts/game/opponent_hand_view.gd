class_name OpponentHandView
extends Node3D
## Rakibin elinde tuttuğu kapalı kartları yelpaze şeklinde gösterir.
##
## Bu düğüm karakterin "el" noktasına (HandAnchor) eklenir. Kartların yüzü
## rakibe (+Z), arkası oyuncuya bakar. Kart kimlikleri burada tutulmaz:
## rakibin ne tuttuğunu görsel katman bile bilmez, kart oynanınca açılır.

const FAN_STEP_DEG := 5.5
const FAN_RADIUS := 0.28
const CARD_SCALE := 0.55
## Kartların birbirine geçmemesi için her kartı biraz öne alırız.
const LAYER_OFFSET := 0.0012
const RELAYOUT_TIME := 0.15

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


## Yelpazedeki i. kartın bu düğüme göre dönüşümü.
func _slot_transform(i: int, n: int) -> Transform3D:
	var angle := deg_to_rad((i - (n - 1) * 0.5) * FAN_STEP_DEG)
	var pos := Vector3(sin(angle) * FAN_RADIUS, (cos(angle) - 1.0) * FAN_RADIUS, i * LAYER_OFFSET)
	# Yüz +Z'de rakibe baksın diye kartı Y ekseninde çevirmiyoruz; sadece yelpaze açısı.
	var b := Basis(Vector3.FORWARD, angle).scaled(Vector3.ONE * CARD_SCALE)
	return Transform3D(b, pos)
