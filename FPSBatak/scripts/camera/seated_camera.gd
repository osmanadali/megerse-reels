class_name SeatedCamera
extends Camera3D
## Oyuncunun gözü: masada oturan birinin bakış açısı.
##
## Kamera sabit bir oturma noktasından masanın ortasına bakar. Baş döndürmeyecek
## kadar küçük bir "nefes" salınımı oturuyormuş hissini güçlendirir.
## `nudge()` ileride kart oynanınca çok hafif bir öne eğilme için kullanılır.

## Kameranın baktığı nokta (genelde masa ortasındaki oyun alanı).
@export var look_target: Node3D
## Bakış noktasının hedefe göre dikey kaydırması: rakiplerin yüzlerini de
## kadraja almak için hedefin biraz üstüne bakarız.
@export var look_height_offset := 0.12

@export_group("Nefes salınımı")
@export var breathing_enabled := true
## Metre cinsinden genlik. Bilerek çok küçük tutuldu.
@export var breathing_amplitude := 0.0025
## Saniyedeki nefes sayısı.
@export var breathing_frequency := 0.22

@export_group("Öne eğilme")
@export var nudge_distance := 0.02
@export var nudge_duration := 0.18

var _base_position: Vector3
var _time := 0.0
var _nudge_offset := Vector3.ZERO
var _nudge_tween: Tween


func _ready() -> void:
	_base_position = position
	_aim()


func _process(delta: float) -> void:
	_time += delta
	var breath := Vector3.ZERO
	if breathing_enabled:
		breath.y = sin(_time * TAU * breathing_frequency) * breathing_amplitude
	position = _base_position + breath + _nudge_offset


## Kısa ve yumuşak bir öne eğilip geri gelme hareketi.
func nudge() -> void:
	if _nudge_tween and _nudge_tween.is_valid():
		_nudge_tween.kill()
	var forward := -global_transform.basis.z * nudge_distance
	_nudge_tween = create_tween().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	_nudge_tween.tween_property(self, "_nudge_offset", forward, nudge_duration * 0.5)
	_nudge_tween.tween_property(self, "_nudge_offset", Vector3.ZERO, nudge_duration * 0.5)


func _aim() -> void:
	if look_target == null:
		return
	look_at(look_target.global_position + Vector3.UP * look_height_offset, Vector3.UP)
