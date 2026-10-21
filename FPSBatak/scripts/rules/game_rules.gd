class_name GameRules
extends Resource
## Bir oyun modunun bütün kuralları tek yerde.
##
## İki mod birbirinden tamamen ayrı yapılandırmalarla tutulur:
##
## STANDARD_BIDDING — Normal İhaleli (4 kişi)
##   4 oyuncu, 13'er kart, yerde kart yok, gömme yok, ihale 5..13.
##   Herkes pas derse ihale 4 olarak dağıtanın sağındakine kalır.
##
## BURIED_BIDDING — Gömmeli İhaleli (3 kişi)
##   3 oyuncu, 16'şar kart + 4 kapalı yer kartı, ihale 7..16.
##   Herkes pas derse ihale 7 olarak dağıtanın sağındakine kalır.
##   İhaleyi alan önce 4 kart gömer, kozu söyler, sonra yeri alır.
##
## Kod içinde "3 kişi", "16 kart" gibi sabitler yerine bu kaynak okunur.

enum Mode { STANDARD_BIDDING, BURIED_BIDDING }

## Herkes pas derse zorunlu ihalenin kime kalacağı.
enum AllPassRecipient { DEALER_RIGHT }

## İhale bittikten sonraki aşamalar (sırasıyla).
const PHASE_BURY := "bury"
const PHASE_TRUMP := "trump"
const PHASE_TAKE_KITTY := "take_kitty"

@export var mode := Mode.BURIED_BIDDING
@export var display_name := ""
@export_range(3, 4) var player_count := 3
@export var cards_per_player := 16
## Yere kapalı konan (ve ihaleyi alanın gömdüğü) kart sayısı. 0 = gömme yok.
@export var buried_cards := 4
@export var min_bid := 7
@export var max_bid := 16
## Herkes pas derse zorunlu ihale değeri ve kime kalacağı.
@export var all_pass_bid := 7
@export var all_pass_recipient := AllPassRecipient.DEALER_RIGHT


## Normal İhaleli — 4 kişi.
static func standard_bidding() -> GameRules:
	var r := GameRules.new()
	r.mode = Mode.STANDARD_BIDDING
	r.display_name = "NORMAL İHALELİ"
	r.player_count = 4
	r.cards_per_player = 13
	r.buried_cards = 0
	r.min_bid = 5
	r.max_bid = 13
	r.all_pass_bid = 4
	r.all_pass_recipient = AllPassRecipient.DEALER_RIGHT
	return r


## Gömmeli İhaleli — 3 kişi.
static func buried_bidding() -> GameRules:
	var r := GameRules.new()
	r.mode = Mode.BURIED_BIDDING
	r.display_name = "GÖMMELİ İHALELİ"
	r.player_count = 3
	r.cards_per_player = 16
	r.buried_cards = 4
	r.min_bid = 7
	r.max_bid = 16
	r.all_pass_bid = 7
	r.all_pass_recipient = AllPassRecipient.DEALER_RIGHT
	return r


static func for_mode(m: Mode) -> GameRules:
	return standard_bidding() if m == Mode.STANDARD_BIDDING else buried_bidding()


## İhale bittikten sonra ihaleyi alanın sırayla yapacakları.
func phases_after_bid() -> Array[String]:
	if buried_cards > 0:
		return [PHASE_BURY, PHASE_TRUMP, PHASE_TAKE_KITTY]
	return [PHASE_TRUMP]


func is_valid() -> bool:
	return player_count * cards_per_player + buried_cards == DeckManager.FULL_DECK_SIZE \
		and min_bid <= max_bid and max_bid <= cards_per_player
