class_name Sfx
extends Node
## Oyun efektleri. Şimdilik sesler kodla üretilen yer tutucu seslerdir
## (filtrelenmiş kısa gürültü patlamaları). İleride gerçek kayıtlarla
## değiştirmek için `_streams` sözlüğüne AudioStream atamak yeterli.

const MIX_RATE := 22050
const VOICES := 6

var _streams := {}
var _players: Array[AudioStreamPlayer] = []
var _next := 0


func _ready() -> void:
	# isim -> [süre sn, düşük geçiren katsayısı (0..1, küçük = boğuk), ses seviyesi]
	_streams["card_place"] = _noise_burst(0.09, 0.35, 0.9)
	_streams["card_deal"] = _noise_burst(0.045, 0.6, 0.45)
	_streams["trick_collect"] = _noise_burst(0.16, 0.2, 0.7)
	for i in VOICES:
		var p := AudioStreamPlayer.new()
		add_child(p)
		_players.append(p)


func play(sound: String, pitch_jitter := 0.08) -> void:
	if not _streams.has(sound):
		return
	var p := _players[_next]
	_next = (_next + 1) % _players.size()
	p.stream = _streams[sound]
	p.pitch_scale = 1.0 + randf_range(-pitch_jitter, pitch_jitter)
	p.play()


## Hızla sönen, tek kutuplu filtreden geçmiş beyaz gürültü: kağıt "şap" sesi.
static func _noise_burst(duration: float, lowpass: float, volume: float) -> AudioStreamWAV:
	var count := int(duration * MIX_RATE)
	var data := PackedByteArray()
	data.resize(count * 2)
	var y := 0.0
	for i in count:
		var t := float(i) / count
		var env: float = exp(-6.0 * t) * min(1.0, t * 40.0)
		y += lowpass * (randf_range(-1.0, 1.0) - y)
		data.encode_s16(i * 2, int(clamp(y * env * volume, -1.0, 1.0) * 32767.0))
	var wav := AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = MIX_RATE
	wav.data = data
	return wav
