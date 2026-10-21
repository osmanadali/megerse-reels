class_name MatchSettings
extends Resource
## Bir maçın (oyunun) başlangıç ayarları: kaç el oynanacağı ve hedef puan.
##
## Maç, seçilen el sayısı tamamlanınca VEYA biri hedef puana ulaşınca
## (hangisi önce olursa) biter. En yüksek puanlı oyuncu kazanır.
## Son seçim cihazda (user://) saklanır; internet gerekmez.

const ROUND_OPTIONS: Array[int] = [5, 7, 9, 11]
const TARGET_OPTIONS: Array[int] = [51, 71, 91, 101]
const SAVE_PATH := "user://settings.cfg"
const SECTION := "match"

@export var mode := GameRules.Mode.BURIED_BIDDING
@export var rounds := 7
@export var target_score := 71


## Maç bitti mi?
func is_match_over(rounds_played: int, totals: Array[int]) -> bool:
	return rounds_played >= rounds or totals.max() >= target_score


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
	return s
