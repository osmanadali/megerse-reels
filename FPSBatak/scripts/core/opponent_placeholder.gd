class_name OpponentPlaceholder
extends Node3D
## Masadaki rakibin görsel düğümü (sandalye + karakter + isim + söz balonu).
##
## Hem yer tutucu (kapsül gövde) hem gerçek karakter sahneleri (ör. Dayı) bu
## sınıfı kullanır; oyun yalnızca bu arayüzü bilir: set_info, get_hand_anchor,
## say, hide_bubble. Karakterler yalnızca görseldir: oynayış, zorluk ve AI
## karakterden bağımsızdır.
## Yerel -Z yönü masanın ortasına bakar.

@export var display_name := "Rakip"
@export var body_color := Color(0.5, 0.5, 0.5)
## Yer tutucu gövdeyi `body_color` ile boyar. Kendi malzemeleri olan
## karakterlerde kapalıdır.
@export var apply_tint := true
@onready var _name_label: Label3D = $NameLabel
@onready var _hand_anchor: Marker3D = $HandAnchor
@onready var _bubble: Label3D = $Bubble

var _bubble_tween: Tween


func _ready() -> void:
	_name_label.text = display_name
	# Elindeki kart görünümü eklendiğinde kart oynama jestine bağlan (varsa).
	_hand_anchor.child_entered_tree.connect(_on_hand_view_added)
	if not apply_tint:
		return
	var body := get_node_or_null("Body") as MeshInstance3D
	var head := get_node_or_null("Head") as MeshInstance3D
	if body == null or head == null:
		return
	var mat := StandardMaterial3D.new()
	mat.albedo_color = body_color
	mat.roughness = 0.8
	body.material_override = mat
	var head_mat := mat.duplicate() as StandardMaterial3D
	head_mat.albedo_color = body_color.lightened(0.25)
	head.material_override = head_mat


func _on_hand_view_added(child: Node) -> void:
	var gesture := get_node_or_null("Gesture")
	if gesture and child.has_signal("card_taken") and gesture.has_method("play"):
		child.card_taken.connect(gesture.play)


## İsim plakasının ikinci satırı (ör. "2 el · 15 puan").
func set_info(line: String) -> void:
	_name_label.text = display_name if line.is_empty() else "%s\n%s" % [display_name, line]


## Karakterin kartları tuttuğu nokta. Yerel +Z karaktere doğru bakar.
func get_hand_anchor() -> Node3D:
	return _hand_anchor


## Başının üstünde kısa bir söz balonu gösterir ("7", "PAS", "Koz ♥"...).
## `duration` <= 0 ise balon kapatılana kadar kalır.
func say(text: String, duration := 1.6) -> void:
	if _bubble_tween and _bubble_tween.is_valid():
		_bubble_tween.kill()
	_bubble.text = text
	_bubble.visible = true
	_bubble.scale = Vector3.ONE * 0.6
	_bubble_tween = create_tween()
	_bubble_tween.tween_property(_bubble, "scale", Vector3.ONE, 0.12).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	if duration > 0.0:
		_bubble_tween.tween_interval(duration)
		_bubble_tween.tween_callback(func(): _bubble.visible = false)


func hide_bubble() -> void:
	_bubble.visible = false
