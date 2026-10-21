class_name UserSettings
extends RefCounted
## Cihaz ayarları: ses seviyesi ve tam ekran. user://settings.cfg içinde saklanır
## (aynı dosyadaki maç ayarlarına dokunmaz).

const PATH := "user://settings.cfg"

var master_volume := 0.8   # 0..1
var fullscreen := false


static func load_saved() -> UserSettings:
	var s := UserSettings.new()
	var cfg := ConfigFile.new()
	if cfg.load(PATH) == OK:
		s.master_volume = clampf(cfg.get_value("audio", "master_volume", s.master_volume), 0.0, 1.0)
		s.fullscreen = cfg.get_value("display", "fullscreen", s.fullscreen)
	return s


func save() -> void:
	var cfg := ConfigFile.new()
	cfg.load(PATH)  # diğer bölümleri koru
	cfg.set_value("audio", "master_volume", master_volume)
	cfg.set_value("display", "fullscreen", fullscreen)
	cfg.save(PATH)


## Ayarları motora uygular.
func apply() -> void:
	var bus := AudioServer.get_bus_index("Master")
	AudioServer.set_bus_volume_db(bus, linear_to_db(maxf(master_volume, 0.0001)))
	AudioServer.set_bus_mute(bus, master_volume <= 0.001)
	if OS.has_feature("mobile") or DisplayServer.get_name() == "headless":
		return
	DisplayServer.window_set_mode(
		DisplayServer.WINDOW_MODE_FULLSCREEN if fullscreen else DisplayServer.WINDOW_MODE_WINDOWED)
