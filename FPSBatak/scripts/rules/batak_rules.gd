class_name BatakRules
extends RefCounted
## Batak el (löve) kuralları — saf fonksiyonlar, görselden ve AI'dan bağımsız.
##
## Uygulanan standart kurallar:
## - Yerden açarken koz, koz kırılmadan açılamaz (elde sadece koz yoksa).
## - Açılan takıma uymak zorunludur.
## - Uyarken, masada koz yoksa ve elinde daha büyüğü varsa yükseltmek zorunludur.
## - Açılan takım yoksa koz atmak zorunludur; masada koz varsa ve
##   yükseltebiliyorsan daha büyük koz atmalısın.
## - Koz da yoksa istediğin kartı atabilirsin.

## Yükseltme zorunluluğu. İleride oda/kural ayarlarından değiştirilebilir.
const MUST_RAISE := true


## `hand` elindeki kartlardan, masadaki `trick` (oynanma sırasıyla) durumunda
## oynanabilecek kartları döndürür.
static func legal_cards(hand: Array[CardData], trick: Array[CardData], trump: int,
		trump_broken: bool) -> Array[CardData]:
	if hand.is_empty():
		return []
	if trick.is_empty():
		return _legal_leads(hand, trump, trump_broken)

	var led_suit: int = trick[0].suit
	var trick_has_trump := _has_suit(trick, trump)

	var same_suit := _cards_of_suit(hand, led_suit)
	if not same_suit.is_empty():
		# Koz açılmadıysa ve masaya koz girdiyse, yükseltme anlamsız: herhangi biri.
		if led_suit != trump and trick_has_trump:
			return same_suit
		return _raise_if_possible(same_suit, _highest_value_of_suit(trick, led_suit))

	var trumps := _cards_of_suit(hand, trump)
	if not trumps.is_empty():
		if trick_has_trump:
			return _raise_if_possible(trumps, _highest_value_of_suit(trick, trump))
		return trumps

	return hand.duplicate()


## Löveyi kazanan kartın `trick` içindeki indeksi.
static func trick_winner(trick: Array[CardData], trump: int) -> int:
	assert(not trick.is_empty())
	var best := 0
	for i in range(1, trick.size()):
		if beats(trick[i], trick[best], trick[0].suit, trump):
			best = i
	return best


## `challenger` kartı şu an kazanan `current` kartını geçer mi?
static func beats(challenger: CardData, current: CardData, led_suit: int, trump: int) -> bool:
	if challenger.suit == current.suit:
		return challenger.rank > current.rank
	if challenger.suit == trump:
		return true
	return false


static func _legal_leads(hand: Array[CardData], trump: int, trump_broken: bool) -> Array[CardData]:
	if trump_broken:
		return hand.duplicate()
	var non_trumps: Array[CardData] = hand.filter(func(c: CardData): return c.suit != trump)
	return non_trumps if not non_trumps.is_empty() else hand.duplicate()


static func _raise_if_possible(options: Array[CardData], value_to_beat: int) -> Array[CardData]:
	if not MUST_RAISE:
		return options
	var higher: Array[CardData] = options.filter(func(c: CardData): return c.rank > value_to_beat)
	return higher if not higher.is_empty() else options


static func _cards_of_suit(cards: Array[CardData], suit: int) -> Array[CardData]:
	return cards.filter(func(c: CardData): return c.suit == suit)


static func _has_suit(cards: Array[CardData], suit: int) -> bool:
	return cards.any(func(c: CardData): return c.suit == suit)


static func _highest_value_of_suit(cards: Array[CardData], suit: int) -> int:
	var best := 0
	for c in cards:
		if c.suit == suit and c.rank > best:
			best = c.rank
	return best
