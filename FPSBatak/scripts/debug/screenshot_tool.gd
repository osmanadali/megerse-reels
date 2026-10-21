extends Node
## Geliştirme aracı: otomatik görsel kontrol için ekran görüntüsü alır.
##   -- --screenshot=<yol.png>                 (yaklaşık 0.5 sn sonra tek kare)
##   -- --screenshot=<yol.png> --shot-times=2,6.5,9
##        (verilen saniyelerde <yol>_0.png, <yol>_1.png ... kaydeder)
## Son kareden sonra oyunu kapatır. Normal oyunda hiçbir şey yapmaz.

var _path := ""
var _times: Array[float] = [0.5]


func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--screenshot="):
			_path = arg.trim_prefix("--screenshot=")
		elif arg.begins_with("--shot-times="):
			_times.clear()
			for t in arg.trim_prefix("--shot-times=").split(","):
				_times.append(float(t))
	if _path.is_empty():
		queue_free()
		return
	var elapsed := 0.0
	for i in _times.size():
		await get_tree().create_timer(_times[i] - elapsed).timeout
		elapsed = _times[i]
		await RenderingServer.frame_post_draw
		var out := _path if _times.size() == 1 else _path.get_basename() + "_%d.png" % i
		var err := get_viewport().get_texture().get_image().save_png(out)
		print("Screenshot -> %s (%s)" % [out, error_string(err)])
	get_tree().quit()
