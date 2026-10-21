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


## Risk iştahı: beklenen löve tahminine eklenen kaydırma (şu an 0). Kişilikler
## (agresif dinozor, temkinli tilki...) ileride bu değeri değiştirecek.
var aggression := 0.0


# --- İhale ---------------------------------------------------------------------
# Karar zinciri BidStrategy'de: el analizi → beklenen löve → başarı olasılığı
# → ihale durumu → son teklif. Bu sınıf yalnızca oyuncuya özgü ayarları
# (zorluk, kişilik) ekler.

## İhale durumunu bilerek teklif seçer; BidManager.PASS (0) = pas.
func choose_bid_in_context(hand: Array[CardData], ctx: BidContext) -> int:
	return BidStrategy.decide(hand, ctx, _mu_shift()).bid


## Eski/basit API: yalnızca geçerli teklifler bilinirken. `kitty_size` > 0 ise
## gömmeli mod kuralları varsayılır.
func choose_bid(hand: Array[CardData], valid: Array[int], kitty_size: int) -> int:
	if valid.is_empty():
		return BidManager.PASS
	var rules := GameRules.buried_bidding() if kitty_size > 0 else GameRules.standard_bidding()
	return choose_bid_in_context(hand, BidContext.minimal(rules, valid))


## Koz olarak en çok löve getireceği tahmin edilen takım. `rules` verilmezse
## el büyüklüğünden mod çıkarılır (16 kart: gömmeli, aksi halde normal).
static func choose_trump(hand: Array[CardData], rules: GameRules = null) -> int:
	if rules == null:
		rules = GameRules.buried_bidding() if hand.size() == GameRules.buried_bidding().cards_per_player \
			else GameRules.standard_bidding()
	return TrickEstimator.best(hand, rules).trump


func _mu_shift() -> float:
	var shift := aggression
	if difficulty == Difficulty.EASY:
		shift += _rng.randf_range(-1.5, 1.5)
	return shift


## Gömülecek kartlar: kozu ve Asları korur; kısa takımları boşaltmaya,
## olmazsa en küçük kartlardan kurtulmaya çalışır. Gömme kozdan önce
## yapıldığı için AI söyleyeceği kozu (`trump`) önceden belirler.
static func choose_bury(hand: Array[CardData], count: int, trump: int) -> Array[CardData]:
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
