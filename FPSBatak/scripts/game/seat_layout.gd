class_name SeatLayout
extends Node3D
## Koltukları oyuncu sayısına göre masanın etrafına dizer ve rakipleri oturtur.
##
## Seat0 (oyuncu ve kamera) sahnede sabittir; diğer koltuklar çalışma anında
## eşit açılarla oluşturulur. Karakter sistemi geldiğinde burada
## OpponentPlaceholder yerine seçilen karakterin sahnesi kullanılacak.

@export var opponent_scene: PackedScene
## Koltukların masa merkezine uzaklığı (m).
@export var seat_radius := 1.0
@export var opponent_names: Array[String] = ["Rakip 1", "Rakip 2", "Rakip 3"]
@export var opponent_colors: Array[Color] = [
	Color(0.55, 0.2, 0.16), Color(0.2, 0.32, 0.55), Color(0.45, 0.42, 0.18)]

var _seats: Array[Node3D] = []
var _opponents := {}  # koltuk -> OpponentPlaceholder


## Koltukları kurar. `table_center` masanın dünya konumu.
func build(player_count: int, table_center: Vector3) -> void:
	_seats = [get_child(0)]  # Seat0_South
	for i in range(1, player_count):
		var seat := Marker3D.new()
		seat.name = "Seat%d" % i
		add_child(seat)
		var pos := table_center + Seat.direction(i, player_count) * seat_radius
		pos.y = 0.0
		seat.global_position = pos
		var look := table_center
		look.y = 0.0
		seat.look_at(look, Vector3.UP)  # yerel -Z masaya baksın
		var opp: OpponentPlaceholder = opponent_scene.instantiate()
		opp.display_name = opponent_names[(i - 1) % opponent_names.size()]
		opp.body_color = opponent_colors[(i - 1) % opponent_colors.size()]
		seat.add_child(opp)
		_seats.append(seat)
		_opponents[i] = opp


func get_seat(i: int) -> Node3D:
	return _seats[i]


## Koltuktaki rakip (oyuncunun kendi koltuğu için null).
func get_opponent(i: int) -> OpponentPlaceholder:
	return _opponents.get(i)
