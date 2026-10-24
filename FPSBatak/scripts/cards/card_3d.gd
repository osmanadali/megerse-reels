class_name Card3D
extends Node3D
## Masadaki fiziksel kartın görsel temsili.
##
## Yerel eksenler: kart yüzü +Z'ye bakar, kartın üstü +Y'dir (Sprite gibi).
## Masaya yüzü yukarı yatırmak için `table_basis()` kullanılır.
## Oyun mantığı bu sınıfı bilmez; yalnızca `card` verisini taşır.

## Okunabilirlik için gerçek kart boyutundan (~6.3x8.8 cm) bilerek büyük.
const SIZE := Vector2(0.13, 0.182)
## Vurgu çerçevesinin kart kenarından taşma payı.
const HIGHLIGHT_MARGIN := 0.012

static var _quad: QuadMesh
static var _highlight_quad: QuadMesh
static var _back_material: StandardMaterial3D
static var _highlight_material: StandardMaterial3D
static var _face_materials := {}  # kart kimliği -> materyal

var card: CardData
var _front: MeshInstance3D
var _back: MeshInstance3D
var _highlight: MeshInstance3D


func _init() -> void:
	if _quad == null:
		_quad = QuadMesh.new()
		_quad.size = SIZE
		_highlight_quad = QuadMesh.new()
		_highlight_quad.size = SIZE + Vector2.ONE * HIGHLIGHT_MARGIN * 2.0
	_front = MeshInstance3D.new()
	_front.mesh = _quad
	_front.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_front)
	_back = MeshInstance3D.new()
	_back.mesh = _quad
	_back.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_back.rotation.y = PI
	add_child(_back)
	_highlight = MeshInstance3D.new()
	_highlight.mesh = _highlight_quad
	_highlight.position.z = -0.0006
	_highlight.visible = false
	_highlight.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_highlight)


## Kartı veriye ve dokulara bağlar. `card_data` null ise kart kimliksiz,
## sadece arkası görünen bir kart olur (rakip elindeki kartlar gibi).
func setup(card_data: CardData, faces: CardFaceRenderer) -> void:
	card = card_data
	if _back_material == null:
		_back_material = _make_material(faces.get_back())
		_highlight_material = StandardMaterial3D.new()
		_highlight_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		_highlight_material.albedo_color = Color(1.0, 0.78, 0.25)
	_back.material_override = _back_material
	_highlight.material_override = _highlight_material
	if card == null:
		_front.material_override = _back_material
		return
	var id := card.get_id()
	if not _face_materials.has(id):
		_face_materials[id] = _make_material(faces.get_face(card))
	_front.material_override = _face_materials[id]


func set_highlighted(on: bool) -> void:
	_highlight.visible = on


## Masaya yatık kartın yönelimi. `face_up` yüzü yukarı; `yaw` masadaki dönüş.
## Kartın üst kenarı varsayılan olarak -Z'ye (oyuncudan uzağa) bakar.
static func table_basis(face_up: bool, yaw: float = 0.0) -> Basis:
	var tilt := -PI * 0.5 if face_up else PI * 0.5
	var b := Basis(Vector3.UP, yaw) * Basis(Vector3.RIGHT, tilt)
	if not face_up:
		b = b * Basis(Vector3.FORWARD, PI)  # arkadan bakınca üst kenar yine uzakta kalsın
	return b


## Kartı bir yay çizerek hedef dünya dönüşümüne taşır; yön yumuşakça döner.
func move_to(target: Transform3D, duration: float, arc_height: float = 0.05) -> Tween:
	var start := global_transform
	var start_q := start.basis.get_rotation_quaternion()
	var end_q := target.basis.get_rotation_quaternion()
	var start_s := start.basis.get_scale()
	var end_s := target.basis.get_scale()
	var tween := create_tween()
	tween.tween_method(func(t: float):
		var e := ease(t, -1.8)  # yumuşak başla, yumuşak bitir
		var pos := start.origin.lerp(target.origin, e)
		pos.y += sin(t * PI) * arc_height
		var b := Basis(start_q.slerp(end_q, e)) * Basis.from_scale(start_s.lerp(end_s, e))
		global_transform = Transform3D(b, pos)
	, 0.0, 1.0, duration)
	return tween


static func _make_material(tex: Texture2D) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_texture = tex
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
	m.alpha_scissor_threshold = 0.5
	m.roughness = 0.9
	# Lamba altında beyazların patlamaması için hafif kısık.
	m.albedo_color = Color(0.86, 0.86, 0.86)
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	return m
