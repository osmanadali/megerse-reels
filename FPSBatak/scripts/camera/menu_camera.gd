class_name MenuCamera
extends Camera3D
## Ana menüde masanın etrafında yavaşça dönen kamera. "Oyuna Başla" ile
## oyuncunun koltuğundaki kameraya süzülerek geçer.

@export var target: Node3D
@export var orbit_radius := 2.05
@export var orbit_height := 1.45
## Masayı ekranın sağına (menünün karşısına) almak için sola bakış açısı.
@export var screen_offset_deg := 13.0
## Derece / saniye. Bilerek yavaş: baş döndürmemeli.
@export var orbit_speed_deg := 4.0
@export var start_angle_deg := 35.0

var _angle := 0.0
var _orbiting := true


func _ready() -> void:
	_angle = deg_to_rad(start_angle_deg)
	_update_orbit()


func _process(delta: float) -> void:
	if _orbiting:
		_angle += deg_to_rad(orbit_speed_deg) * delta
		_update_orbit()


## Kamerayı `to` kamerasının konumuna/açısına süzer ve onu etkin yapar.
func glide_to(to: Camera3D, duration := 1.4) -> void:
	_orbiting = false
	var from := global_transform
	var from_fov := fov
	var tween := create_tween()
	tween.tween_method(func(t: float):
		var e := ease(t, -2.2)
		global_transform = from.interpolate_with(to.global_transform, e)
		fov = lerpf(from_fov, to.fov, e)
	, 0.0, 1.0, duration)
	await tween.finished
	to.make_current()


func _update_orbit() -> void:
	var c := target.global_position
	global_position = c + Vector3(sin(_angle) * orbit_radius, orbit_height, cos(_angle) * orbit_radius)
	look_at(c + Vector3.UP * 0.1, Vector3.UP)
	rotate_object_local(Vector3.UP, deg_to_rad(screen_offset_deg))
