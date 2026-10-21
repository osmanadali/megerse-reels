class_name BidStrategy
extends RefCounted
## İhale AI'sının 4. ve 5. adımı: İHALE DURUMU ANALİZİ → SON TEKLİF.
##
## Akış:
##   EL ANALİZİ (HandAnalysis)
##   → BEKLENEN LÖVE (TrickEstimator.best: en iyi koz ve μ, σ)
##   → TEKLİF BAŞARI OLASILIĞI (P(löve ≥ k) her teklif seviyesi için)
##   → İHALE DURUMU (BidContext: masadaki teklif, pas diyenler, zorunlu ihale)
##   → SON TEKLİF
##
## Kural: AI en fazla, tutma olasılığı eşiğin üstünde kalan en yüksek seviyeye
## kadar çıkar ve her seferinde yalnızca geçerli en küçük teklifi söyler
## (rastgele yüksek teklif yok, atlama yok).
##
## Zorunlu ihale bağlamı: Kimse teklif vermemişken herkes pas derse ihale
## zaten bu oyuncuya (dağıtanın sağındakine) kalacaksa, pas demek riski
## ortadan kaldırmaz; bu oyuncu en düşük teklifi daha düşük bir eşikle söyler.
##
## Eşikler simülasyonla seçildi (tools/ai/benchmark_bidding.gd); seçimin
## gerekçesi rapor/README'de.

## Bir teklif seviyesine girmek için gereken en düşük tutma olasılığı.
const THRESHOLD := {
	GameRules.Mode.STANDARD_BIDDING: 0.60,
	GameRules.Mode.BURIED_BIDDING: 0.60,
}
## Zorunlu ihaleyi zaten alacak oyuncu, kimse teklif vermemişken en düşük
## teklif için bu eşiği kullanır.
const RECIPIENT_THRESHOLD := {
	GameRules.Mode.STANDARD_BIDDING: 0.50,
	GameRules.Mode.BURIED_BIDDING: 0.50,
}

## Ölçüm aracının farklı eşikleri denemesi için (oyunda kullanılmaz; <0 = kapalı).
static var override_threshold := -1.0
static var override_recipient_threshold := -1.0


## Kararı ve gerekçesini döndürür:
## {bid (0=PAS), trump, mu, sigma, max_ok, p_first (geçerli ilk teklifin tutma olasılığı), reason}
static func decide(hand: Array[CardData], ctx: BidContext, mu_shift := 0.0) -> Dictionary:
	var r := ctx.rules
	var e := TrickEstimator.best(hand, r)
	var mu: float = e.mu + mu_shift
	var sigma: float = e.sigma
	var t := override_threshold if override_threshold >= 0.0 else float(THRESHOLD[r.mode])
	var max_ok := 0
	for b in range(r.min_bid, r.max_bid + 1):
		if TrickEstimator.prob_at_least(b, mu, sigma) >= t:
			max_ok = b
	var out := {"bid": BidManager.PASS, "trump": e.trump, "mu": mu, "sigma": sigma,
		"max_ok": max_ok, "p_first": 0.0, "reason": ""}
	if ctx.valid.is_empty():
		out.reason = "geçerli teklif yok"
		return out
	var first: int = ctx.valid[0]
	out.p_first = TrickEstimator.prob_at_least(first, mu, sigma)
	if first <= max_ok:
		out.bid = first
		out.reason = "P(≥%d)=%.0f%% ≥ eşik %.0f%%" % [first, out.p_first * 100, t * 100]
		return out
	if ctx.nobody_bid() and ctx.i_am_all_pass_recipient():
		var tr := override_recipient_threshold if override_recipient_threshold >= 0.0 \
			else float(RECIPIENT_THRESHOLD[r.mode])
		if out.p_first >= tr:
			out.bid = first
			out.reason = "herkes pas derse zorunlu %d bana kalacak; P(≥%d)=%.0f%% ≥ %.0f%%" % [
				ctx.all_pass_bid, first, out.p_first * 100, tr * 100]
			return out
	out.reason = "P(≥%d)=%.0f%% eşiğin altında" % [first, out.p_first * 100]
	return out
