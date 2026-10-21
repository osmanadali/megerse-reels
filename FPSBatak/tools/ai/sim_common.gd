extends RefCounted
## AI ihale kalibrasyonu ve ölçümü için ortak simülasyon yardımcıları
## (geliştirme aracı; oyunda kullanılmaz).
##
## Bir eli sonuna kadar oynatır: ihaleyi alan seçilen kozla ilk löveyi açar,
## herkes oyundaki kart oynama AI'sıyla oynar ve kurallar BatakRules'tan
## gelir. Böylece "gerçek löve" oyundaki AI'nın gerçekten alacağı löve sayısıdır.


## Oyundaki kart oynama yolu (CardTracker + PlayContext + PlayPolicy, NORMAL
## zorluk — TableController'ın varsayılanı). Gömülen kartlar yalnızca ihale
## sahibinin bağlamına verilir; savunanlar yalnızca sayısını bilir.
## Her koltuğun aldığı löve sayısını döndürür. `hands` değiştirilir.
static func play_out_current(rules: GameRules, hands: Array, trump: int, declarer: int, bid: int,
		buried: Array[CardData] = []) -> Array[int]:
	var n := hands.size()
	var ais: Array = []
	for i in n:
		ais.append(AIPlayer.new(i))
	var tr := CardTracker.new(n, trump, declarer, bid, hands[0].size(), buried.size())
	var leader := declarer
	for t in hands[0].size():
		var trick: Array[CardData] = []
		var seats: Array[int] = []
		var seat := leader
		for k in n:
			var h: Array[CardData] = hands[seat]
			var legal := BatakRules.legal_cards(h, trick, trump, tr.trump_broken)
			var ctx := PlayContext.build(rules, seat, h, legal, trick, seats, tr,
				buried if seat == declarer else ([] as Array[CardData]))
			var card: CardData = ais[seat].choose_card_in_context(ctx)
			h.erase(card)
			tr.record_play(seat, card)
			trick.append(card)
			seats.append(seat)
			seat = (seat + 1) % n
		leader = seats[BatakRules.trick_winner(trick, trump)]
		tr.record_trick_end(leader)
	return tr.tricks_won.duplicate()


## ESKİ kart oynama yolu (bağlamsız `choose_card`; ilk ihale kalibrasyonu bununla
## yapılmıştı). Karşılaştırma için korunur.
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
## Gömülen kartları döndürür (yalnızca ihale sahibinin bilgisi).
static func apply_bury_and_kitty(hand: Array[CardData], kitty: Array[CardData], trump: int) -> Array[CardData]:
	var buried := AIPlayer.choose_bury(hand, kitty.size(), trump)
	for c in buried:
		hand.erase(c)
	hand.append_array(kitty)
	return buried
