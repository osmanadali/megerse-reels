class_name BidManager
extends RefCounted
## İhale turunun durumu (saf mantık). Kurallar GameRules'tan okunur.
##
## Sıra dağıtanın sağındakinden başlar ve dönerek ilerler. Her oyuncu ya
## mevcut en yüksek tekliften büyük bir değer söyler ya da pas der; pas diyen
## o ihale turuna bir daha giremez. Tek kişi kalınca (veya biri en yüksek
## ihaleyi söyleyince) biter.
##
## Herkes pas derse (ya da teklif yokken yalnızca zorunlu ihaleyi alacak oyuncu
## kalırsa) yeni ihale turu açılmaz: ihale `all_pass_bid` değeriyle doğrudan
## dağıtanın sağındaki oyuncuya kalır.

const PASS := 0

var player_count: int
var dealer: int
var min_bid: int
var max_bid: int
var all_pass_bid: int
## Herkes pas derse ihalenin kalacağı koltuk.
var all_pass_seat: int

var current_bid := 0
var current_holder := -1
## İhale, herkes pas dediği için zorunlu mu verildi?
var forced := false
var _turn: int
var _passed: Array[bool] = []
var _finished := false
## Her koltuğun son söylediği (PASS veya sayı); -1 = henüz konuşmadı.
var last_call: Array[int] = []


func _init(rules: GameRules, p_dealer: int) -> void:
	player_count = rules.player_count
	dealer = p_dealer
	min_bid = rules.min_bid
	max_bid = rules.max_bid
	all_pass_bid = rules.all_pass_bid
	match rules.all_pass_recipient:
		GameRules.AllPassRecipient.DEALER_RIGHT:
			all_pass_seat = dealer_right(dealer, player_count)
	_turn = dealer_right(dealer, player_count)
	for i in player_count:
		_passed.append(false)
		last_call.append(-1)


## Dağıtanın sağındaki oyuncu (oyun sağa doğru ilerlediği için sıradaki koltuk).
static func dealer_right(p_dealer: int, count: int) -> int:
	return Seat.next(p_dealer, count)


func current_seat() -> int:
	return _turn


func is_finished() -> bool:
	return _finished


func has_passed(seat: int) -> bool:
	return _passed[seat]


## Sıradaki oyuncunun söyleyebileceği ihaleler (pas her zaman serbesttir).
func valid_bids() -> Array[int]:
	var out: Array[int] = []
	for v in range(max(current_bid + 1, min_bid), max_bid + 1):
		out.append(v)
	return out


func is_valid_bid(amount: int) -> bool:
	return not _finished and amount >= min_bid and amount <= max_bid and amount > current_bid


## Sıradaki oyuncu `amount` söyler. Geçersizse (aralık dışı veya mevcut en
## yüksek tekliften büyük değilse) reddedilir, durum değişmez ve false döner.
func bid(amount: int) -> bool:
	if not is_valid_bid(amount):
		return false
	current_bid = amount
	current_holder = _turn
	last_call[_turn] = amount
	if amount >= max_bid:
		_finished = true
		return true
	_advance()
	return true


## Sıradaki oyuncu pas der; o ihale turuna bir daha giremez.
func pass_turn() -> bool:
	if _finished:
		return false
	_passed[_turn] = true
	last_call[_turn] = PASS
	_advance()
	return true


func _advance() -> void:
	var active := _passed.count(false)
	if current_holder >= 0 and active <= 1:
		_finished = true
		return
	if current_holder < 0 and (active == 0 or (active == 1 and not _passed[all_pass_seat])):
		_force_to_recipient()
		return
	for step in player_count:
		_turn = Seat.next(_turn, player_count)
		if not _passed[_turn]:
			return


## Kimse teklif vermedi: yeni tur açılmaz, zorunlu ihale doğrudan verilir.
func _force_to_recipient() -> void:
	_finished = true
	forced = true
	current_holder = all_pass_seat
	current_bid = all_pass_bid
