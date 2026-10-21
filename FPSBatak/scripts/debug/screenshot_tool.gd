extends Node
## Geliştirme aracı: otomatik görsel kontrol için ekran görüntüsü alır.
##   -- --screenshot=<yol.png>                 (yaklaşık 0.5 sn sonra tek kare)
##   -- --screenshot=<yol.png> --shot-times=2,6.5,9
##        (verilen saniyelerde <yol>_0.png, <yol>_1.png ... kaydeder)
##   --preview-panels  her karede sırayla ihale / gömme / koz panelini açar
##                     (karar panellerinin görünümünü kontrol etmek için)
## Son kareden sonra oyunu kapatır. Normal oyunda hiçbir şey yapmaz.

var _path := ""
var _times: Array[float] = [0.5]
var _preview_panels := false


func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--screenshot="):
			_path = arg.trim_prefix("--screenshot=")
		elif arg.begins_with("--shot-times="):
			_times.clear()
			for t in arg.trim_prefix("--shot-times=").split(","):
				_times.append(float(t))
		elif arg == "--preview-panels":
			_preview_panels = true
	if _path.is_empty():
		queue_free()
		return
	var elapsed := 0.0
	for i in _times.size():
		await get_tree().create_timer(_times[i] - elapsed).timeout
		elapsed = _times[i]
		if _preview_panels:
			_show_preview(i)
			await get_tree().create_timer(0.5).timeout
			elapsed += 0.5
		await RenderingServer.frame_post_draw
		var out := _path if _times.size() == 1 else _path.get_basename() + "_%d.png" % i
		var err := get_viewport().get_texture().get_image().save_png(out)
		print("Screenshot -> %s (%s)" % [out, error_string(err)])
	get_tree().quit()


func _show_preview(step: int) -> void:
	var hud: GameHUD = get_node("../HUD")
	var seats: SeatLayout = get_node("../Seats")
	hud.hide_bury()
	hud._bid_panel.visible = false
	hud._trump_panel.visible = false
	match step:
		0:
			hud.show_bidding([5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], "Henüz ihale yok — en az 5")
		1:
			seats.get_opponent(1).say("7", 0)
			seats.get_opponent(2).say("PAS", 0)
			hud.show_bury(4)
			hud.hand.begin_multi_select(4)
			for i in [1, 4, 9]:
				hud.hand._cards[i].selected = true
			hud._on_selection_changed(3)
		2:
			hud.show_trump_choice()
