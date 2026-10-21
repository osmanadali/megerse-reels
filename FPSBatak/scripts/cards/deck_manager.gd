class_name DeckManager
extends RefCounted
## Desteyi yöneten saf mantık sınıfı (sahneye bağlı değildir).
##
## Görevleri: 52 kartı oluşturmak, karıştırmak, dağıtmak ve oynanan kartları
## takip etmek. Dağıtım animasyonu görsel katmanın işidir; o katman
## `cards_dealt` sinyalini dinleyerek kartları masada hareket ettirir.

signal deck_built(card_count: int)
signal deck_shuffled
signal cards_dealt(hands: Array)
signal card_played(card: CardData)

const PLAYER_COUNT := 4
const CARDS_PER_PLAYER := 13
const FULL_DECK_SIZE := 52

## Henüz dağıtılmamış kartlar. Dizinin sonu "destenin üstü"dür.
var _draw_pile: Array[CardData] = []
## Bu tur masaya oynanmış (veya gömülmüş) kartlar, oynanma sırasıyla.
var _played: Array[CardData] = []
var _rng := RandomNumberGenerator.new()


func _init(seed_value: int = -1) -> void:
	set_seed(seed_value)
	build_deck()


## Tekrarlanabilir karıştırma için tohum. -1 rastgele tohum demektir.
func set_seed(seed_value: int) -> void:
	if seed_value < 0:
		_rng.randomize()
	else:
		_rng.seed = seed_value


## Sıralı, eksiksiz 52 kartlık desteyi yeniden oluşturur.
func build_deck() -> void:
	_draw_pile.clear()
	_played.clear()
	for s in CardData.Suit.values():
		for r in CardData.Rank.values():
			_draw_pile.append(CardData.create(s, r))
	deck_built.emit(_draw_pile.size())


## Fisher–Yates karıştırma (kendi RNG'mizle, tohumlanabilir).
func shuffle() -> void:
	for i in range(_draw_pile.size() - 1, 0, -1):
		var j := _rng.randi_range(0, i)
		var tmp := _draw_pile[i]
		_draw_pile[i] = _draw_pile[j]
		_draw_pile[j] = tmp
	deck_shuffled.emit()


## Destenin üstünden bir kart çeker. Deste boşsa null döner.
func draw_card() -> CardData:
	if _draw_pile.is_empty():
		return null
	return _draw_pile.pop_back()


## Kartları gerçek masadaki gibi tek tek, sırayla dağıtır.
## Dönen dizi: her oyuncu için bir Array[CardData], elde sıralı.
## `first_player` dağıtıma başlanacak koltuk indeksidir.
func deal(player_count: int = PLAYER_COUNT, cards_each: int = CARDS_PER_PLAYER,
		first_player: int = 0) -> Array:
	assert(player_count * cards_each <= _draw_pile.size(), "Destede yeterli kart yok")
	var hands: Array = []
	for i in player_count:
		var hand: Array[CardData] = []
		hands.append(hand)
	for round_index in cards_each:
		for offset in player_count:
			var seat := (first_player + offset) % player_count
			hands[seat].append(draw_card())
	for hand in hands:
		hand.sort_custom(CardData.sort_for_hand)
	cards_dealt.emit(hands)
	return hands


## Bir kartın masaya oynandığını (veya gömüldüğünü) kaydeder.
func register_played(card: CardData) -> void:
	_played.append(card)
	card_played.emit(card)


func is_played(card: CardData) -> bool:
	for c in _played:
		if c.same_as(card):
			return true
	return false


func get_played_cards() -> Array[CardData]:
	return _played.duplicate()


func cards_remaining() -> int:
	return _draw_pile.size()
