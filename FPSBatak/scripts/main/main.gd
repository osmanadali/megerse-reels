extends Node3D
## Ana sahne: masa, kamera ve (şimdilik) deste sisteminin duman testi.
##
## Faz 1–2: sahne yüklendiğinde bir deste oluşturulur, karıştırılır ve dört
## oyuncuya dağıtılır; sonuç konsola ve ekranın altına yazılır. Görsel kartlar
## ve dağıtım animasyonu sonraki fazda bu düğüme bağlanacak.

@onready var _debug_info: Label = $HUD/DebugInfo

var deck: DeckManager


func _ready() -> void:
	deck = DeckManager.new()
	deck.shuffle()
	var hands := deck.deal()
	for seat in hands.size():
		print("%s: %s" % [Seat.NAMES_TR[seat], hands[seat]])
	var my_hand: Array = hands[Seat.LOCAL_PLAYER]
	_debug_info.text = "Elin (%d kart): %s" % [my_hand.size(), " ".join(my_hand.map(func(c): return c.get_short_label()))]


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_tree().quit()
