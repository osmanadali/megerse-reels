extends Node
## Blender'dan gelen karakter modelinin yüzeylerine üç paylaşılan malzemeyi
## atar: "Cloth" (kumaş: vertex color × örgü dokusu), "Smooth" (ten, ahşap,
## porselen: vertex color) ve "Metal" (gözlük). Renkler modelin vertex
## color'ında olduğu için karakter başına en fazla 3 malzeme ve parça başına
## 2–3 çizim çağrısı kalır (mobil bütçe). Yalnızca görsel.

@export var model: Node3D
@export var cloth: Material
@export var smooth: Material
@export var metal: Material


func _ready() -> void:
	if model == null:
		return
	for mi: MeshInstance3D in model.find_children("*", "MeshInstance3D", true, false):
		for i in mi.mesh.get_surface_count():
			var src := mi.mesh.surface_get_material(i)
			var n := src.resource_name if src else ""
			var m: Material = smooth
			if n.begins_with("Cloth"):
				m = cloth
			elif n.begins_with("Metal"):
				m = metal
			mi.set_surface_override_material(i, m)
