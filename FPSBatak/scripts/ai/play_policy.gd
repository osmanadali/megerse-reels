class_name PlayPolicy
extends RefCounted
## Kart oynama strateji motoru (deterministik, aday kart puanlama).
##
## Kurallar burada YOKTUR: aday kartlar her zaman BatakRules.legal_cards()
## listesidir (PlayContext.legal) ve seçim yalnızca bu listeden yapılır.
## Strateji, her yasal kartı puanlayıp en yükseğini seçer:
##
##   puan = V₀ × P(bu kartla löveyi alırım) − V₀ × gelecek_değeri(kart)
##          [+ savunan için: DENY × P(löve ihale sahibine GİTMEZ)] + bağlam terimleri
##
## - V (lövenin değeri) role göre değişir: ihale sahibi için ihtiyacı kadar
##   aciliyet; savunan için ihale sahibini durdurma ve sıfır löve cezasından
##   kaçınma. Bunlar sabit kural değil, ağırlıktır.
## - P(alırım): benden sonra oynayacakların (açık bilgiye göre) bu kartı
##   geçme ihtimali. Mecburi yükseltme kuralı gereği daha büyük kartı olan
##   oyuncu onu oynamak ZORUNDA; renk boşluğu olan da koz atmak zorunda.
##   Bu yüzden geçebilecek kartın kimde olabileceği hesaplanır.
## - V₀: role göre bir lövenin taban değeri. Saklanan kart da ileride aynı
##   değerde löve alacağı için gelecek değeri de bununla ölçeklenir; yoksa
##   rol bonusları kartları erken harcatır (ölçümle bulundu).
## - gelecek_değeri: kartı saklasaydım ileride löve alma ihtimali (renginin en
##   büyüğü mü, kaç büyük kart dışarıda). Oyun sonuna doğru azalır.
##
## Zorluk: NORMAL yalnızca kesin bilinen renk boşluklarını kullanır; HARD
## bilinmeyen boşlukları da olasılıkla tahmin eder (probabilistic = true).

## Ağırlıklar (simülasyonla ayarlandı; bkz. tools/ai/benchmark_play.gd).
## Ölçüm aracının deneme yapabilmesi için sözlükte tutulur; oyunda değişmez.
static var W := {
	"BIDDER_URGENCY": 0.5,
	"DEFENDER_DENY": 0.8,
	"DEFENDER_ZERO": 0.3,
	"DEFENDER_ZERO_LATE": 0.3,
	"FUTURE_DISCOUNT_BIDDER": 0.6,    # ihale sahibi kazananlarını erken alır (rakipler sonra keser)
	"FUTURE_DISCOUNT_DEFENDER": 0.9,  # savunan büyük kartlarını saklar
	"TRUMP_CONTROL": 0.1,
	"GUARD_PENALTY": 0.2,
	"VOID_BONUS": 0.15,
	"PROMOTE_BONUS": 0.5,
	"DRAW_TRUMP_MAJOR": 0.0,          # ölçüm: sabit koz çekme ödülü zararlı (koz açmanın
	"DRAW_TRUMP_MINOR": 0.0,          # değeri zaten P(alırım) teriminde)
	"FORCE_RUFF_BONUS": 1.0,          # savunan: ihale sahibini kozla kesmeye zorlamak (koz eritme)
}
const ENDGAME_TRICKS := 4


static func choose(ctx: PlayContext, probabilistic := false) -> CardData:
	# Savunan takip ederken kazanan kart varsa (mecburi yükseltme gereği bu
	# durumda yasal kartların hepsi kazanandır) en küçük kazananı oynar:
	# ucuz kartla girmek, arkadaki ihale sahibini büyük kartını harcamaya
	# ZORLAR; arkadaki başka savunan geçerse löve yine savunmada kalır.
	# Ölçüm (3000 el, eski ihale sahibine karşı): puanlamalı seçim 5,756 löve /
	# %85,4 tutma; en küçük kazanan 5,671 / %83,4 (ihale sahibi için daha kötü).
	# İhale sahibinde ise puanlama daha iyi ölçüldü (5,783 vs 5,746).
	if not ctx.is_leading() and not ctx.is_bidder():
		var cur: CardData = ctx.trick[BatakRules.trick_winner(ctx.trick, ctx.trump)]
		var led: int = ctx.trick[0].suit
		var wins: Array[CardData] = ctx.legal.filter(
			func(c: CardData): return BatakRules.beats(c, cur, led, ctx.trump))
		if not wins.is_empty():
			return AIPlayer._lowest(wins)
	var info := _Info.new(ctx, probabilistic)
	var best: CardData = null
	var best_score := -INF
	for c in ctx.legal:
		var s := score(c, ctx, info)
		if best == null or s > best_score + 1e-9 or (absf(s - best_score) <= 1e-9 and c.rank < best.rank):
			best = c
			best_score = s
	return best


