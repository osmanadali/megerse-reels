class_name MatchSettings
extends Resource
## Bir maçın (oyunun) başlangıç ayarları: oyun modu ve oyunun nasıl biteceği.
##
## İki ayrı oyun türü vardır, birlikte uygulanmaz:
## - TUR SAYISI ile: seçilen tur sayısı (5/7/9/11) oynanır; puan ne olursa
##   olsun oyun ancak turlar bitince biter, en yüksek puanlı kazanır.
## - HEDEF PUAN ile: tur sınırı yoktur; biri hedef puana (51/71/91/101)
##   ulaşınca oyun biter. Aynı turda birden fazla kişi ulaşırsa en yüksek
##   puanlı kazanır.
## Son seçim cihazda (user://) saklanır; internet gerekmez.

enum EndCondition { ROUNDS, TARGET }

const ROUND_OPTIONS: Array[int] = [5, 7, 9, 11]
const TARGET_OPTIONS: Array[int] = [51, 71, 91, 101]
const SAVE_PATH := "user://settings.cfg"
const SECTION := "match"

@export var mode := GameRules.Mode.BURIED_BIDDING
@export var end_condition := EndCondition.ROUNDS
@export var rounds := 7
@export var target_score := 71


## Maç bitti mi? Yalnızca seçilen oyun türünün koşuluna bakılır.
func is_match_over(rounds_played: int, totals: Array[int]) -> bool:
	if end_condition == EndCondition.ROUNDS:
		return rounds_played >= rounds
	return totals.max() >= target_score


## En yüksek puanlı koltuk(lar). Birden fazlaysa berabere.
static func winners(totals: Array[int]) -> Array[int]:
	var best: int = totals.max()
	var out: Array[int] = []
	for i in totals.size():
		if totals[i] == best:
			out.append(i)
	return out


func save() -> void:
	var cfg := ConfigFile.new()
	cfg.load(SAVE_PATH)  # varsa diğer bölümleri koru
	cfg.set_value(SECTION, "mode", mode)
	cfg.set_value(SECTION, "end_condition", end_condition)
	cfg.set_value(SECTION, "rounds", rounds)
	cfg.set_value(SECTION, "target_score", target_score)
	cfg.save(SAVE_PATH)


## Kaydedilmiş ayarları yükler; yoksa veya geçersizse varsayılanları döndürür.
static func load_saved() -> MatchSettings:
	var s := MatchSettings.new()
	var cfg := ConfigFile.new()
	if cfg.load(SAVE_PATH) == OK:
		var r: int = cfg.get_value(SECTION, "rounds", s.rounds)
		var t: int = cfg.get_value(SECTION, "target_score", s.target_score)
		if ROUND_OPTIONS.has(r):
			s.rounds = r
		if TARGET_OPTIONS.has(t):
			s.target_score = t
		var m: int = cfg.get_value(SECTION, "mode", s.mode)
		if GameRules.Mode.values().has(m):
			s.mode = m
		var ec: int = cfg.get_value(SECTION, "end_condition", s.end_condition)
		if EndCondition.values().has(ec):
			s.end_condition = ec
	return s
