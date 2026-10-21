extends Node
## Karakterin sakin bekleme hareketi: nefes, yavaş baş hareketi, sigara
## ucunun hafif parlaması. İskelet/animasyon dosyası gerektirmez; birkaç
## düğümün dönüşümünü sinüsle oynatır (mobilde ihmal edilebilir maliyet).
## Yalnızca görsel: oyun mantığını bilmez.

@export var torso: Node3D
@export var head: Node3D
@export var ember: Node3D
## Nefes: gövde yüksekliğinde oransal salınım ve saniyedeki nefes sayısı.
@export var breath_amount := 0.012
@export var breath_rate := 0.23
## Baş: yavaş sağa-sola bakma ve hafif öne-arkaya (radyan).
@export var head_yaw := 0.07
@export var head_pitch := 0.025

var _t := 0.0
var _torso_scale := Vector3.ONE
var _head_basis := Basis()
var _phase := 0.0


func _ready() -> void:
	_phase = randf() * TAU  # masadaki karakterler aynı anda nefes almasın
	if torso:
		_torso_scale = torso.scale
	if head:
		_head_basis = head.transform.basis


func _process(delta: float) -> void:
	_t += delta
	var p := _t + _phase
	if torso:
		torso.scale = _torso_scale * Vector3(1.0, 1.0 + sin(p * TAU * breath_rate) * breath_amount, 1.0)
	if head:
		var yaw := sin(p * 0.11 * TAU) * head_yaw + sin(p * 0.031 * TAU) * head_yaw * 0.6
		var pitch := sin(p * 0.07 * TAU + 1.3) * head_pitch
		head.transform.basis = _head_basis * Basis(Vector3.UP, yaw) * Basis(Vector3.RIGHT, pitch)
	if ember:
		ember.scale = Vector3.ONE * (1.0 + 0.25 * maxf(0.0, sin(p * 0.4 * TAU)))
