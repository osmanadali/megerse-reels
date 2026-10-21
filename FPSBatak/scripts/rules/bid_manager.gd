class_name BidManager
extends RefCounted
## İhale turunun durumu (saf mantık).
##
## Sıra dağıtanın sağındakinden başlar ve dönerek ilerler. Her oyuncu ya
## mevcut ihaleden büyük bir değer söyler ya da pas der; pas diyen bir daha
## giremez. Tek kişi kalınca (veya biri en yüksek ihaleyi söyleyince) biter.

const PASS := 0

var player_count: int
var dealer: int
var min_bid: int
var max_bid: int
var forces_dealer: bool

var current_bid := 0
var current_holder := -1
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
	forces_dealer = rules.all_pass_forces_dealer
	_turn = Seat.next(dealer, player_count)
	for i in player_count:
		_passed.append(false)
		last_call.append(-1)


func current_seat() -> int:
	return _turn


func is_finished() -> bool:
	return _finished


## Sıradaki oyuncunun söyleyebileceği ihaleler (pas her zaman serbesttir).
func valid_bids() -> Array[int]:
	var out: Array[int] = []
	for v in range(max(current_bid + 1, min_bid), max_bid + 1):
		out.append(v)
	return out


func bid(amount: int) -> void:
	assert(not _finished and valid_bids().has(amount), "Geçersiz ihale")
	current_bid = amount
	current_holder = _turn
	last_call[_turn] = amount
	if amount >= max_bid:
		_finished = true
		return
	_advance()


func pass_turn() -> void:
	assert(not _finished)
	_passed[_turn] = true
	last_call[_turn] = PASS
	_advance()


## Herkes pas dedi ve kimse ihale almadı mı? (forces_dealer=false ise yeniden dağıtılır)
func is_void() -> bool:
	return _finished and current_holder < 0


func _advance() -> void:
	var active := _passed.count(false)
	if current_holder >= 0 and active <= 1:
		_finished = true
		return
	if active == 0:  # kimse ihale almadı
		_finished = true
		if forces_dealer:
			current_holder = dealer
			current_bid = min_bid
		return
	for step in player_count:
		_turn = Seat.next(_turn, player_count)
		if not _passed[_turn]:
			return
