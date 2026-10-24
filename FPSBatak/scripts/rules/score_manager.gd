class_name ScoreManager
extends RefCounted
## Toplam puanları tutar ve el sonu puanlarını hesaplar.
##
## Kural: ihaleyi alan ihalesini tutturursa aldığı el kadar artı, tutturamazsa
## (batarsa) ihale kadar eksi yazar. Diğer oyuncular aldıkları el kadar yazar;
## hiç el alamayan ise ihale kadar eksi yazar ("sıfır alan ihaleye batar").

var totals: Array[int] = []


func _init(player_count: int) -> void:
	for i in player_count:
		totals.append(0)


static func round_scores(bidder: int, bid: int, tricks: Array[int]) -> Array[int]:
	var out: Array[int] = []
	for seat in tricks.size():
		if seat == bidder:
			out.append(tricks[seat] if tricks[seat] >= bid else -bid)
		elif tricks[seat] == 0:
			out.append(-bid)
		else:
			out.append(tricks[seat])
	return out


## Eli işler ve bu elin puanlarını döndürür.
func apply_round(bidder: int, bid: int, tricks: Array[int]) -> Array[int]:
	var deltas := round_scores(bidder, bid, tricks)
	for i in deltas.size():
		totals[i] += deltas[i]
	return deltas
