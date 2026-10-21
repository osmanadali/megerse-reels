class_name AIPlayer
extends RefCounted
## Bilgisayar rakibin karar verme mantığı.
##
## Hile yok: AI yalnızca kendi elini, oynayabileceği kartları ve masaya açık
## oynanmış kartları görür. Başka oyuncuların ellerine hiçbir referansı yoktur.
## Zorluk seviyeleri ve kişilikler ileride bu sınıfın stratejisini değiştirecek.

enum Difficulty { EASY, NORMAL, HARD, MASTER }

var seat: int
var difficulty: Difficulty
var _rng := RandomNumberGenerator.new()


func _init(p_seat: int, p_difficulty: Difficulty = Difficulty.NORMAL) -> void:
	seat = p_seat
	difficulty = p_difficulty
	_rng.randomize()


## `legal` içinden oynanacak kartı seçer. `trick` masadaki açık kartlardır.
func choose_card(legal: Array[CardData], trick: Array[CardData], trump: int) -> CardData:
	assert(not legal.is_empty())
	if difficulty == Difficulty.EASY:
		return legal[_rng.randi_range(0, legal.size() - 1)]
	if trick.is_empty():
		return _choose_lead(legal)
	return _choose_follow(legal, trick, trump)


## Açarken: elinde As varsa onu oyna (büyük ihtimalle alır), yoksa en küçük kartı.
func _choose_lead(legal: Array[CardData]) -> CardData:
	for c in legal:
		if c.rank == CardData.Rank.ACE:
			return c
	return _lowest(legal)


## Uyarken: löveyi alabiliyorsan alabilen en küçük kartla al, alamıyorsan en küçüğü at.
func _choose_follow(legal: Array[CardData], trick: Array[CardData], trump: int) -> CardData:
	var current_best: CardData = trick[BatakRules.trick_winner(trick, trump)]
	var led_suit: int = trick[0].suit
	var winners: Array[CardData] = legal.filter(
		func(c: CardData): return BatakRules.beats(c, current_best, led_suit, trump))
	if not winners.is_empty():
		return _lowest(winners)
	return _lowest(legal)


static func _lowest(cards: Array[CardData]) -> CardData:
	var best: CardData = cards[0]
	for c in cards:
		if c.rank < best.rank:
			best = c
	return best
