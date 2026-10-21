class_name CardTracker
extends RefCounted
## Masadaki AÇIK bilgiyi tutar: hangi kart, hangi lövede, kim tarafından
## oynandı ve oyun kurallarından meşru olarak çıkarılabilenler.
##
## Hile yoktur: tracker hiçbir oyuncunun elini görmez. Bir oyuncunun "bakış
## açısından" görünmeyen kartlar, o oyuncunun kendi eli (ve ihale sahibiyse
## kendi gömdüğü kartlar) ayrıca verilerek hesaplanır.
##
## Kurallardan çıkarımlar (hepsi herkesin görebileceği hamlelerden):
## - Açılan renge uymadıysa: o renkte BOŞ (void).
## - Uymadı ve koz da atmadıysa: kozda da BOŞ.
## - Renge uydu ama masadaki en büyük kartı geçmedi (masada koz yokken):
##   mecburi yükseltme kuralı gereği o renkte daha büyük kartı YOK.
## - Koz attı ama masadaki kozu geçmedi: daha büyük kozu YOK.

var player_count: int
var trump: int
var bidder: int
var bid: int
var cards_per_player: int
## Gömmeli modda kimsenin bilmediği (ihale sahibi hariç) gömülü kart sayısı.
var hidden_buried: int

var played := {}                 # kart kimliği -> {seat, trick}
var history: Array = []          # [{trick, seat, card}] oynanma sırasıyla
var trick_winners: Array[int] = []
var tricks_won: Array[int] = []
var trump_broken := false
var trick_index := 0
var leader := 0
## voids[seat][suit] = true ise o oyuncu o renkte kesin boş.
var voids: Array = []
## suit_cap[seat][suit] = o oyuncunun o rengde sahip olabileceği en büyük
## değerden bir fazlası (15 = sınır yok).
var suit_cap: Array = []
var _cards_played_by: Array[int] = []
var _current: Array = []         # mevcut löve: [{seat, card}]


func _init(p_player_count: int, p_trump: int, p_bidder: int, p_bid: int,
		p_cards_per_player: int, p_hidden_buried := 0) -> void:
	player_count = p_player_count
	trump = p_trump
	bidder = p_bidder
	bid = p_bid
	cards_per_player = p_cards_per_player
	hidden_buried = p_hidden_buried
	leader = bidder
	for s in player_count:
		tricks_won.append(0)
		_cards_played_by.append(0)
		voids.append([false, false, false, false])
		suit_cap.append([15, 15, 15, 15])


static func key(c: CardData) -> String:
	return c.get_id()


## Bir kartın oynandığını kaydeder (oynanma anındaki löve durumuyla birlikte).
func record_play(seat: int, card: CardData) -> void:
	if not _current.is_empty():
		var led: CardData = _current[0].card
		var best: CardData = _current_best()
		var trumped := _current.any(func(e): return e.card.suit == trump)
		if card.suit != led.suit:
			voids[seat][led.suit] = true
			if card.suit != trump:
				voids[seat][trump] = true
			elif best.suit == trump and card.rank < best.rank:
				suit_cap[seat][trump] = mini(suit_cap[seat][trump], best.rank)
		elif not trumped or led.suit == trump:
			if card.rank < best.rank:
				suit_cap[seat][led.suit] = mini(suit_cap[seat][led.suit], best.rank)
	played[key(card)] = {"seat": seat, "trick": trick_index}
	history.append({"trick": trick_index, "seat": seat, "card": card})
	_cards_played_by[seat] += 1
	_current.append({"seat": seat, "card": card})
	if card.suit == trump:
		trump_broken = true


## Löve bittiğinde kazananı kaydeder.
func record_trick_end(winner: int) -> void:
	trick_winners.append(winner)
	tricks_won[winner] += 1
	trick_index += 1
	leader = winner
	_current.clear()


func is_played(c: CardData) -> bool:
	return played.has(key(c))


func hand_size(seat: int) -> int:
	return cards_per_player - _cards_played_by[seat]


func remaining_tricks() -> int:
	return cards_per_player - trick_index


## İhale sahibinin ihaleyi tutturmak için daha kaç löveye ihtiyacı var.
func tricks_needed() -> int:
	return maxi(0, bid - tricks_won[bidder])


## Bir oyuncunun belirli bir kartı elinde tutması (açık bilgiye göre) mümkün mü?
func could_hold(seat: int, c: CardData) -> bool:
	return not is_played(c) and not voids[seat][c.suit] and c.rank < suit_cap[seat][c.suit]


## `perspective` oyuncusunun göremediği kartlar: oynanmamış, kendi elinde
## olmayan ve (ihale sahibiyse) kendi gömmediği kartlar.
func unseen(own_hand: Array[CardData], own_buried: Array[CardData] = []) -> Array[CardData]:
	var mine := {}
	for c in own_hand:
		mine[key(c)] = true
	for c in own_buried:
		mine[key(c)] = true
	var out: Array[CardData] = []
	for s in CardData.Suit.values():
		for r in CardData.Rank.values():
			var c := CardData.create(s, r)
			if not is_played(c) and not mine.has(key(c)):
				out.append(c)
	return out


## Bir rengin oynanmamış en büyük kartı (bakış açısından bağımsız; 0 = renk bitti).
func highest_unplayed(suit: int) -> int:
	for r in range(14, 1, -1):
		if not played.has("%s_%s" % [CardData.SUIT_CODES[suit], CardData.RANK_LABELS[r]]):
			return r
	return 0


## `c` kartı, bakış açısına göre o rengin kalan en büyüğü mü? (Daha büyük
## kartların hepsi oynandı ya da bu oyuncunun kendisinde / kendi gömdüklerinde.)
func is_master(c: CardData, own_hand: Array[CardData], own_buried: Array[CardData] = []) -> bool:
	var mine := {}
	for x in own_hand:
		mine[key(x)] = true
	for x in own_buried:
		mine[key(x)] = true
	for r in range(c.rank + 1, 15):
		var h := CardData.create(c.suit, r)
		if not is_played(h) and not mine.has(key(h)):
			return false
	return true


## Bakış açısına göre rakiplerde (veya bilinmeyen gömülüde) olabilecek koz sayısı.
func unseen_trumps(own_hand: Array[CardData], own_buried: Array[CardData] = []) -> int:
	return unseen(own_hand, own_buried).filter(func(c): return c.suit == trump).size()


func current_trick_seats() -> Array[int]:
	var out: Array[int] = []
	for e in _current:
		out.append(e.seat)
	return out


func _current_best() -> CardData:
	var cards: Array[CardData] = []
	for e in _current:
		cards.append(e.card)
	return cards[BatakRules.trick_winner(cards, trump)]
