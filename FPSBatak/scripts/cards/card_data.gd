class_name CardData
extends Resource
## Tek bir iskambil kartının saf verisi.
##
## Bu sınıf yalnızca kural/veri tarafındadır: 3D model, animasyon veya UI
## bilgisi içermez. Görsel taraf (CardView vb.) bir CardData'yı okuyarak
## kendini çizer. Böylece kart tasarımı/deste teması oyun mantığına
## dokunmadan değiştirilebilir.

## Takımlar. Sıra, eldeki kartları sıralarken kullanılan varsayılan sıradır.
enum Suit { SPADES, HEARTS, DIAMONDS, CLUBS }

## Değerler. Sayısal karşılıkları güç sırasıdır (As en büyük).
enum Rank {
	TWO = 2, THREE = 3, FOUR = 4, FIVE = 5, SIX = 6, SEVEN = 7, EIGHT = 8,
	NINE = 9, TEN = 10, JACK = 11, QUEEN = 12, KING = 13, ACE = 14,
}

const SUIT_SYMBOLS := {
	Suit.SPADES: "♠", Suit.HEARTS: "♥", Suit.DIAMONDS: "♦", Suit.CLUBS: "♣",
}
const SUIT_NAMES_TR := {
	Suit.SPADES: "Maça", Suit.HEARTS: "Kupa", Suit.DIAMONDS: "Karo", Suit.CLUBS: "Sinek",
}
## Kart kimliklerinde ve ileride doku dosya adlarında kullanılan kısa kodlar.
const SUIT_CODES := {
	Suit.SPADES: "S", Suit.HEARTS: "H", Suit.DIAMONDS: "D", Suit.CLUBS: "C",
}
const RANK_LABELS := {
	Rank.TWO: "2", Rank.THREE: "3", Rank.FOUR: "4", Rank.FIVE: "5",
	Rank.SIX: "6", Rank.SEVEN: "7", Rank.EIGHT: "8", Rank.NINE: "9",
	Rank.TEN: "10", Rank.JACK: "J", Rank.QUEEN: "Q", Rank.KING: "K", Rank.ACE: "A",
}
const RANK_NAMES_TR := {
	Rank.TWO: "İkili", Rank.THREE: "Üçlü", Rank.FOUR: "Dörtlü", Rank.FIVE: "Beşli",
	Rank.SIX: "Altılı", Rank.SEVEN: "Yedili", Rank.EIGHT: "Sekizli", Rank.NINE: "Dokuzlu",
	Rank.TEN: "Onlu", Rank.JACK: "Vale", Rank.QUEEN: "Kız", Rank.KING: "Papaz", Rank.ACE: "As",
}

@export var suit: Suit = Suit.SPADES
@export var rank: Rank = Rank.ACE
## İsteğe bağlı kart yüzü dokusu. Boşsa görsel katman kartı prosedürel çizer.
@export var face_texture: Texture2D


## Yeni bir kart oluşturur.
static func create(p_suit: Suit, p_rank: Rank) -> CardData:
	var card := CardData.new()
	card.suit = p_suit
	card.rank = p_rank
	return card


## Benzersiz kimlik, ör. "S_A" (Maça As), "H_10" (Kupa 10).
## Doku temalarında dosya adı olarak da kullanılabilir: "<tema>/S_A.png".
func get_id() -> String:
	return "%s_%s" % [SUIT_CODES[suit], RANK_LABELS[rank]]


## Karşılaştırmada kullanılan güç değeri (2..14).
func get_value() -> int:
	return int(rank)


func get_suit_symbol() -> String:
	return SUIT_SYMBOLS[suit]


func get_rank_label() -> String:
	return RANK_LABELS[rank]


## Kısa gösterim, ör. "A♠".
func get_short_label() -> String:
	return get_rank_label() + get_suit_symbol()


## Türkçe uzun ad, ör. "Maça As".
func get_display_name() -> String:
	return "%s %s" % [SUIT_NAMES_TR[suit], RANK_NAMES_TR[rank]]


func is_red() -> bool:
	return suit == Suit.HEARTS or suit == Suit.DIAMONDS


func same_as(other: CardData) -> bool:
	return other != null and other.suit == suit and other.rank == rank


## Eldeki kartları sıralamak için: önce takım, sonra büyükten küçüğe değer.
static func sort_for_hand(a: CardData, b: CardData) -> bool:
	if a.suit != b.suit:
		return a.suit < b.suit
	return a.rank > b.rank


func _to_string() -> String:
	return get_short_label()
