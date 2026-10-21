class_name BidContext
extends RefCounted
## İhale AI'sının 4. adımı için girdi: İHALE DURUMU.
## Yalnızca masada herkesin bildiği bilgileri içerir (kimin ne dediği);
## başka oyuncuların kartlarına dair hiçbir şey yoktur.

var rules: GameRules
var seat := 0
var valid: Array[int] = []        # şu an söylenebilecek teklifler (artan)
var current_bid := 0               # masadaki en yüksek teklif (0 = yok)
var current_holder := -1
var passed: Array[bool] = []       # kim pas dedi
var all_pass_seat := -1            # herkes pas derse ihale kime kalır
var all_pass_bid := 0


static func from_bid_manager(bm: BidManager, p_rules: GameRules) -> BidContext:
	var c := BidContext.new()
	c.rules = p_rules
	c.seat = bm.current_seat()
	c.valid = bm.valid_bids()
	c.current_bid = bm.current_bid
	c.current_holder = bm.current_holder
	for i in bm.player_count:
		c.passed.append(bm.has_passed(i))
	c.all_pass_seat = bm.all_pass_seat
	c.all_pass_bid = bm.all_pass_bid
	return c


## Bağlam bilgisi olmadan (yalnızca geçerli tekliflerle) çağrılan eski API için.
static func minimal(p_rules: GameRules, p_valid: Array[int]) -> BidContext:
	var c := BidContext.new()
	c.rules = p_rules
	c.valid = p_valid
	c.current_bid = maxi(0, p_valid[0] - 1) if not p_valid.is_empty() else 0
	return c


func nobody_bid() -> bool:
	return current_holder < 0


## Herkes pas derse zorunlu ihale bu oyuncuya mı kalacak?
func i_am_all_pass_recipient() -> bool:
	return seat == all_pass_seat


## Benden sonra hâlâ konuşabilecek (pas dememiş) başka oyuncu var mı?
func others_still_active() -> int:
	var n := 0
	for i in passed.size():
		if i != seat and not passed[i]:
			n += 1
	return n
