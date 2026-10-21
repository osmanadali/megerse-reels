class_name PlayContext
extends RefCounted
## Kart oynama AI'sının karar anında görebildiği her şey. Yalnızca o oyuncunun
## MEŞRU olarak bildiği bilgiler: kendi eli, masadaki açık kartlar, tracker'ın
## açık bilgiden çıkardıkları ve (ihale sahibiyse) kendi gömdüğü kartlar.

var rules: GameRules
var seat := 0
var own_hand: Array[CardData] = []
var legal: Array[CardData] = []
var trick: Array[CardData] = []          # mevcut lövede oynananlar (sırayla)
var trick_seats: Array[int] = []
var trump := 0
var trump_broken := false
var bidder := 0
var bid := 0
var tracker: CardTracker
## Yalnızca ihale sahibi için: kendi gömdüğü kartlar (diğerleri için boş).
var own_buried: Array[CardData] = []


static func build(p_rules: GameRules, p_seat: int, hand: Array[CardData], p_legal: Array[CardData],
		p_trick: Array[CardData], p_trick_seats: Array[int], p_tracker: CardTracker,
		p_own_buried: Array[CardData] = []) -> PlayContext:
	var c := PlayContext.new()
	c.rules = p_rules
	c.seat = p_seat
	c.own_hand = hand
	c.legal = p_legal
	c.trick = p_trick
	c.trick_seats = p_trick_seats
	c.tracker = p_tracker
	c.trump = p_tracker.trump
	c.trump_broken = p_tracker.trump_broken
	c.bidder = p_tracker.bidder
	c.bid = p_tracker.bid
	c.own_buried = p_own_buried if p_seat == p_tracker.bidder else ([] as Array[CardData])
	return c


func mode() -> int:
	return rules.mode


func player_count() -> int:
	return tracker.player_count


func is_bidder() -> bool:
	return seat == bidder


func tricks_won() -> Array[int]:
	return tracker.tricks_won


func tricks_needed() -> int:
	return tracker.tricks_needed()


func remaining_tricks() -> int:
	return tracker.remaining_tricks()


func leader_index() -> int:
	return tracker.leader


func is_leading() -> bool:
	return trick.is_empty()


## Bu lövede benden sonra oynayacak koltuklar.
func players_after() -> Array[int]:
	var out: Array[int] = []
	var n := player_count()
	var left := n - trick.size() - 1
	for i in left:
		out.append((seat + 1 + i) % n)
	return out


func opponents() -> Array[int]:
	var out: Array[int] = []
	for s in player_count():
		if s != seat:
			out.append(s)
	return out


## Bu oyuncunun göremediği kartlar (rakiplerde veya bilinmeyen gömülüde).
func unseen() -> Array[CardData]:
	return tracker.unseen(own_hand, own_buried)


## Gömmeli modda bu oyuncunun bilmediği gömülü kart sayısı (yalnızca savunanlar için > 0).
func unknown_buried() -> int:
	return 0 if is_bidder() else tracker.hidden_buried
