extends Node3D
## Ana sahne kökü. Oyun akışı TableController'da; burası yalnızca genel
## kısayolları yönetir.


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_tree().quit()
