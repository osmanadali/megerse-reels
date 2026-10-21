class_name GameRules
extends Resource
## Oyun varyantının bütün ayarları tek yerde.
##
## Kod içinde "3 kişi", "16 kart" gibi sabitler yerine bu kaynak okunur;
## böylece 3 kişilik gömmeli ve 4 kişilik ihaleli batak aynı kodla çalışır.

@export_range(3, 4) var player_count := 3
@export var cards_per_player := 16
## Yere kapalı konan ve ihaleyi alanın alıp aynı sayıda gömdüğü kart sayısı.
@export var kitty_size := 4
@export var min_bid := 5
@export var max_bid := 16
## Herkes pas derse dağıtan en düşük ihaleyle almak zorunda (false: yeniden dağıt).
@export var all_pass_forces_dealer := true


## Varsayılan: 3 kişilik gömmeli ihaleli batak (16'şar kart + 4 yer kartı).
static func three_player_gommeli() -> GameRules:
	return GameRules.new()


## 4 kişilik ihaleli batak (13'er kart, gömme yok).
static func four_player_ihaleli() -> GameRules:
	var r := GameRules.new()
	r.player_count = 4
	r.cards_per_player = 13
	r.kitty_size = 0
	r.min_bid = 5
	r.max_bid = 13
	return r


func is_valid() -> bool:
	return player_count * cards_per_player + kitty_size == DeckManager.FULL_DECK_SIZE \
		and min_bid <= max_bid and max_bid <= cards_per_player
