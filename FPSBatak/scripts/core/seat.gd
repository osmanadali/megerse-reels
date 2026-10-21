class_name Seat
extends RefCounted
## Masadaki koltuk düzeni (3 veya 4 kişi).
##
## Koltuk 0 her zaman SENsin (kameranın olduğu yer, masanın +Z tarafı).
## Oyun saat yönünün tersine, yani sağına doğru ilerler. Koltuklar masa
## etrafına eşit açılarla dizilir: 3 kişide rakipler sağ-ön ve sol-ön
## çaprazdadır, 4 kişide sağ, karşı ve sol.

const LOCAL_PLAYER := 0


## Sıradaki koltuk (saat yönünün tersi).
static func next(seat: int, count: int) -> int:
	return (seat + 1) % count


## Koltuğun masa merkezine göre yönü (radyan). 0 = oyuncu (+Z), artan açı sağa.
static func angle(seat: int, count: int) -> float:
	return TAU * seat / count


## Masa merkezinden koltuğa doğru yatay birim vektör.
static func direction(seat: int, count: int) -> Vector3:
	var a := angle(seat, count)
	return Vector3(sin(a), 0.0, cos(a))
