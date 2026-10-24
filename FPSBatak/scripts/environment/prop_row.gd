extends MultiMeshInstance3D
## Aynı küçük nesneyi (çay bardağı, şişe...) bir sıra hâlinde dizer.
##
## Tek bir MultiMesh = tek çizim çağrısı: rafta onlarca bardak mobil GPU'ya
## tek nesne kadar yük getirir. Yalnızca dekor; oyun mantığı bilmez.

@export var item_mesh: Mesh
@export var count := 8
## Yerel X ekseni boyunca aralık (m).
@export var spacing := 0.12
## Her öğeye küçük, tekrarlanabilir bir kayma/dönme (doğal görünüm için).
@export var jitter := 0.012
@export var seed_value := 1


func _ready() -> void:
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = item_mesh
	mm.instance_count = count
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_value
	var start := -spacing * (count - 1) * 0.5
	for i in count:
		var pos := Vector3(start + i * spacing + rng.randf_range(-jitter, jitter), 0.0,
			rng.randf_range(-jitter, jitter))
		var basis := Basis(Vector3.UP, rng.randf_range(-PI, PI))
		mm.set_instance_transform(i, Transform3D(basis, pos))
	multimesh = mm
