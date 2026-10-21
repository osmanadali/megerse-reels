extends RefCounted
## AI ihale kalibrasyonu ve ölçümü için ortak simülasyon yardımcıları
## (geliştirme aracı; oyunda kullanılmaz).
##
## Bir eli sonuna kadar oynatır: ihaleyi alan (koltuk 0) seçilen kozla ilk
## löveyi açar, herkes mevcut AIPlayer kart oynama mantığıyla oynar ve
## kurallar BatakRules'tan gelir. Böylece "gerçek löve" oyundaki AI'nın
## gerçekten alacağı löve sayısıdır.


## Koltuk `declarer` ihaleyi almış ve `trump` koz iken oynanan eli bitirir;
## her koltuğun aldığı löve sayısını döndürür. `hands` değiştirilir.
static func play_out(hands: Array, trump: int, declarer: int) -> Array[int]:
	var n := hands.size()
	var ais: Array = []
	for i in n:
		ais.append(AIPlayer.new(i))
	var won: Array[int] = []
	won.resize(n)
	won.fill(0)
	var leader := declarer
	var broken := false
	var tricks: int = hands[0].size()
	for t in tricks:
		var trick: Array[CardData] = []
		var seats: Array[int] = []
		var seat := leader
		for k in n:
			var h: Array[CardData] = hands[seat]
			var legal := BatakRules.legal_cards(h, trick, trump, broken)
			var card: CardData = ais[seat].choose_card(legal, trick, trump)
			h.erase(card)
			if card.suit == trump:
				broken = true
			trick.append(card)
			seats.append(seat)
			seat = (seat + 1) % n
		leader = seats[BatakRules.trick_winner(trick, trump)]
		won[leader] += 1
	return won


static func copy_hands(hands: Array) -> Array:
	var out: Array = []
	for h in hands:
		out.append((h as Array[CardData]).duplicate())
	return out


## Gömmeli mod: ihaleyi alan önce `trump` için gömer, sonra yeri alır.
static func apply_bury_and_kitty(hand: Array[CardData], kitty: Array[CardData], trump: int) -> void:
	for c in AIPlayer.choose_bury(hand, kitty.size(), trump):
		hand.erase(c)
	hand.append_array(kitty)
