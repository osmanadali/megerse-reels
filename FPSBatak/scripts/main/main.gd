extends Node3D
## Ana sahne kökü: menü ↔ oyun geçişlerini ve duraklatmayı yönetir.
## Oyunun kendisi TableController'dadır.
##
## Akış: ana menü (kamera masanın etrafında döner) → OYUNA BAŞLA → kamera
## oyuncunun koltuğuna süzülür → masa ayarları → oyun. Esc: duraklat.

@onready var _menu: MainMenu = $MainMenu
@onready var _menu_camera: MenuCamera = $MenuCamera
@onready var _player_camera: Camera3D = $Seats/Seat0_South/PlayerCamera
@onready var _controller: TableController = $TableController
@onready var _hud: GameHUD = $HUD

var _in_game := false


func _ready() -> void:
	UserSettings.load_saved().apply()
	_menu.start_requested.connect(_on_start)
	_menu.resume_requested.connect(_resume)
	_menu.main_menu_requested.connect(_back_to_menu)
	_hud.main_menu_requested.connect(_back_to_menu)
	if "--autoplay" in OS.get_cmdline_user_args():
		_menu.hide_all()
		_player_camera.make_current()
		_in_game = true
		_controller.begin()
		return
	_hud.visible = false
	_menu_camera.make_current()
	_menu.show_main()


func _on_start() -> void:
	_menu.hide_all()
	await _menu_camera.glide_to(_player_camera)
	_hud.visible = true
	_in_game = true
	_controller.begin()


func _unhandled_input(event: InputEvent) -> void:
	if not event.is_action_pressed("ui_cancel"):
		return
	if not _in_game:
		_menu.close_side_panel()
	elif _menu.is_pause_open():
		_menu.hide_all()
		_resume()
	else:
		get_tree().paused = true
		_menu.show_pause()
	get_viewport().set_input_as_handled()


func _resume() -> void:
	get_tree().paused = false


## Süren eli bırakıp menüye döner. Sahne baştan yüklenir; böylece yarım kalan
## animasyon ve beklemeler temizce kapanır.
func _back_to_menu() -> void:
	get_tree().paused = false
	get_tree().reload_current_scene()
