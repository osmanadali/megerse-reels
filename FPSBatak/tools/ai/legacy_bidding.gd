extends RefCounted
## ÖNCEKİ ihale AI'sının birebir kopyası (yalnızca önce/sonra ölçümü için;
## oyunda kullanılmaz). Kaynak: AI ihale yenilemesinden önceki scripts/ai/ai_player.gd.

const KITTY_TRICK_VALUE := 0.2


static func choose_bid(hand: Array[CardData], valid: Array[int], kitty_size: int) -> int:
	if valid.is_empty():
		return BidManager.PASS
	var estimate := estimate_tricks(hand) + kitty_size * KITTY_TRICK_VALUE
	var target := int(floor(estimate))
	return valid[0] if valid[0] <= target else BidManager.PASS


static func estimate_tricks(hand: Array[CardData]) -> float:
	var best := 0.0
	for suit in CardData.Suit.values():
		best = max(best, _strength_with_trump(hand, suit))
	return best


static func choose_trump(hand: Array[CardData]) -> int:
	var best_suit: int = CardData.Suit.SPADES
	var best := -1.0
	for suit in CardData.Suit.values():
		var s := _strength_with_trump(hand, suit)
		if s > best:
			best = s
			best_suit = suit
	return best_suit


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
