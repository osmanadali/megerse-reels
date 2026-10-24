extends Node
## Kart oynarken kısa el/kol jesti (yalnızca görsel; iskelet gerekmez):
## kol omuz pivotundan kart bloğuna uzanır ("kartı alır"), masaya doğru
## bırakır, sonra dinlenme pozuna döner. Toplam ~0,5 sn, tween tabanlı.

@export var arm: Node3D
## Kart bloğuna uzanma pozu: omuz dönüşü (x: kaldırma, y: içe çevirme, radyan) ve kayma (m).
@export var pick_rotation := Vector3(0.25, 0.35, 0.0)
@export var pick_offset := Vector3(-0.02, 0.02, 0.02)
## Masaya bırakma pozu.
@export var play_rotation := Vector3(-0.04, 0.24, 0.0)
@export var play_offset := Vector3(-0.01, -0.012, -0.06)
@export var pick_time := 0.1
@export var play_time := 0.14
@export var back_time := 0.26

var _rest: Transform3D
var _tween: Tween


func _ready() -> void:
	if arm:
		_rest = arm.transform


func play() -> void:
	if arm == null:
		return
	if _tween and _tween.is_valid():
		_tween.kill()
	_tween = create_tween().set_trans(Tween.TRANS_SINE)
	_tween.tween_property(arm, "transform", _pose(pick_rotation, pick_offset), pick_time).set_ease(Tween.EASE_OUT)
	_tween.tween_property(arm, "transform", _pose(play_rotation, play_offset), play_time).set_ease(Tween.EASE_IN_OUT)
	_tween.tween_property(arm, "transform", _rest, back_time).set_ease(Tween.EASE_IN_OUT)


func _pose(rot: Vector3, offset: Vector3) -> Transform3D:
	return Transform3D(_rest.basis * Basis.from_euler(rot), _rest.origin + offset)
