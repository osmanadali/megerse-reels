class_name TableLayout
extends RefCounted
## Masa üstündeki konumlar (oyuncu sayısına göre hesaplanır).
##
## - Löve yuvaları: her oyuncunun kartı kendi oturduğu yöne bakan yuvaya iner.
##   Merkez biraz ileri kaydırılmıştır ki oyuncunun kartı elinin arkasında kalmasın.
## - Löve yığınları ve gömü yeri: her oyuncunun önünde, iki yanında.

const TRICK_CENTER_OFFSET := Vector3(0, 0, -0.08)
const TRICK_RADIUS := 0.16
const PILE_RADIUS := 0.44
const PILE_ANGLE_OFFSET := deg_to_rad(24.0)
const DECK_TOWARD_DEALER := 0.42

var center: Vector3
var player_count: int


func _init(p_center: Vector3, p_player_count: int) -> void:
	center = p_center
	player_count = p_player_count


func trick_slot(seat: int) -> Vector3:
	return center + TRICK_CENTER_OFFSET + Seat.direction(seat, player_count) * TRICK_RADIUS


## Yerdeki (gömü için açılacak) kartların merkezi.
func kitty_spot() -> Vector3:
	return center + TRICK_CENTER_OFFSET


## Kazanılan lövelerin yığını: oyuncunun sağ-önünde.
func pile_spot(seat: int) -> Vector3:
	return center + _dir(Seat.angle(seat, player_count) + PILE_ANGLE_OFFSET) * PILE_RADIUS


## Gömülen kartlar: oyuncunun sol-önünde.
func bury_spot(seat: int) -> Vector3:
	return center + _dir(Seat.angle(seat, player_count) - PILE_ANGLE_OFFSET) * PILE_RADIUS


func deck_spot(dealer: int) -> Vector3:
	return center + Seat.direction(dealer, player_count) * PILE_RADIUS * DECK_TOWARD_DEALER * 2.0


## Koltuğa göre masa üstü dönüş açısı (kartların o oyuncuya hizalanması için).
func seat_yaw(seat: int) -> float:
	return Seat.angle(seat, player_count)


static func _dir(a: float) -> Vector3:
	return Vector3(sin(a), 0.0, cos(a))