## Bir adayın puanı (test ve açıklama için ayrı).
static func score(c: CardData, ctx: PlayContext, info: _Info) -> float:
	var v0 := _base_value(ctx)
	var s := -info.future_value(c) * v0
	var led_suit := c.suit if ctx.is_leading() else ctx.trick[0].suit
	var after := ctx.opponents() if ctx.is_leading() else ctx.players_after()
	var current_best: CardData = null if ctx.is_leading() \
		else ctx.trick[BatakRules.trick_winner(ctx.trick, ctx.trump)]
	var wins_now := ctx.is_leading() or BatakRules.beats(c, current_best, led_suit, ctx.trump)
	if ctx.is_bidder():
		if wins_now:
			s += _bidder_value(ctx) * info.p_hold(c, after, led_suit)
	else:
		# Savunan için iki ayrı soru: (1) löveyi BEN alır mıyım (kendi puanım),
		# (2) löve İHALE SAHİBİNE gider mi (onu batırmak). Arkadaki başka bir
		# savunanın geçmesi löveyi ihale sahibinden uzak tutar; kayıp değildir.
		if wins_now:
			s += v0 * info.p_hold(c, after, led_suit)
		if ctx.tricks_needed() > 0:
			s += PlayPolicy.W.DEFENDER_DENY * (1.0 - _p_bidder_takes(c, wins_now, current_best,
				after, led_suit, ctx, info))
	if ctx.is_leading():
		s += _lead_terms(c, ctx, info)
	elif c.suit != led_suit and c.suit != ctx.trump:  # serbest atış
		s += _discard_terms(c, ctx, info)
	return s


## Savunanın bakışından: bu kartı oynarsam löveyi ihale sahibinin alma olasılığı.
static func _p_bidder_takes(c: CardData, wins_now: bool, current_best: CardData, after: Array,
		led_suit: int, ctx: PlayContext, info: _Info) -> float:
	var target: CardData = c if wins_now else current_best
	var others := after.filter(func(x): return x != ctx.bidder)
	if not wins_now and ctx.trick_seats[ctx.trick.find(current_best)] == ctx.bidder:
		# İhale sahibi şu an kazanıyor; arkadaki savunanlar geçemezse onundur.
		return info.p_hold(target, others, led_suit)
	if not after.has(ctx.bidder):
		return 0.0
	# İhale sahibi arkada: hedef kartı geçer ve ondan sonrakiler onu geçemezse alır.
	return 1.0 - info.p_hold(target, [ctx.bidder], led_suit)


# --- Lövenin değeri (role göre) -------------------------------------------------

static func _base_value(ctx: PlayContext) -> float:
	if ctx.is_bidder():
		var need := ctx.tricks_needed()
		if need <= 0:
			return 1.0
		return 1.0 + PlayPolicy.W.BIDDER_URGENCY * clampf(float(need) / maxi(ctx.remaining_tricks(), 1), 0.0, 1.0)
	var v := 1.0
	if ctx.tricks_won()[ctx.seat] == 0:
		v += PlayPolicy.W.DEFENDER_ZERO
		if ctx.remaining_tricks() <= ENDGAME_TRICKS:
			v += PlayPolicy.W.DEFENDER_ZERO_LATE
	return v


static func _bidder_value(ctx: PlayContext) -> float:
	return _base_value(ctx)


# --- Açılış terimleri ------------------------------------------------------------

