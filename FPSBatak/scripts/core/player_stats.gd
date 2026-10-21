class_name PlayerStats
extends RefCounted
## Oyuncunun kalıcı istatistikleri (cihazda, user:// altında saklanır).

const DEFAULT_PATH := "user://stats.cfg"
const SECTION := "stats"
const KEYS := ["matches_played", "matches_won", "rounds_played", "bids_taken", "bids_made",
	"best_match_score"]

var matches_played := 0
var matches_won := 0
var rounds_played := 0
var bids_taken := 0
var bids_made := 0
var best_match_score := 0
var _path: String


func _init(path: String = DEFAULT_PATH) -> void:
	_path = path


static func load_from(path: String = DEFAULT_PATH) -> PlayerStats:
	var s := PlayerStats.new(path)
	var cfg := ConfigFile.new()
	if cfg.load(path) == OK:
		for key in KEYS:
			s.set(key, int(cfg.get_value(SECTION, key, 0)))
	return s


func save() -> void:
	var cfg := ConfigFile.new()
	for key in KEYS:
		cfg.set_value(SECTION, key, get(key))
	cfg.save(_path)


## Bir tur bittiğinde. `took_bid`: ihaleyi oyuncu mu aldı, `made`: tutturdu mu.
func record_round(took_bid: bool, made: bool) -> void:
	rounds_played += 1
	if took_bid:
		bids_taken += 1
		if made:
			bids_made += 1


func record_match(won: bool, final_score: int) -> void:
	matches_played += 1
	if won:
		matches_won += 1
	if matches_played == 1 or final_score > best_match_score:
		best_match_score = final_score


## Ekranda gösterilecek satırlar.
func summary_lines() -> Array[String]:
	var win_rate := 0 if matches_played == 0 else roundi(100.0 * matches_won / matches_played)
	var bid_rate := 0 if bids_taken == 0 else roundi(100.0 * bids_made / bids_taken)
	return [
		"Oynanan oyun: %d" % matches_played,
		"Kazanılan oyun: %d  (%%%d)" % [matches_won, win_rate],
		"Oynanan tur: %d" % rounds_played,
		"Alınan ihale: %d — tutturulan: %d  (%%%d)" % [bids_taken, bids_made, bid_rate],
		"En yüksek oyun puanı: %d" % best_match_score,
	]
