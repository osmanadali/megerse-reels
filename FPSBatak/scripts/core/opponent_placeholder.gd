class_name OpponentPlaceholder
extends Node3D
## Rakip için geçici yer tutucu (sandalye + gövde + baş + isim).
##
## İleride karakter sistemi (Dinozor, Kurt, Robot...) bu düğümün yerine
## gerçek modeli koyacak. Şimdilik sadece masada üç kişinin oturduğu hissini
## vermek ve koltuk konumlarını göstermek için var.
## Yerel -Z yönü masanın ortasına bakar.

@export var display_name := "Rakip"
@export var body_color := Color(0.5, 0.5, 0.5)

@onready var _body: MeshInstance3D = $Body
@onready var _head: MeshInstance3D = $Head
@onready var _name_label: Label3D = $NameLabel
@onready var _hand_anchor: Marker3D = $HandAnchor


func _ready() -> void:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = body_color
	mat.roughness = 0.8
	_body.material_override = mat
	var head_mat := mat.duplicate() as StandardMaterial3D
	head_mat.albedo_color = body_color.lightened(0.25)
	_head.material_override = head_mat
	_name_label.text = display_name


## Karakterin kartları tuttuğu nokta. Yerel +Z karaktere doğru bakar.
func get_hand_anchor() -> Node3D:
	return _hand_anchor