static func _lead_terms(c: CardData, ctx: PlayContext, info: _Info) -> float:
	var s := 0.0
	var own_suit := info.own_suit_cards(c.suit)
	# Dizinin üstünü açmak: tek büyük kart dışarıdaysa onu çıkarır, alttaki kesinleşir.
	if c.suit != ctx.trump and info.unseen_higher(c).size() == 1 and info.has_rank(c.suit, c.rank - 1):
		s += PlayPolicy.W.PROMOTE_BONUS
	# Büyük kartı koruyan tek küçük kartı açmamak.
	s -= info.guard_penalty(c)
	if c.suit == ctx.trump:
		if ctx.is_bidder():
			var opp_trumps := info.unseen_trump_count()
			if opp_trumps > 0:
				s += PlayPolicy.W.DRAW_TRUMP_MAJOR if info.own_trump_count() >= opp_trumps else PlayPolicy.W.DRAW_TRUMP_MINOR
	else:
		# Kozu varken tek kartlı rengi açıp boşaltmak (ileride kesmek için).
		if own_suit.size() == 1 and info.own_trump_count() > 0 and not info.is_master(c):
			s += PlayPolicy.W.VOID_BONUS
		# Savunan: ihale sahibinin boş olduğu rengi açıp onu kozla kesmeye zorlamak
		# kozunu eritir; kozu azalan ihale sahibi uzun renklerini koruyamaz.
		# (İlk sürümde bu "ucuz löve verme" diye CEZAYDI; ölçüm tersini gösterdi:
		# gömmelide eski ihale sahibine karşı ceza 0,6 → %83,0 tutma, ödül 1,0 → %74,2.
		# Ödül 1,0'ın üstünde değişmiyor.)
		if not ctx.is_bidder():
			s += PlayPolicy.W.FORCE_RUFF_BONUS * info.p_void(ctx.bidder, c.suit) * info.p_has_trump(ctx.bidder)
	return s


# --- Atış terimleri --------------------------------------------------------------

static func _discard_terms(c: CardData, ctx: PlayContext, info: _Info) -> float:
	var s := -info.guard_penalty(c)
	if info.own_suit_cards(c.suit).size() == 1 and info.own_trump_count() > 0:
		s += PlayPolicy.W.VOID_BONUS
	return s


