extends Node
## Geliştirme aracı: `-- --screenshot=<yol>` argümanıyla çalıştırılırsa birkaç
## kare bekleyip ekran görüntüsü kaydeder ve oyunu kapatır. Otomatik görsel
## kontrol için kullanılır; normal oyunda hiçbir şey yapmaz.

const SETTLE_FRAMES := 30

var _path := ""


func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--screenshot="):
			_path = arg.trim_prefix("--screenshot=")
	if _path.is_empty():
		queue_free()
		return
	for i in SETTLE_FRAMES:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var err := get_viewport().get_texture().get_image().save_png(_path)
	print("Screenshot -> %s (%s)" % [_path, error_string(err)])
	get_tree().quit()
