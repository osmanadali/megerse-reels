class_name TwoRowLayout
extends RefCounted
## Bir eldeki kartları İKİ SIRAYA dizmenin ortak hesabı (yalnızca görsel düzen).
##
## Hem oyuncunun 2D eli (HandView) hem rakiplerin 3D eli (OpponentHandView)
## bu sınıfı kullanır; her görünüm sonucu kendi ölçüsüne (piksel / metre) çevirir.
##
## - Üst sıra büyük yarıdır: 13 → 7+6, 16 → 8+8, 5 → 3+2, 1 → 1+0.
## - Kart sırası korunur: ilk ⌈n/2⌉ kart üst sırada soldan sağa, kalanlar alt
##   sırada. Alt sıra önde (üstte çizilir), üst sıra arkada ve yukarıdadır.
## - Sıralar eşitse alt sıra yarım adım kaydırılır (tuğla dizilimi), böylece
##   iki sıra tek blok gibi durur ve üst sıranın köşeleri görünür kalır.


## (üst sıra kart sayısı, alt sıra kart sayısı)
static func row_counts(n: int) -> Vector2i:
	var top := (n + 1) >> 1
	return Vector2i(top, n - top)


## n kartlık elde i. kartın yeri:
##   row    : 0 = üst (arka), 1 = alt (ön)
##   index  : sıra içindeki sırası (0'dan)
##   offset : yatay konum, kart adımı biriminde, blok ortasına göre
##            (görünüm bunu kendi adımıyla çarpar)
##   center : sıra ortasına göre konum (yelpaze açısı ve eğrilik için)
static func slot(i: int, n: int) -> Dictionary:
	var rows := row_counts(n)
	var bottom := i >= rows.x
	var j := i - rows.x if bottom else i
	var m := rows.y if bottom else rows.x
	var center := j - (m - 1) * 0.5
	var offset := center
	if bottom and rows.x == rows.y:
		offset += 0.5
	return {"row": 1 if bottom else 0, "index": j, "offset": offset, "center": center}


## Bloğun yatay sınırları (kart adımı biriminde, kart merkezleri): Vector2(min, max).
## Genişlik = (max - min) × adım + kart genişliği.
static func extent(n: int) -> Vector2:
	if n <= 0:
		return Vector2.ZERO
	var rows := row_counts(n)
	var lo := -(rows.x - 1) * 0.5
	var hi := -lo
	if rows.y > 0:
		var shift := 0.5 if rows.x == rows.y else 0.0
		lo = minf(lo, -(rows.y - 1) * 0.5 + shift)
		hi = maxf(hi, (rows.y - 1) * 0.5 + shift)
	return Vector2(lo, hi)