## Karar anındaki ön hesaplar: görünmeyen kartlar, kimin neyi tutabileceği.
class _Info:
	var ctx: PlayContext
	var probabilistic: bool
	var unseen_by_suit := [[], [], [], []]  # takım -> [değerler] (göremediklerim)
	var own_by_suit := [[], [], [], []]
	var hidden: int
	var _cache := {}  # aynı karar içinde tekrar eden olasılıklar (sonucu değiştirmez)

	func _init(p_ctx: PlayContext, p_prob: bool) -> void:
		ctx = p_ctx
		probabilistic = p_prob
		hidden = ctx.unknown_buried()
		for c in ctx.unseen():
			unseen_by_suit[c.suit].append(int(c.rank))
		for c in ctx.own_hand:
			own_by_suit[c.suit].append(c)

	func own_suit_cards(suit: int) -> Array:
		return own_by_suit[suit]

	func has_rank(suit: int, rank: int) -> bool:
		return own_by_suit[suit].any(func(x): return x.rank == rank)

	func own_trump_count() -> int:
		return own_by_suit[ctx.trump].size()

	func unseen_trump_count() -> int:
		return unseen_by_suit[ctx.trump].size()

	func unseen_higher(c: CardData) -> Array:
		return unseen_by_suit[c.suit].filter(func(r): return r > c.rank)

	func is_master(c: CardData) -> bool:
		return unseen_higher(c).is_empty()

	## Görünmeyen bir kartın `seat` oyuncusunda olma olasılığı (açık bilgiye göre).
	func p_holds(seat: int, suit: int, rank: int) -> float:
		var k := seat * 1000 + suit * 100 + rank
		if _cache.has(k):
			return _cache[k]
		var tr := ctx.tracker
		var total := float(hidden)
		var mine := 0.0
		for s in ctx.opponents():
			if not tr.voids[s][suit] and rank < tr.suit_cap[s][suit]:
				var w := float(tr.hand_size(s))
				total += w
				if s == seat:
					mine = w
		var p := 0.0 if total <= 0.0 else mine / total
		_cache[k] = p
		return p

	## Oyuncunun o renkte boş olma olasılığı (NORMAL: yalnızca kesin bilgi).
	func p_void(seat: int, suit: int) -> float:
		if ctx.tracker.voids[seat][suit]:
			return 1.0
		if not probabilistic:
			return 0.0
		var p := 1.0
		for r in unseen_by_suit[suit]:
			p *= 1.0 - p_holds(seat, suit, r)
		return p

	func p_has_trump(seat: int) -> float:
		if ctx.tracker.voids[seat][ctx.trump]:
			return 0.0
		var none := 1.0
		for r in unseen_by_suit[ctx.trump]:
			none *= 1.0 - p_holds(seat, ctx.trump, r)
		return 1.0 - none

	func _p_has_higher(seat: int, suit: int, rank: int) -> float:
		var none := 1.0
		for r in unseen_by_suit[suit]:
			if r > rank:
				none *= 1.0 - p_holds(seat, suit, r)
		return 1.0 - none

	## `c` (şu an kazanan olacak kart), `after` oyuncuları oynadıktan sonra da
	## kazanır mı? Mecburi yükseltme: daha büyüğünü tutan onu oynamak zorunda;
	## açılan renkte boş olan koz atmak (ve kozda yükseltmek) zorunda.
	func p_hold(c: CardData, after: Array, led_suit: int) -> float:
		var trump := ctx.trump
		var p := 1.0
		for s in after:
			if c.suit == trump:
				if led_suit == trump:
					p *= 1.0 - _p_has_higher(s, trump, c.rank)
				else:
					p *= 1.0 - p_void(s, led_suit) * _p_has_higher(s, trump, c.rank)
			else:
				var lose := _p_has_higher(s, c.suit, c.rank)
				lose += (1.0 - lose) * p_void(s, c.suit) * p_has_trump(s)
				p *= 1.0 - lose
		return p

	## Kartı saklamanın değeri: oyunun sonuna kadar bu kartla löve alma olasılığı.
	## Batak'ta her kart sonunda oynanır: üstündeki büyük kartlar (k tane) er geç
	## çıkar; elde onları beklerken atılabilecek küçük kartlar (koruma) varsa
	## kart harcanmadan kalır ve sonunda kesinleşir. Kesilme (koz) riski ve oyun
	## sonu ufku bunu azaltır. (İlk sürüm "şimdi açılsa alır mı"ya bakıyordu; bu
	## büyük kartları erken harcattı — ölçümle bulundu.)
	func future_value(c: CardData) -> float:
		var left := ctx.remaining_tricks() - 1
		if left <= 0:
			return 0.0
		var k := unseen_higher(c).size()
		var guards: int = own_by_suit[c.suit].filter(func(x): return x.rank < c.rank).size()
		var eventual := 1.0
		if k > 0:
			eventual = minf(1.0, float(guards) / k) * pow(0.75, k - 1)
			if k > left:
				eventual = 0.0  # üstündekiler oyun bitmeden çıkamaz
		if c.suit != ctx.trump:
			eventual *= 1.0 - _ruff_risk(c.suit)
		var fd: float = PlayPolicy.W.FUTURE_DISCOUNT_BIDDER if ctx.is_bidder() \
			else PlayPolicy.W.FUTURE_DISCOUNT_DEFENDER
		var v: float = fd * eventual
		if c.suit == ctx.trump:
			v += PlayPolicy.W.TRUMP_CONTROL * c.rank / 14.0
		return v * clampf(float(left) / 3.0, 0.0, 1.0)

	## Bir rengin herhangi bir rakip tarafından kozla kesilme riski (açık bilgiye göre).
	func _ruff_risk(suit: int) -> float:
		var risk := 0.0
		for s in ctx.opponents():
			risk = maxf(risk, p_void(s, suit) * p_has_trump(s))
		return risk

	## Büyük kartı (Q ve üstü, renginin en büyüğü değil) koruyan tek küçük kartı vermenin bedeli.
	func guard_penalty(c: CardData) -> float:
		var suit_cards: Array = own_by_suit[c.suit]
		if c.suit == ctx.trump or suit_cards.size() != 2:
			return 0.0
		var other: CardData = suit_cards[0] if suit_cards[1] == c else suit_cards[1]
		if other.rank >= 12 and other.rank > c.rank and not is_master(other):
			return PlayPolicy.W.GUARD_PENALTY
		return 0.0
