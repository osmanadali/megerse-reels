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


## Risk iştahı: tahmini löve sayısına eklenir. Kişilikler (agresif dinozor,
## temkinli tilki...) ileride bu değeri değiştirecek.
var aggression := 0.0
## Yerden gelecek kartların ortalama katkısı (kart başına löve).
const KITTY_TRICK_VALUE := 0.2


# --- İhale ---------------------------------------------------------------------

## Söylenecek ihaleyi döndürür; BidManager.PASS (0) = pas.
## `valid` artan sıradadır. AI yalnızca kendi elini bilir.
func choose_bid(hand: Array[CardData], valid: Array[int], kitty_size: int) -> int:
	if valid.is_empty():
		return BidManager.PASS
	var estimate := estimate_tricks(hand) + kitty_size * KITTY_TRICK_VALUE + aggression
	if difficulty == Difficulty.EASY:
		estimate += _rng.randf_range(-1.5, 1.5)
	var target := int(floor(estimate))
	return valid[0] if valid[0] <= target else BidManager.PASS


## Elin en iyi koz seçimiyle kaç löve alabileceğine dair kaba tahmin.
static func estimate_tricks(hand: Array[CardData]) -> float:
	var best := 0.0
	for suit in CardData.Suit.values():
		best = max(best, _strength_with_trump(hand, suit))
	return best


## Koz olarak en güçlü takım.
static func choose_trump(hand: Array[CardData]) -> int:
	var best_suit: int = CardData.Suit.SPADES
	var best := -1.0
	for suit in CardData.Suit.values():
		var s := _strength_with_trump(hand, suit)
		if s > best:
			best = s
			best_suit = suit
	return best_suit


## Gömülecek kartlar: kozu ve Asları korur; kısa takımları boşaltmaya,
## olmazsa en küçük kartlardan kurtulmaya çalışır.
static func choose_bury(hand: Array[CardData], count: int) -> Array[CardData]:
	var trump := choose_trump(hand)
	var lengths := {}
	for c in hand:
		lengths[c.suit] = lengths.get(c.suit, 0) + 1
	var candidates: Array[CardData] = hand.filter(
		func(c: CardData): return c.suit != trump and c.rank != CardData.Rank.ACE)
	if candidates.size() < count:
		candidates = hand.duplicate()
	candidates.sort_custom(func(a: CardData, b: CardData):
		if lengths[a.suit] != lengths[b.suit]:
			return lengths[a.suit] < lengths[b.suit]
		return a.rank < b.rank)
	return candidates.slice(0, count)


static func _strength_with_trump(hand: Array[CardData], trump: int) -> float:
	var by_suit := {}
	for c in hand:
		if not by_suit.has(c.suit):
			by_suit[c.suit] = []
		by_suit[c.suit].append(c.rank)
	var total := 0.0
	for suit in by_suit:
		var ranks: Array = by_suit[suit]
		var n := ranks.size()
		if suit == trump:
			for r in ranks:
				total += {14: 1.0, 13: 0.9, 12: 0.7, 11: 0.5}.get(r, 0.0)
			total += max(0, n - 3) * 0.9  # uzun kozun fazlası löve getirir
		else:
			if ranks.has(CardData.Rank.ACE):
				total += 1.0
			if ranks.has(CardData.Rank.KING) and n >= 2:
				total += 0.75
			if ranks.has(CardData.Rank.QUEEN) and n >= 3:
				total += 0.4
	return total


# --- Kart oynama ---------------------------------------------------------------

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
