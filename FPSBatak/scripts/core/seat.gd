class_name Seat
extends RefCounted
## Masadaki koltuk düzeni.
##
## Oyun saat yönünün tersine (sağa doğru) ilerler:
##   0 = SEN (güney, kameranın olduğu yer)
##   1 = SAĞ (doğu, +X)
##   2 = KARŞI (kuzey, -Z)
##   3 = SOL (batı, -X)
## Kurallar yalnızca indeksleri bilir; dünyadaki konumlar Main sahnesindeki
## Seats/* marker düğümlerinden okunur.

enum Position { SOUTH = 0, EAST = 1, NORTH = 2, WEST = 3 }

const COUNT := 4
const LOCAL_PLAYER := Position.SOUTH

const NAMES_TR := {
	Position.SOUTH: "Sen",
	Position.EAST: "Sağ",
	Position.NORTH: "Karşı",
	Position.WEST: "Sol",
}


## Sıradaki koltuk (saat yönünün tersi).
static func next(seat: int) -> int:
	return (seat + 1) % COUNT
