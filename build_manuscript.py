# -*- coding: utf-8 -*-
"""EVT catastrophe-loss paper, v4 final (29 October 2026). Builds the manuscript (full / --blind / --ar-abstract) from evt_results.json;
no number in the text is typed by hand. Section 4 runs results -> robustness -> discussion. Writes analysis/wordcount.json on a full build."""
import json, sys, math, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); VER = os.path.dirname(HERE); FIGS = f"{VER}/figures"
_h = open(f"{HERE}/helpers_head.py", encoding="utf-8").read()
_h = _h.replace('R = json.load(open(f"{OUT}/results.json"))', 'R = {}'); _h = re.sub(r'^OUT = .*$', f'OUT = {VER!r}', _h, flags=re.M)
exec(_h)
from docx.enum.text import WD_COLOR_INDEX
R = json.load(open(f"{HERE}/evt_results.json")); D = R["datasets"]; names = list(D); V = R["review"]; EGF = json.load(open(f"{HERE}/egypt_fire.json"))
US, DK, NO, NZ, AU = [D[n] for n in names]; nUS, nDK, nNO, nNZ, nAU = names
short = {nUS: "U.S. disasters", nDK: "Danish fire", nNO: "Norwegian fire", nNZ: "New Zealand catastrophes", nAU: "Australian catastrophes"}
unit = {nUS: "USD m", nDK: "DKK m", nNO: "NOK k", nNZ: "NZD m", nAU: "AUD m"}
AR = "--ar-abstract" in sys.argv
REPO = "https://github.com/dr-elbehairy/evt-catastrophe-losses"
WCJ = json.load(open(f"{HERE}/wordcount.json")) if os.path.exists(f"{HERE}/wordcount.json") else {"main_text": 8000}

# ---- word counting (main text = Sections 1–5 body paragraphs; abstract counted separately; captions/notes/tables excluded)
_P0, _H0 = P, H
WC = {}; SEC = ["front"]
def P(text="", body=False, **kw):
    if (body or kw.get("indent")) and SEC[0] in ("1", "2", "3", "4", "5", "abstract"):
        WC[SEC[0]] = WC.get(SEC[0], 0) + len(re.sub(r"\*\*", "", text).split())
    return _P0(text, **kw)
def H(text, lvl=1):
    if lvl == 1:
        m = re.match(r"(\d)\.", text); SEC[0] = m.group(1) if m else ("abstract" if text == "Abstract" else "back")
    return _H0(text, lvl)

def f0(x): return "∞" if (x is None or (isinstance(x, float) and (math.isinf(x) or math.isnan(x)))) else f"{x:,.0f}"
def f1(x): return f"{x:,.1f}"
def f2(x): return f"{x:.2f}"
def bn(x): return f"{x/1000:,.0f}"
F = R["noaa_freq"]; AG = R["noaa_aggregate"]; LAY = R["layers"]; LAD = V["us_ladder"]["ladder"]; L90 = LAD["0.90"]; L50 = LAD["0.50"]
SEL = V["selection"]; CMP = V["comparators"]
MCA = V["us_ladder"].get("mc_p995_auto", {"cv": float("nan")})
LAD["0.90"] = dict(LAD["0.90"], agg_p995_2024=R["noaa_aggregate"]["fitted_rate_2024"]["p995"], agg_p995_recent=R["noaa_aggregate"]["mean_rate_2015_2024"]["p995"], agg_mean_2024=R["noaa_aggregate"]["fitted_rate_2024"]["mean"])
# headline shapes: automated fits for the four registers whose shape is stable; the high-threshold fit for the U.S. record
xi_head = {nUS: US["hi"]["xi"], nDK: DK["xi"], nNO: NO["xi"], nNZ: NZ["xi"], nAU: AU["xi"]}
ratio = {n: (D[n]["risk"]["0.995"]["TVaR"] / D[n]["risk"]["0.995"]["VaR"]) for n in (nDK, nNO, nAU)}; ratio[nUS] = US["hi"]["risk"]["0.995"]["TVaR"] / US["hi"]["risk"]["0.995"]["VaR"]
ratio_med_US = US["risk"]["0.995"]["TVaR"] / US["risk"]["0.995"]["VaR"]
under = {n: D[n]["compare"]["0.995"]["lognormal"] / D[n]["compare"]["0.995"]["gpd"] for n in names}
under_tr = {n: CMP[n]["auto"]["quantiles"]["0.995"]["trunc_lognormal"] / CMP[n]["auto"]["quantiles"]["0.995"]["gpd"] for n in names}
EXNZ = [nUS, nDK, nNO, nAU]
under_tr9 = {n: CMP[n]["auto"]["quantiles"]["0.999"]["trunc_lognormal"] / CMP[n]["auto"]["quantiles"]["0.999"]["gpd"] for n in names}
under_sh = {n: CMP[n]["auto"]["quantiles"]["0.995"]["shifted_lognormal"] / CMP[n]["auto"]["quantiles"]["0.995"]["gpd"] for n in names}
egp, egc = EGF["premiums_kEGP"], EGF["claims_kEGP"]; lr = {k: egc[k] / egp[k] for k in egp}
lr_other_min = 100 * min(lr[k] for k in lr if k != "2018/19"); lr_other_max = 100 * max(lr[k] for k in lr if k != "2018/19")
A24, AREC, AALL = AG["fitted_rate_2024"], AG["mean_rate_2015_2024"], AG["mean_rate_1980_2024"]; BOOT = V["us_ladder"]["boot_p995_hi"]; MC = V["us_ladder"]["mc_p995_hi"]
n_fs_floor = sum(1 for n in names if SEL[n]["forward_stop"]["start0.10_alpha0.05"]["q"] <= 0.1001)
def fs(n, s, a): return SEL[n]["forward_stop"][f"start{s:.2f}_alpha{a:.2f}"]

TITLE = "Heavy Tails in Catastrophe and Large-Fire Losses: Threshold Choice, Capital Measures and Lessons for Egypt and Saudi Arabia"
P(TITLE, bold=True, align="c", size=15, after=14)
if AR:
    _t = P("الذيول الثقيلة في خسائر الكوارث والحرائق الكبرى: اختيار العتبة ومقاييس رأس المال ودروس لمصر والمملكة العربية السعودية", bold=True, align="c", size=14, after=12); RTL(_t)
    for _r in _t.runs: _r.font.size = Pt(15); _r.bold = True
if not BLIND:
    P("Moustafa Elbehairy ¹ ∗", align="c", size=12, after=2)
    P("¹ Department of Statistics and Insurance, Faculty of Commerce, Suez Canal University, Ismailia, Egypt", align="c", size=11, after=2)
    P("∗ Corresponding author: moustafayosri@commerce.suez.edu.eg  |  ORCID 0009-0009-1062-9420", align="c", size=11, after=10)
else:
    P("[Author details removed for double-blind review]", align="c", size=11, italic=True, after=10)
if not AR:
    P(f"Manuscript type: Quantitative research article   |   Main text ≈ {WCJ['main_text']:,} words (Sections 1–5, excluding abstract, tables, captions and references)   |   Tables: 9   |   Figures: 5   |   JEL: G22, G28, C46, Q54", align="c", size=10, after=14)

# ------------------------------------------------------------------ ABSTRACT
ABS = (f"Property insurers hold capital against the losses conventional models describe worst, and two emerging-market supervisors now decide how to measure them. "
       f"This paper measures how heavy catastrophe and large-fire tails are on observed data, how much the answer depends on the threshold, and what conventional models miss. "
       f"The peaks-over-threshold model is fitted to five registers, {US['n']} U.S. billion-dollar disasters, {DK['n']:,} Danish and {NO['n']:,} Norwegian fire losses and {NZ['n']} New Zealand and {AU['n']} Australian catastrophes, with thresholds chosen by three automated rules, intervals on every estimate, a U.S. annual aggregate and a reading of Egypt's fire line. "
       f"All five tails are Pareto-type with shape parameters of {f2(min(xi_head.values()))} to {f2(max(xi_head.values()))}, so no register has a finite variance and the three catastrophe registers cannot exclude an infinite tail mean. "
       f"A lognormal fitted to all data recovers {100*min(under.values()):.0f} to {100*max(under.values()):.0f} percent of the generalized Pareto 99.5 percent quantile; fitted above the same threshold it recovers {100*min(under_tr[n] for n in EXNZ):.0f} to {100*max(under_tr[n] for n in EXNZ):.0f} percent, so most of the familiar understatement comes from fitting the body; tail value-at-risk exceeds value-at-risk by a factor of {min(ratio.values()):.1f} to {max(ratio.values()):.1f}. "
       f"The U.S. shape falls from {f2(US['xi'])} at the median threshold to {f2(US['hi']['xi'])} at the 90th percentile, and the 1-in-200-year annual aggregate moves with it, from USD {bn(L50['agg_p995_2024'])} billion to USD {bn(A24['p995'])} billion at the 2024 event frequency. "
       f"Egypt's Financial Regulatory Authority should mandate an event-level large-loss register for the fire line, and Saudi Arabia's Insurance Authority should require the shape interval and a tail value-at-risk beside the 99.5 percent quantile.")
if not AR:
    H("Abstract", 1); P(ABS, body=True, after=6)
    P("**Keywords:** extreme value theory; generalized Pareto distribution; threshold selection; catastrophe losses; fire insurance; tail value-at-risk; risk-based capital", after=10)
if AR:
    p = P("الملخص", bold=True, align="r", after=2); RTL(p)
    ar = (f"تحتفظ شركات تأمين الممتلكات برأس مال لمواجهة خسائر تصفها النماذج التقليدية أسوأ وصف، وتقف جهتان رقابيتان في الأسواق الناشئة اليوم أمام قرار قياسها: فهيئة التأمين السعودية تطبّق إطار رأس المال القائم على المخاطر اعتبارًا من 2027، والهيئة العامة للرقابة المالية في مصر ما زالت تحدد الملاءة كنسبة من الأقساط. "
          f"يقيس هذا البحث مدى ثقل ذيول خسائر الكوارث والحرائق الكبرى على بيانات مرصودة، ومدى اعتماد النتيجة على العتبة، وما الذي تغفله النماذج التقليدية. "
          f"طُبّق نموذج تجاوز العتبة على خمسة سجلات خسائر: {US['n']} كارثة أمريكية تجاوزت خسائرها مليار دولار، و{DK['n']:,} خسارة حريق دنماركية و{NO['n']:,} خسارة حريق نرويجية، و{NZ['n']} حدثًا نيوزيلنديًا و{AU['n']} حدثًا أستراليًا، مع اختيار العتبة بثلاث قواعد آلية، وفترات ثقة بالإمكان الجانبي والبوتستراب لكل تقدير، ونموذج بواسون مركّب للخسارة السنوية الإجمالية في الولايات المتحدة، وقراءة لفرع الحريق المصري من إحصاءات الهيئة. "
          f"الذيول الخمسة جميعها من نوع باريتو بمعلمة شكل بين {f2(min(xi_head.values()))} و{f2(max(xi_head.values()))}، فلا يوجد سجل بتباين منتهٍ، ولا تستطيع سجلات الكوارث الثلاثة استبعاد متوسط ذيل لا نهائي. "
          f"ولا يستعيد التوزيع اللوغاريتمي الطبيعي المطبّق على كامل البيانات سوى {100*min(under.values()):.0f}% إلى {100*max(under.values()):.0f}% من كمّية 99.5% لتوزيع باريتو المعمّم، ويستعيد {100*min(under_tr[n] for n in EXNZ):.0f}% إلى {100*max(under_tr[n] for n in EXNZ):.0f}% منها عند تطبيقه فوق العتبة نفسها، فمعظم التقليل المألوف ينشأ من مطابقة جسم التوزيع، ويعود النموذجان إلى الافتراق أبعد في الذيل وفي متوسطه؛ وتفوق القيمة المعرّضة للخطر الذيلية القيمةَ المعرّضة للخطر بمعامل {min(ratio.values()):.1f} إلى {max(ratio.values()):.1f}. "
          f"وتنخفض معلمة الشكل الأمريكية من {f2(US['xi'])} عند عتبة الوسيط إلى {f2(US['hi']['xi'])} عند المئين التسعين، فتتحرك الخسارة السنوية الإجمالية لفترة عودة 200 سنة تبعًا لذلك من {bn(L50['agg_p995_2024'])} إلى {bn(A24['p995'])} مليار دولار عند معدل تكرار 2024. "
          f"ويوصي البحث الهيئةَ العامة للرقابة المالية بإلزام الشركات بسجل للخسائر الكبرى على مستوى الحدث في فرع الحريق وبتحديد احتفاظات إعادة التأمين وفق مستويات العودة المقدّرة، ويوصي هيئة التأمين السعودية باشتراط الإفصاح عن فترة ثقة معلمة الشكل وعن القيمة الذيلية إلى جانب كمّية 99.5%.")
    p = P(ar, align="r", after=4); RTL(p)
    p = P("الكلمات المفتاحية: نظرية القيم المتطرفة؛ توزيع باريتو المعمّم؛ اختيار العتبة؛ الخسائر الكارثية؛ تأمين الحريق؛ القيمة المعرّضة للخطر الذيلية؛ رأس المال القائم على المخاطر", align="r", after=12); RTL(p)
    doc.save(f"{VER}/EVT_Catastrophe_Losses_Manuscript_v4_الملخص_العربي.docx"); print("saved arabic abstract"); sys.exit(0)

# ------------------------------------------------------------------ 1 INTRODUCTION
H("1.  Introduction", 1)
P("Insured losses from natural catastrophes reached about USD 107 billion in 2025, and the January wildfires in Los Angeles alone cost insurers close to "
  "USD 40 billion (Swiss Re Institute, 2026). The United States recorded 23 billion-dollar disasters in 2025 at "
  "a direct cost near USD 115 billion (Climate Central, 2026), on top of the 403 events of 1980–2024 analysed here. The hazard is not confined to the markets "
  "that record it best: when a Mediterranean storm crossed Egypt in March 2020 the government called it the country's worst in four decades (Al-Monitor, "
  "2020), almost none of the loss was insured, and the protection gap for flood and windstorm is widest in emerging markets (Holzheu & Turner, 2018).", indent=True)
P("For an actuary the difficulty with such losses is statistical before it is financial. A few events carry most of the total, and a normal or lognormal model fitted to all claims "
  "describes the body of the distribution while misrepresenting the part that decides capital. Extreme value "
  "theory addresses the tail directly: the Pickands–Balkema–de Haan theorem shows that excesses over a high threshold converge to the generalized "
  "Pareto distribution, whose shape parameter measures how heavy the tail is (Balkema & de Haan, 1974; Pickands, 1975). Two practical difficulties remain. "
  "The threshold must be chosen, by eye from a mean-excess plot for most of the method's history (Scarrott & MacDonald, 2012) or by the automated "
  "rules now available (Bader et al., 2018; Murphy et al., 2025). And on a few hundred events the shape carries wide uncertainty, which matters because a "
  "value at or above one makes the tail mean, and with it tail value-at-risk, infinite.", indent=True)
P("Both difficulties have a regulatory edge. Solvency II calibrates capital to a one-year 99.5 percent value-at-risk and gives natural catastrophe its own "
  "sub-module with prescribed regional scenarios (European Commission, 2015). Saudi Arabia's Insurance Authority announced in April 2026 that a risk-based "
  "capital framework broadly aligned with Solvency II becomes mandatory on 1 January 2027, with an internal-model option (Insurance Authority, 2026). Egypt's Financial Regulatory Authority issued Decision No. 148 of 2025 on solvency "
  "standards under the Unified Insurance Law, and its margin remains premium-based without a catastrophe module (FRA, 2025b). How heavy the tail is, and how "
  "confidently it can be measured, therefore bears on two capital regimes being written now.", indent=True)
P(f"The objective of this paper is to answer those questions on observed rather than simulated losses. It fits the peaks-over-threshold model to five "
  f"registers covering natural catastrophes on three continents and the two large-fire datasets on which the literature was calibrated, selects thresholds "
  f"by three automated rules, reports profile-likelihood and bootstrap uncertainty for every tail quantity, sets the generalized Pareto tail against "
  f"conventional alternatives fitted both to all data and above the same threshold, and, for the dated U.S. record, combines a frequency trend with the "
  f"fitted severity into an annual aggregate, before reading Egypt's fire line against the same lens. The contribution is threefold. (1) Methodologically, it shows on five registers what automated threshold "
  f"selection does and does not settle: goodness-of-fit rules accept the lowest candidate on truncated registers, and the shape, not the fit, has to decide. (2) Empirically, it provides comparable tail estimates with full uncertainty for "
  f"the five registers and a 1-in-200-year U.S. annual aggregate whose dependence on the threshold is stated rather than assumed. (3) Practically, it "
  f"specifies what a catastrophe module for Egypt's forthcoming regime needs first and what Saudi Arabia's 2027 module should report.", indent=True)
P("Three questions organise the analysis. **RQ1:** How heavy are the tails of observed catastrophe and large-fire losses, and how much does the answer "
  "depend on how the threshold is chosen? **RQ2:** By how much do conventional models understate the 99.5 percent loss, and how far does tail value-at-risk "
  "exceed value-at-risk? **RQ3:** What follows for catastrophe capital and reinsurance in Egypt and Saudi Arabia? Section 2 reviews the literature, Section 3 "
  "describes the data, estimators and tests, Section 4 reports the results, their robustness and the discussion, and Section 5 concludes with recommendations "
  "to named bodies, limitations and further work.", indent=True)

# ------------------------------------------------------------------ 2 LITERATURE REVIEW
H("2.  Literature Review", 1)
H("2.1  Peaks over Threshold in Insurance Loss Modelling", 2)
P("Extreme value theory offers two routes to the tail. The block-maxima route fits the generalized extreme value distribution to the largest loss in each "
  "block; the peaks-over-threshold route uses every loss above a threshold u and extracts more from the same data (Coles, 2001; Embrechts et al., 1997). "
  "McNeil (1997) made the second route standard in insurance with the Danish fire data, Embrechts, Resnick and Samorodnitsky (1999) presented it as a "
  "risk-management tool, and applications followed to windstorm, large claims, operational losses, financial returns and, more recently, cyber events "
  "(Rootzén & Tajvidi, 1997; Cebrián et al., 2003; Gilli & Këllezi, 2006; Chavez-Demoulin et al., 2016; Eling & Wirfs, 2019). In each case the quantity of "
  "interest is the shape parameter of the generalized Pareto distribution, because it alone decides which moments exist and hence which risk measures are "
  "defined. Tail value-at-risk is coherent in the sense of Artzner et al. (1999) where value-at-risk is not, and the ratio between them, which tends to "
  "1/(1 − ξ) far in the tail, measures how much of the risk a quantile leaves out (Rockafellar & Uryasev, 2002). The regulatory relevance is direct. "
  "Solvency II's natural-catastrophe sub-module prescribes regional scenarios calibrated by the supervisor rather than a tail fitted by the insurer, which "
  "is defensible where loss registers are long and exposure data rich, and unavailable where neither exists; in such markets the layer-pricing use of the "
  "fitted tail in McNeil (1997) and Chao (2022) is the only quantitative basis a reinsurance buyer has.", indent=True)
H("2.2  Threshold Selection and Estimation Uncertainty", 2)
P("The threshold trades bias against variance: too low and the Pareto approximation fails, too high and few exceedances remain. The classical diagnostics, "
  "the mean-excess plot, which is linear above a valid threshold, and the plot of the estimated shape against u, which should be flat, are informative but "
  "subjective (Davison & Smith, 1990; Scarrott & MacDonald, 2012), and the asymptotically optimal sample fractions of Drees and Kaufmann (1998) and "
  "Danielsson et al. (2001) require second-order assumptions that small insurance registers cannot check. Three automated rules are now in use. Northrop and "
  "Coleman (2014) test the constancy of the shape above candidate thresholds. Bader, Yan and Zhang (2018) test the generalized Pareto fit with the "
  "Anderson–Darling statistic at an ascending sequence of thresholds and apply the ForwardStop rule, which controls the false-discovery rate of ordered "
  "tests, to select the lowest threshold above which the fit is adequate. Murphy, Tawn and Varty (2025) instead choose the threshold that minimises the "
  "expected discrepancy between bootstrap-fitted model quantiles and the sample quantiles of the excesses, and Schneider, Krajina and Krivobokova (2021) "
  "compare such rules in simulation. Uncertainty is the second issue. On a few hundred events the profile likelihood for the shape is wide and asymmetric, "
  "and long-period return levels inherit that width in amplified form (Smith, 1987; Coles, 2001). Reporting a shape without its interval conceals the one "
  "fact about a catastrophe tail that a capital rule most needs, whether ξ ≥ 1 can be ruled out.", indent=True)
H("2.3  Prior Evidence on Catastrophe and Large-Fire Tails", 2)
P("McNeil (1997) found shapes between 0.5 and 0.7 for the Danish fires depending on the threshold, and Wong, Li and Yu (2021) confirm with a new test that "
  "their variance does not exist. Rootzén and Tajvidi (1997) reported a similarly heavy tail for Swedish windstorm claims, and Kellner and Gatzert (2013) "
  "used multivariate extremes to price the basis risk of index-linked catastrophe cover. For U.S. disasters, Smith and Katz (2013) documented the sources, "
  "biases and trends of the billion-dollar record and attributed the rising annual aggregate mainly to a rise in event frequency of about 5 percent a year; "
  "Katz (2002) proposed the compound-Poisson model of hurricane damage that Section 3.2 adopts. Whether that trend reflects hazard or exposure is contested: "
  "Pielke et al. (2008) found no trend in hurricane damage once losses were normalised to current exposure, while Barthel and Neumayer (2012) found "
  "significant upward trends in normalised insured losses for the United States and West Germany but not globally. For reinsurance the generalized Pareto "
  "tail is the natural basis for excess-of-loss layer pricing (McNeil, 1997; Chao, 2022), and for capital it underlies the tail-measure regimes that "
  "Solvency II's quantile calibration leaves aside. Evidence from the Middle East and North Africa is thin: the protection-gap analysis of Holzheu and "
  "Turner (2018) places the region among the most under-insured for flood and earthquake, and the G20 Sustainable Finance Working Group (2025) names data "
  "scarcity as the first obstacle to closing that gap.", indent=True)
P("Read together, these strands leave two things undone, and the taxonomy of Müller-Bloch and Kranz (2015) and Robinson, Saldanha and McKoy (2011) names "
  "them. The first is a methodological gap. Automated selectors have been available for a decade, but they are rarely applied side by side to several "
  "registers, so it is not known whether they agree, whether they add anything on registers that are already truncated tails, or how far the capital "
  "figures that follow depend on the choice they make; most applied work still picks one threshold on one dataset and reports a point estimate of the "
  "shape without its interval. The second is a population gap. No published tail analysis exists for Egypt's property-fire line, Gulf and MENA "
  "property-catastrophe tails are absent from the literature, and no study has read extreme-value estimates from observed registers against the capital "
  "regimes that Egypt and Saudi Arabia are now writing. This paper addresses both: it applies three selectors and one estimation procedure, with full "
  "uncertainty, to five observed registers, and brings the result to the two markets where the question has not yet been asked.", indent=True)

# ------------------------------------------------------------------ 3 METHODOLOGY
H("3.  Methodology", 1)
H("3.1  Research Design and Data", 2)
P("The design is a comparative tail analysis. One estimation procedure is applied, without dataset-specific tuning, to five observed loss registers, and "
  "the results are then read against a sixth, market-level series for Egypt. The five were chosen on three grounds. Each is a register of recorded losses "
  "rather than a simulated or calibrated loss set. Together they span three continents, two perils and sample sizes from 144 to 9,181 events, so the "
  "behaviour of the procedure on small and large registers can be compared. And the two fire datasets are the benchmarks on which the extreme-value "
  "literature has calibrated itself since McNeil (1997), which ties the new estimates to the prior evidence of Section 2.3.", indent=True)
P(f"Table 1 describes the data. The U.S. register is the National Centers for Environmental Information record of weather and climate disasters whose "
  f"direct cost reached USD 1 billion, CPI-adjusted to 2024 dollars: {US['n']} events from 1980 to 2024 across severe storms, tropical cyclones, floods, "
  f"droughts, winter storms, wildfires and freezes (NOAA NCEI, 2025); Climate Central has maintained the series since 2025 (Climate Central, 2026). The "
  f"Danish data are the {DK['n']:,} fire losses above DKK 1 million recorded by Copenhagen Re between 1980 and 1990 and used by McNeil (1997); the Norwegian "
  f"data are {NO['n']:,} fire losses above NOK 500,000 from 1972 to 1992 at 2012 prices. The New Zealand and Australian registers are the catastrophe lists "
  f"of the two national insurance councils, {NZ['n']} and {AU['n']} events from 1967–1968 to 2014 normalised to 2014 exposure. All four are distributed in "
  f"the CASdatasets collection (Dutang & Charpentier, 2020). Costs are kept in the units recorded, so results are compared within and not across registers; "
  f"the question is the shape of each tail, which is scale-free, not the size of one market against another. Two features of the registers matter for what "
  f"follows. Each begins at a reporting threshold, one billion dollars for the U.S. record, DKK 1 million and NOK 500,000 for the fire data and a "
  f"materiality criterion for the two councils' lists, so every register is already a truncated tail and the lowest candidate threshold is not the "
  f"smallest claim but a point well inside the Pareto region. And the registers differ by two orders of magnitude in size, which is the range over which "
  f"the behaviour of an automated selector and the width of the profile intervals are expected to change most. "
  f"The Egyptian fire line is read from Tables 1/6 and 2/6 of the Financial Regulatory Authority's Insurance Statistical Books for 2022/2023 and 2023/2024 "
  f"(FRA, 2024, 2025a), with the 2014/2015 baseline as stated by the Insurance Federation of Egypt in September 2026 and the 2025 ratios as stated by the "
  f"Authority's Deputy Chairman (Al-Mal, 2026a, 2026b).", indent=True)
TABLE("Table 1. Observed loss registers and descriptive statistics",
      ["Register (unit)", "Source", "n", "Mean", "Median", "Max", "Top-10 share of total", "Skewness"],
      [[f"{short[n]} ({unit[n]})", {nUS: "NOAA NCEI / Climate Central", nDK: "Copenhagen Re via McNeil (1997)", nNO: "Norwegian insurers via CASdatasets", nNZ: "ICNZ via CASdatasets", nAU: "ICA via CASdatasets"}[n],
        f"{D[n]['n']:,}", f1(D[n]["mean"]), f1(D[n]["median"]), f0(D[n]["max"]), f"{100*D[n]['top10_share']:.0f}%", f1(D[n]["skew"])] for n in names],
      note="Note. U.S. costs are CPI-adjusted to 2024 dollars; Norwegian losses to 2012 prices; New Zealand and Australian costs normalised to 2014 exposure. Top-10 share = sum of the ten largest losses ÷ sum of all losses.",
      widths=[3.6, 3.4, 1.2, 1.4, 1.4, 1.6, 2.0, 1.4], size=8.5)

H("3.2  Peaks-over-Threshold Model and Estimation", 2)
P("The estimation follows the peaks-over-threshold approach of Embrechts, Klüppelberg and Mikosch (1997) as applied to insurance losses by McNeil (1997). "
  "For a loss X with distribution F, the excess Y = X − u given X > u converges, as u rises, to the generalized Pareto distribution", indent=True)
EQ("G_{ξ,β}(y) = 1 − (1 + ξ y / β)^{−1/ξ},   ξ ≠ 0;    G_{0,β}(y) = 1 − exp(−y/β)", 1)
P("with scale β > 0 and shape ξ. A negative shape gives a bounded tail, zero an exponential one, and a positive shape a Pareto-type tail in which moments "
  "of order 1/ξ and above do not exist: the variance is infinite for ξ ≥ 0.5 and the mean for ξ ≥ 1. Combining the fitted distribution with the empirical "
  "exceedance probability N_u/n gives the tail estimator", indent=True)
EQ("P̂(X > x) = (N_u / n) · (1 + ξ̂ (x − u) / β̂)^{−1/ξ̂},   x > u", 2)
P("from which value-at-risk at level p, tail value-at-risk (the mean loss beyond that quantile, also called expected shortfall) and the return level for a "
  "return period of T events follow as", indent=True)
EQ("VaR_p = u + (β̂/ξ̂) [ ((n/N_u)(1 − p))^{−ξ̂} − 1 ],    TVaR_p = VaR_p/(1 − ξ̂) + (β̂ − ξ̂ u)/(1 − ξ̂)  (ξ̂ < 1),    x_T = VaR_{1 − 1/T}", 3)
P("(McNeil et al., 2015). Parameters are estimated by maximum likelihood on the exceedances and the shape's 95 percent interval by profile likelihood "
  "(Smith, 1987; Coles, 2001).", indent=True)
P("Three selection rules are applied to the same candidate grid, the 10th to the 95th percentile of each register in steps of 2.5 percentage points with "
  "at least 40 exceedances. The first is the ordered goodness-of-fit rule of Bader, Yan and Zhang (2018): at each candidate the generalized Pareto "
  "distribution is fitted, its Anderson–Darling statistic is compared with a parametric-bootstrap distribution to give a p-value, and the ForwardStop rule "
  "at level α rejects the lowest thresholds whose cumulative evidence of misfit is significant and selects the first that survives. Because the rule "
  "can only reject candidates below the first adequate one, its answer depends on where the grid starts, so the paper reports it from three starting "
  "quantiles and at three levels of α. The second is the expected-quantile-discrepancy rule of Murphy, Tawn and Varty (2025): for each candidate the "
  "excesses are resampled, the model is refitted, and the mean absolute distance between the refitted quantiles and the sample quantiles of the excesses is "
  "averaged over resamples; the threshold with the smallest discrepancy is chosen. The third is a stability rule in the spirit of Northrop and Coleman "
  "(2014): the lowest candidate whose profile-likelihood interval contains every shape estimate obtained at higher thresholds. The main tables report the "
  "ForwardStop fit from the median upward, which is the configuration of the original proposal, together with a high-threshold fit at the 90th percentile "
  "(or the highest grid quantile that leaves 25 exceedances), and Section 4.2 compares all three rules.", indent=True)
P("Value-at-risk, tail value-at-risk and return levels are computed from equation (3) at 99, 99.5 and 99.9 percent and for return periods of 10 to 1,000 "
  "events, with 95 percent intervals from 500 non-parametric bootstrap replications of the fit at the selected threshold quantile; the selection step is "
  "held fixed inside the bootstrap because re-running three selectors in every replicate would mix two sources of uncertainty that the paper prefers to "
  "show separately. The generalized Pareto quantiles are compared with four conventional alternatives: normal and lognormal distributions fitted by "
  "maximum likelihood to all observations, which is how such models are commonly used, and two fairer competitors fitted to the same exceedances, a "
  "lognormal left-truncated at the threshold and a lognormal fitted to the excesses themselves. The truncated fit conditions the likelihood on exceedance, "
  "so the lognormal is asked to describe only the region in which the generalized Pareto distribution is also fitted, and both are combined with the same "
  "empirical exceedance probability when quantiles are formed; any remaining difference is then one of tail form rather than of the data each model was "
  "shown.", indent=True)
P("For the U.S. record, which carries dates, the annual number of events is modelled as a Poisson process with a log-linear trend,", indent=True)
EQ("N_t ~ Poisson(λ_t),   log λ_t = a + b (t − 1980)", 4)
P("and the annual aggregate S = Σ X_i is simulated 40,000 times as a compound Poisson sum, following Katz (2002), with severity drawn from the empirical "
  "distribution below the threshold and from the fitted generalized Pareto distribution above it. Three frequencies are used: the 1980–2024 mean, the "
  "2015–2024 mean and the fitted 2024 rate. The 99.5 percent quantile of S is the one-year 1-in-200 aggregate that a Solvency II-style regime targets. "
  "Expected losses to excess-of-loss layers, E[min(max(X − a, 0), l)], are computed under the fitted tail and empirically for three illustrative layers, in "
  "the manner of McNeil (1997).", indent=True)
H("3.3  Tests in Order, Planned Robustness Checks and Reproducibility", 2)
P("Diagnostics are applied in a fixed order at each selected threshold. The bootstrap Anderson–Darling p-value that the selection rule itself produces "
  "tests the adequacy of the fit; a Kolmogorov–Smirnov statistic is added with a parametric-bootstrap p-value, because the asymptotic p-value is not "
  "exact when the parameters are estimated; quantile–quantile plots of the excesses provide the visual check; and the maximum-likelihood shape is compared "
  "with the Hill estimator at the same number of exceedances, a semi-parametric check that does not assume the Pareto form (Beirlant et al., 2004). For "
  "the frequency model the trend coefficient b in equation (4) is tested by its Poisson-regression p-value.", indent=True)
P("Five robustness checks are announced here and reported in Section 4.2. First, the three selection rules are compared on every register, and the "
  "ForwardStop rule is rerun from three starting quantiles and at three levels of α. Second, every register is refitted at the high threshold and the "
  "shape, its interval and the return levels are compared with the automated fit. Third, for the U.S. record the shape, the ratio of tail value-at-risk "
  "to value-at-risk and the 1-in-200 annual aggregate are traced across seven thresholds from the median to the 90th percentile, the headline aggregate "
  "carries a bootstrap interval from 200 resamples of the register, and its Monte-Carlo error is measured across five seeds. Fourth, the conventional "
  "comparators are refitted above the threshold so that the understatement of the tail is not an artefact of fitting the body. Fifth, the shape is traced "
  "across the whole grid against the profile band of the selected fit, so that a threshold accepted on goodness of fit can still be rejected on stability. "
  "All computations use Python 3.11 with SciPy and statsmodels and a single random seed (2026) for the parametric bootstrap, the non-parametric "
  "bootstrap and the compound-Poisson simulation. " +
  ("The scripts, the merged data, the results files and the manuscript builder are available in a public repository (link withheld for review)." if BLIND else
   f"The scripts, the merged data, the results files and the manuscript builder are openly available at {REPO} (release v1.0.0)."), indent=True)
if not BLIND:
    _p = P("", align="j", after=6); _r = _p.add_run("Zenodo DOI: to be inserted after release"); _r.font.name = FONT; _r.font.size = Pt(12); _r.font.highlight_color = WD_COLOR_INDEX.YELLOW

# ------------------------------------------------------------------ 4 EMPIRICAL ANALYSIS
H("4.  Empirical Analysis", 1)
H("4.1  Results", 2)
H("4.1.1  The Shape of the Loss Distributions", 3)
P(f"Table 1 and Figure 1 show one profile in five registers. The mean exceeds the median by a factor of {min(D[n]['mean']/D[n]['median'] for n in names):.1f} to "
  f"{max(D[n]['mean']/D[n]['median'] for n in names):.1f}, skewness runs from {min(D[n]['skew'] for n in names):.0f} to {max(D[n]['skew'] for n in names):.0f}, and the ten "
  f"largest losses account for {100*min(D[n]['top10_share'] for n in names):.0f} to {100*max(D[n]['top10_share'] for n in names):.0f} percent of the total. In the U.S. "
  f"record the ten largest of {US['n']} events, led by Hurricanes Katrina, Harvey, Ian and Maria, carry {100*US['top10_share']:.0f} percent of the loss; in New "
  f"Zealand the 2011 Christchurch earthquake is by itself {100*NZ['top10_share']-6:.0f} percent of the register. On the log–log survival plot every register decays "
  f"along a straight line, the signature of a power tail, and the fitted generalized Pareto tails follow the empirical points to the largest observation.", indent=True)
FIG(f"{FIGS}/fig1_tails.png", "Figure 1. Empirical survival functions of the five loss registers on log–log axes, losses scaled by each register's median, with the fitted generalized Pareto tails (solid lines) above the ForwardStop thresholds. Sources: NOAA NCEI / Climate Central; CASdatasets.", width_cm=14)
H("4.1.2  Thresholds and Generalized Pareto Estimates", 3)
P(f"Table 2 reports the fits at the ForwardStop threshold from the median upward and at the high threshold. The ForwardStop rule selects the median in every "
  f"register: the bootstrap Anderson–Darling p-values at the median run from {min(D[n]['ad_p'] for n in names):.2f} to {max(D[n]['ad_p'] for n in names):.2f}, so the "
  f"generalized Pareto distribution is not rejected from the median upward. For records that are themselves truncated tails, the U.S. record beginning at one "
  f"billion dollars and the fire data at fixed reporting thresholds, that is what adequacy of fit should look like. Adequacy is not stability, however, and "
  f"Section 4.2 shows that the U.S. shape moves with the threshold more than the goodness-of-fit test can detect. For that reason the U.S. record is "
  f"reported at both thresholds throughout, the high-threshold fit is used wherever a single U.S. figure is quoted, and the median fit is treated as an "
  f"upper bound.", indent=True)
P(f"The shapes are heavy everywhere. At the median they are {f2(DK['xi'])} for the Danish fires, at the upper end of McNeil's (1997) range, {f2(NO['xi'])} for the "
  f"Norwegian fires, {f2(AU['xi'])} for Australia, {f2(US['xi'])} for the United States and {f2(NZ['xi'])} for New Zealand; at the 90th percentile the U.S. shape "
  f"is {f2(US['hi']['xi'])}. The intervals matter more than the points. For the two fire registers, with thousands of exceedances, the profile intervals are "
  f"narrow ({f2(DK['xi_ci'][0])}–{f2(DK['xi_ci'][1])} and {f2(NO['xi_ci'][0])}–{f2(NO['xi_ci'][1])}), exclude one and include 0.5: the variance is infinite and "
  f"the mean finite. For the three catastrophe registers, with {NZ['n']} to {US['n']} events, the upper limits reach {f2(US['xi_ci'][1])}, {f2(NZ['xi_ci'][1])} and "
  f"{f2(AU['xi_ci'][1])} at the median and {f2(US['hi']['xi_ci'][1])} for the United States even at the high threshold, so the data cannot rule out ξ ≥ 1, the "
  f"point at which the expected excess and tail value-at-risk cease to exist. The bootstrap Kolmogorov–Smirnov p-values lie between "
  f"{min(D[n]['ks_p_boot'] for n in names):.2f} and {max(D[n]['ks_p_boot'] for n in names):.2f}, and the quantile–quantile plots of Figure 2 show the excesses "
  f"on the fitted line up to the largest observation in each register.", indent=True)
TABLE("Table 2. Generalized Pareto estimates at the ForwardStop threshold (median) and at the high threshold, with goodness of fit",
      ["Register", "ForwardStop u (quantile), N_u", "ξ̂ (95% profile CI)", "AD p / bootstrap KS p", "High u (quantile), N_u", "ξ̂ high (95% CI)", "AD p high", "Hill ξ̂ at N_u"],
      [[short[n], f"{f1(D[n]['u'])} (q{D[n]['q_u']:.2f}), {D[n]['nu']:,}", f"{f2(D[n]['xi'])} ({f2(D[n]['xi_ci'][0])}, {f2(D[n]['xi_ci'][1])})", f"{f2(D[n]['ad_p'])} / {f2(D[n]['ks_p_boot'])}",
        f"{f1(D[n]['hi']['u'])} (q{D[n]['hi']['q_u']:.2f}), {D[n]['hi']['nu']:,}", f"{f2(D[n]['hi']['xi'])} ({f2(D[n]['hi']['xi_ci'][0])}, {f2(D[n]['hi']['xi_ci'][1])})", f2(D[n]["hi"]["ad_p"]), f2(D[n]["hill"][str(D[n]["nu"])])] for n in names],
      note="Note. ForwardStop rule of Bader, Yan and Zhang (2018) over the 50th to 95th percentiles with at least 40 exceedances (α = 0.05); high threshold = highest grid quantile up to the 90th percentile with at least 25 exceedances. "
           "Profile-likelihood intervals at 95 percent; Anderson–Darling (AD) and Kolmogorov–Smirnov (KS) p-values from parametric bootstrap.", widths=[2.6, 2.6, 2.5, 1.8, 2.6, 2.3, 1.2, 1.4], size=8)
FIG(f"{FIGS}/fig2_qq.png", "Figure 2. Quantile–quantile plots of threshold excesses against the fitted generalized Pareto distribution at the ForwardStop threshold (log axes).")
H("4.1.3  Tail Risk Measures and Return Levels", 3)
P(f"Table 3 reports value-at-risk and tail value-at-risk at the three levels with bootstrap intervals, and Table 4 the return levels. Tail value-at-risk "
  f"exceeds value-at-risk by a margin that widens with the shape: at 99.5 percent the ratio is {ratio[nDK]:.1f} for the Danish fires, {ratio[nNO]:.1f} for the "
  f"Norwegian fires, {ratio[nAU]:.1f} for Australia and {ratio[nUS]:.1f} for the United States at the high threshold, close to the limiting value 1/(1 − ξ̂) in "
  f"each case; at the median U.S. threshold it would be {ratio_med_US:.1f}, and for New Zealand, where ξ̂ exceeds one, tail value-at-risk is undefined. A capital "
  f"rule that stops at the 99.5 percent quantile therefore leaves out an expected loss beyond it that is between roughly twice and seven times the "
  f"quantile. The bootstrap intervals are wide, asymmetric and widen with the level: the U.S. 99.5 percent value-at-risk of USD {bn(US['risk']['0.995']['VaR'])} "
  f"billion at the median threshold has an interval of USD {bn(US['risk']['0.995']['VaR_ci'][0])} to {bn(US['risk']['0.995']['VaR_ci'][1])} billion. The generalized "
  f"Pareto 99.5 percent quantile sits above the empirical quantile in four registers, as it should when fewer than 200 events are available per unit of "
  f"exceedance, and below it in New Zealand, where the Christchurch observation lies far beyond what the other {NZ['n']-1} events predict. The return levels of "
  f"Table 4 translate the same tails into the language of reinsurance programmes. For the Danish fires the loss exceeded once in 200 events is DKK "
  f"{f0(DK['return_levels']['200'])} million at the median threshold and DKK {f0(DK['hi']['return_levels']['200'])} million at the high threshold, a difference "
  f"well inside the bootstrap interval; for the U.S. record the two fits give USD {bn(US['return_levels']['200'])} and {bn(US['hi']['return_levels']['200'])} "
  f"billion, and the gap widens with the return period until at 1,000 events the median fit implies a loss of USD {bn(US['return_levels']['1000'])} billion "
  f"that no physical reading of the record supports. The pattern is general: where the shape is stable the return levels are too, and where it is not the "
  f"threshold choice carries through to every long-period figure.", indent=True)
def rrow(n):
    r = D[n]["risk"]; return [short[n]] + sum([[f"{f0(r[p]['VaR'])}\n({f0(r[p]['VaR_ci'][0])}–{f0(r[p]['VaR_ci'][1])})", (f"{f0(r[p]['TVaR'])}\n({f0(r[p]['TVaR_ci'][0])}–{f0(r[p]['TVaR_ci'][1])})" if r[p]["TVaR_ci"] else "∞"), f0(r[p]["empirical"])] for p in ("0.99", "0.995", "0.999")], [])
TABLE("Table 3. Generalized Pareto value-at-risk and tail value-at-risk per event at the ForwardStop threshold, with 95 percent bootstrap intervals (loss units of Table 1)",
      ["Register", "VaR 99%", "TVaR 99%", "Emp. 99%", "VaR 99.5%", "TVaR 99.5%", "Emp. 99.5%", "VaR 99.9%", "TVaR 99.9%", "Emp. 99.9%"],
      [rrow(n) for n in names],
      note=f"Note. Intervals (in parentheses, second line) from 500 non-parametric bootstrap replications of the fit at the selected quantile. TVaR is undefined (∞) where ξ̂ ≥ 1. The U.S. high-threshold figures are VaR {bn(US['hi']['risk']['0.995']['VaR'])} and TVaR {bn(US['hi']['risk']['0.995']['TVaR'])} USD billion at 99.5 percent (Table 9).",
      widths=[2.4, 1.6, 1.7, 1.4, 1.6, 1.7, 1.4, 1.6, 1.7, 1.4], size=7.5)
TABLE("Table 4. Return levels by return period in events, ForwardStop threshold (upper row) and high threshold (lower row), loss units of Table 1",
      ["Register", "T = 10", "20", "50", "100", "200", "500", "1,000"],
      sum([[[short[n]] + [f0(D[n]["return_levels"][str(T)]) for T in (10, 20, 50, 100, 200, 500, 1000)], ["   high threshold"] + [f0(D[n]["hi"]["return_levels"][str(T)]) for T in (10, 20, 50, 100, 200, 500, 1000)]] for n in names], []),
      note=f"Note. Return level x_T is the loss exceeded on average once every T events; for the U.S. record at the 2024 frequency of about {F['rate_2024_fit']:.0f} events a year, 200 events correspond to roughly nine years. The high-threshold rows are discussed in Section 4.2.",
      widths=[3.4, 1.9, 1.9, 1.9, 1.9, 1.9, 1.9, 1.9], size=8.5)
H("4.1.4  Conventional Models Against the Tail", 3)
P(f"Table 5 answers the first half of RQ2. Fitted to all observations, the lognormal reproduces {100*under[nUS]:.0f} percent of the generalized Pareto 99.5 "
  f"percent quantile for the United States, {100*under[nDK]:.0f} percent for Denmark, {100*under[nNO]:.0f} percent for Norway, {100*under[nNZ]:.0f} percent for New Zealand "
  f"and {100*under[nAU]:.0f} percent for Australia; the normal distribution does worse, and in the two smallest registers it falls below the empirical quantile. "
  f"That comparison is the one practitioners make, but it is not entirely fair, because the lognormal is being asked to describe the body and the tail at "
  f"once. Fitted above the same threshold, as a left-truncated distribution, the lognormal recovers {100*min(under_tr[n] for n in EXNZ):.0f} to "
  f"{100*max(under_tr[n] for n in EXNZ):.0f} percent of the generalized Pareto quantile in the four registers other than New Zealand, where it overshoots, and "
  f"{100*min(under_sh[n] for n in EXNZ):.0f} to {100*max(under_sh[n] for n in EXNZ):.0f} percent when fitted to the excesses themselves. Most of the familiar "
  f"understatement at 99.5 percent is therefore a consequence of fitting the body, not of the lognormal form; the two families part company further out, "
  f"where the truncated lognormal gives {100*min(under_tr9[n] for n in EXNZ):.0f} to {100*max(under_tr9[n] for n in EXNZ):.0f} percent of the generalized Pareto "
  f"99.9 percent quantile, and in the tail mean, which the lognormal always keeps finite. At 99.9 percent the generalized Pareto quantile exceeds the largest observed "
  f"loss in every register except New Zealand, which is the property that makes it useful for capital: it extrapolates beyond the record instead of being "
  f"bounded by it. The lognormal tail value-at-risk at 99.5 percent, finite for any parameter, is {100*DK['lognormal_TVaR_0995']/DK['risk']['0.995']['TVaR']:.0f} "
  f"percent of the generalized Pareto figure for the Danish data and {100*US['lognormal_TVaR_0995']/US['risk']['0.995']['TVaR']:.0f} percent for the United States "
  f"at the median threshold.", indent=True)
TABLE("Table 5. Loss quantiles at 99.5 percent: conventional models fitted to all data and above the threshold, generalized Pareto tail and empirical (loss units of Table 1)",
      ["Register", "Normal (all data)", "Lognormal (all data)", "Lognormal truncated at u", "Lognormal on excesses", "GPD", "Empirical", "Lognormal (all) ÷ GPD", "Truncated ÷ GPD", "Truncated ÷ GPD at 99.9%"],
      [[short[n], f0(D[n]["compare"]["0.995"]["normal"]), f0(D[n]["compare"]["0.995"]["lognormal"]), f0(CMP[n]["auto"]["quantiles"]["0.995"]["trunc_lognormal"]), f0(CMP[n]["auto"]["quantiles"]["0.995"]["shifted_lognormal"]),
        f0(D[n]["compare"]["0.995"]["gpd"]), f0(D[n]["compare"]["0.995"]["empirical"]), f"{100*under[n]:.0f}%", f"{100*under_tr[n]:.0f}%", f"{100*under_tr9[n]:.0f}%"] for n in names],
      note="Note. All fits at the ForwardStop (median) threshold. Normal and lognormal (all data) by maximum likelihood on every observation; lognormal truncated at u by maximum likelihood on observations above u with the likelihood conditioned on exceedance; lognormal on excesses fitted to X − u. Quantiles of the threshold models use the empirical exceedance probability N_u/n as in equation (2).",
      widths=[2.3, 1.5, 1.6, 1.7, 1.6, 1.4, 1.4, 1.6, 1.4, 1.5], size=7.5)
H("4.1.5  The United States: Frequency Trend and Annual Aggregate", 3)
P(f"Because the U.S. record is dated it supports the question a capital regime asks, which is the loss from a year rather than from an event. Table 6 and "
  f"Figure 3 give the answer at the high threshold. The number of billion-dollar events per year rose from an average of {F['mean_1980s']:.1f} in the 1980s to "
  f"{F['mean_2015_24']:.1f} in 2015–2024, a Poisson trend of {F['trend_pct']:.1f} percent a year (p < 0.001). At the fitted 2024 rate of {F['rate_2024_fit']:.1f} events "
  f"the compound-Poisson model gives a mean annual aggregate of USD {bn(A24['mean'])} billion, a 1-in-100-year aggregate of USD {bn(A24['p99'])} billion and a "
  f"1-in-200-year aggregate of USD {bn(A24['p995'])} billion, against a worst observed year, {AG['empirical_annual']['year_max']}, of USD "
  f"{bn(AG['empirical_annual']['max'])} billion; the tail value-at-risk beyond the 1-in-200 point is USD {bn(A24['tvar995'])} billion. At the 2015–2024 mean "
  f"frequency of {AREC['lam']:.1f} events the 1-in-200 aggregate is USD {bn(AREC['p995'])} billion, and at the 1980–2024 mean of {AALL['lam']:.1f} events it is USD "
  f"{bn(AALL['p995'])} billion, so the frequency trend alone raises the capital point by {100*(A24['p995']/AALL['p995']-1):.0f} percent. The bootstrap interval for "
  f"the headline figure, from 200 resamples of the register, runs from USD {bn(BOOT['ci'][0])} to {bn(BOOT['ci'][1])} billion, and its Monte-Carlo error across "
  f"seeds is {100*MC['cv']:.1f} percent of the estimate, so the sampling uncertainty of the register, not the simulation, is what limits precision. The same "
  f"tail prices reinsurance: the expected annual loss to a USD 50 billion excess of USD 50 billion per-event layer is USD "
  f"{LAY['50bn xs 50bn']['gpd']*F['rate_2024_fit']/1000:.2f} billion under the fitted tail against USD {LAY['50bn xs 50bn']['empirical']*F['rate_2024_fit']/1000:.2f} "
  f"billion on the empirical distribution, and for the USD 100 billion excess of USD 100 billion layer, which no observed event has reached, the fitted tail "
  f"still assigns USD {LAY['100bn xs 100bn']['gpd']*F['rate_2024_fit']/1000:.2f} billion a year.", indent=True)
TABLE("Table 6. U.S. billion-dollar disasters: frequency trend and compound-Poisson annual aggregate at the high threshold (USD billion, 2024 prices)",
      ["Quantity", "1980–2024 mean frequency", "2015–2024 mean frequency", "Fitted 2024 frequency", "Observed 1980–2024"],
      [["Events per year (λ)", f"{AALL['lam']:.1f}", f"{AREC['lam']:.1f}", f"{F['rate_2024_fit']:.1f}", f"{F['mean_1980s']:.1f} (1980s) → {F['mean_2015_24']:.1f} (2015–24)"],
       ["Mean annual aggregate", bn(AALL["mean"]), bn(AREC["mean"]), bn(A24["mean"]), bn(AG["empirical_annual"]["mean"])],
       ["1-in-100-year aggregate (99%)", bn(AALL["p99"]), bn(AREC["p99"]), bn(A24["p99"]), "–"],
       ["1-in-200-year aggregate (99.5%)", bn(AALL["p995"]), bn(AREC["p995"]), f"{bn(A24['p995'])}\n(bootstrap {bn(BOOT['ci'][0])}–{bn(BOOT['ci'][1])})", f"worst year {AG['empirical_annual']['year_max']}: {bn(AG['empirical_annual']['max'])}"],
       ["1-in-1,000-year aggregate (99.9%)", bn(AALL["p999"]), bn(AREC["p999"]), bn(A24["p999"]), "–"],
       ["TVaR beyond 99.5%", bn(AALL["tvar995"]), bn(AREC["tvar995"]), bn(A24["tvar995"]), "–"],
       ["Expected annual loss, layer 40 xs 10", f"{LAY['40bn xs 10bn']['gpd']*AALL['lam']/1000:.1f}", f"{LAY['40bn xs 10bn']['gpd']*AREC['lam']/1000:.1f}", f"{LAY['40bn xs 10bn']['gpd']*F['rate_2024_fit']/1000:.1f}", f"{LAY['40bn xs 10bn']['empirical']*F['rate_2024_fit']/1000:.1f} (empirical, 2024 rate)"],
       ["Expected annual loss, layer 50 xs 50", f"{LAY['50bn xs 50bn']['gpd']*AALL['lam']/1000:.2f}", f"{LAY['50bn xs 50bn']['gpd']*AREC['lam']/1000:.2f}", f"{LAY['50bn xs 50bn']['gpd']*F['rate_2024_fit']/1000:.2f}", f"{LAY['50bn xs 50bn']['empirical']*F['rate_2024_fit']/1000:.2f} (empirical, 2024 rate)"]],
      note=f"Note. Frequency from a Poisson regression of annual counts on year; aggregates from 40,000 compound-Poisson simulations with empirical severity below the high threshold (90th percentile, ξ̂ = {f2(US['hi']['xi'])}) and the fitted tail above it; the median-threshold alternative is in Table 9. Bootstrap interval from 200 resamples of the register (10,000 simulated years each); Monte-Carlo coefficient of variation across five seeds {100*MC['cv']:.1f} percent. Layer notation: limit xs attachment, per event, USD billion.",
      widths=[4.0, 2.6, 2.6, 2.8, 4.0], size=8)
FIG(f"{FIGS}/fig3_noaa_agg.png", "Figure 3. (a) Annual number of U.S. billion-dollar disasters, 1980–2024, with the fitted Poisson trend; (b) simulated annual aggregate loss at the 2024 frequency and the high-threshold severity, with the 1-in-200-year point and the worst observed year. Source: NOAA NCEI / Climate Central.")
H("4.1.6  Egypt's Fire Line Through the Same Lens", 3)
P(f"Egypt publishes no event-level catastrophe losses, but its fire line, the class that carries property-catastrophe exposure, is reported every year, and "
  f"Table 7 assembles it. Direct premiums grew from EGP {egp['2014/15']/1e6:.2f} billion in 2014/15 to EGP {egp['2023/24']/1e6:.2f} billion in 2023/24, a rise of "
  f"{100*(egp['2023/24']/egp['2014/15']-1):.0f} percent that owes much to inflation and asset revaluation after the 2016 and 2022–2024 devaluations, while direct "
  f"claims rose {100*(egc['2023/24']/egc['2014/15']-1):.0f} percent. The loss ratio is anything but smooth. It reached {100*lr['2018/19']:.0f} percent in 2018/19, when "
  f"claims of EGP {egc['2018/19']/1e6:.2f} billion were {egc['2018/19']/egc['2019/20']:.1f} times the following year's, and lay between {lr_other_min:.0f} and "
  f"{lr_other_max:.0f} percent in every other year in the table; for 2025 the Authority reports a loss ratio of {100*EGF['y2025']['loss_ratio']:.0f} percent, a "
  f"retention rate of {100*EGF['y2025']['retention']:.0f} percent and a fire share of {100*EGF['y2025']['fire_share_of_premiums']:.0f} percent of property premiums. One "
  f"year in seven with a loss ratio two to four times the others is the aggregate footprint of a heavy-tailed severity, and with {100*(1-EGF['y2025']['retention']):.0f} "
  f"percent of the line ceded the price and structure of reinsurance is where that tail is actually managed. A premium-based margin of the kind Decision "
  f"148/2025 retains would have read 2018/19 and 2019/20 identically. Two cautions apply to the reading. The series is a market aggregate, so a single large "
  f"event and a cluster of medium ones leave the same mark, and the fiscal years before 2025 ran from July to June, so an event in a wet winter is split "
  f"across the years in which claims are paid; neither weakens the point that a line whose claims can triple from one year to the next is not described by "
  f"its average loss ratio. What the aggregate cannot give is the shape, and without the shape neither a return level nor a layer price can be computed for "
  f"the line. That absence, rather than any estimate, is the empirical result for Egypt.", indent=True)
TABLE("Table 7. Egypt's fire insurance line, 2014/15 to 2023/24 (EGP million)",
      ["Fiscal year", "Direct premiums", "Direct claims paid", "Loss ratio", "Premium growth"],
      [[k, f"{egp[k]/1000:,.0f}", f"{egc[k]/1000:,.0f}", f"{100*lr[k]:.0f}%", ("–" if i == 0 else f"{100*(egp[k]/egp[list(egp)[i-1]]-1):.0f}%")] for i, k in enumerate(egp)] +
      [["2025 (calendar)", f"{100*EGF['y2025']['fire_share_of_premiums']:.0f}% of property premiums", "–", f"{100*EGF['y2025']['loss_ratio']:.0f}%", f"retention {100*EGF['y2025']['retention']:.0f}%"]],
      note="Note. 2018/19–2023/24 from the FRA Insurance Statistical Books 2022/2023 and 2023/2024, Tables 1/6 and 2/6 (FRA, 2024, 2025a); 2014/15 as stated by the Insurance Federation of Egypt (Al-Mal, 2026a); 2025 ratios as stated by the FRA Deputy Chairman for insurance (Al-Mal, 2026b). Growth for 2018/19 is over the four years from 2014/15. The fiscal year was aligned with the calendar year from 1 January 2025.",
      widths=[2.6, 3.4, 3.2, 2.2, 3.0], size=9)

# ------------------------------------------------------------------ 4.2 ROBUSTNESS
H("4.2  Robustness and Sensitivity", 2)
P("Section 3.3 announced five checks: the comparison of selection rules, the high-threshold refit, the U.S. threshold ladder with its bootstrap and "
  "Monte-Carlo uncertainty, the comparators refitted above the threshold, and the shape trace against the profile band. The fourth was reported with "
  "Table 5; the others follow.", indent=True)
H("4.2.1  What the Selection Rules Choose", 3)
P(f"Table 8 shows that the ForwardStop rule's choice depends on the register's size as much as on its tail. On the three catastrophe registers, with "
  f"{NZ['n']} to {US['n']} events, the rule returns the floor of whatever grid it is given, the 10th, 25th or 50th percentile, at every level of α from 0.01 to "
  f"0.10: the bootstrap Anderson–Darling p-values never fall below 0.05 anywhere on the grid, so there is nothing for the rule to reject, and its answer is "
  f"a property of the grid rather than of the data. On the two fire registers, with thousands of observations, the test has power and the rule starts to "
  f"bite, but it then becomes sensitive to α instead. Started at the 10th percentile it rejects the Danish thresholds up to the 25th percentile and selects "
  f"the {100*fs(nDK,0.10,0.01)['q']:.1f}th at α = 0.01, the {100*fs(nDK,0.10,0.05)['q']:.1f}th at α = 0.05 and the {100*fs(nDK,0.10,0.10)['q']:.0f}th at α = 0.10, with "
  f"the shape between {f2(min(fs(nDK,0.10,a)['xi'] for a in (0.01,0.05,0.10)))} and {f2(max(fs(nDK,0.10,a)['xi'] for a in (0.01,0.05,0.10)))} at all three; for the "
  f"Norwegian fires it rejects everything below the {100*fs(nNO,0.10,0.01)['q']:.1f}th percentile at α = 0.01 and below the {100*fs(nNO,0.10,0.05)['q']:.1f}th at "
  f"α = 0.05, where the shape is {f2(fs(nNO,0.10,0.05)['xi'])} rather than {f2(NO['xi'])}. The rule is doing what it was designed to do, which is to reject "
  f"thresholds below which the generalized Pareto distribution does not fit; it is simply that on short registers nothing is rejected and on long ones the "
  f"outcome turns on the level chosen.", indent=True)
P(f"The expected-quantile-discrepancy rule behaves differently because it rewards closeness of the fitted quantiles rather than mere non-rejection. For the "
  f"U.S. record it selects the {SEL[nUS]['eqd_choice']['q']*100:.0f}th percentile, where the shape is {f2(SEL[nUS]['eqd_choice']['xi'])}, which is the high-threshold "
  f"fit the paper uses; for the Danish fires the {SEL[nDK]['eqd_choice']['q']*100:.1f}th percentile with a shape of {f2(SEL[nDK]['eqd_choice']['xi'])} on "
  f"{SEL[nDK]['eqd_choice']['nu']:,} exceedances, for the Norwegian fires the {SEL[nNO]['eqd_choice']['q']*100:.0f}th ({f2(SEL[nNO]['eqd_choice']['xi'])}), for New "
  f"Zealand the {SEL[nNZ]['eqd_choice']['q']*100:.1f}th ({f2(SEL[nNZ]['eqd_choice']['xi'])}) and for Australia the {SEL[nAU]['eqd_choice']['q']*100:.1f}th, where the "
  f"shape is {f2(SEL[nAU]['eqd_choice']['xi'])} on {SEL[nAU]['eqd_choice']['nu']} exceedances. The stability rule, which asks for the lowest threshold whose "
  f"profile interval contains every higher estimate, selects the {SEL[nUS]['stability_choice']['q']*100:.1f}th percentile for the United States, the "
  f"{SEL[nDK]['stability_choice']['q']*100:.0f}th for the Danish fires, the {SEL[nNO]['stability_choice']['q']*100:.0f}th for the Norwegian fires and the "
  f"{SEL[nAU]['stability_choice']['q']*100:.1f}th for Australia, and the floor for New Zealand, whose estimates never leave the wide band of the lowest fit. Two "
  f"conclusions follow. The fire tails are Pareto-type with a shape between about 0.6 and 0.8 under every rule and every threshold, which is the firm "
  f"evidence in this paper. The short catastrophe registers are not so settled: for the United States and Australia the discrepancy and stability rules "
  f"both point to thresholds at which the shape is well below the median-threshold value, so the instability documented for the U.S. record in Section "
  f"4.2.2 is a feature of short registers generally, and the headline shapes for those registers should be read with the interval and the threshold "
  f"attached.", indent=True)
def selrow(n):
    S = SEL[n]; st = S["stability_choice"]
    return [short[n], f"q{fs(n,0.50,0.05)['q']:.2f} ({f2(fs(n,0.50,0.05)['xi'])})", f"q{fs(n,0.25,0.05)['q']:.3f} ({f2(fs(n,0.25,0.05)['xi'])})", f"q{fs(n,0.10,0.05)['q']:.3f} ({f2(fs(n,0.10,0.05)['xi'])})",
            f"q{fs(n,0.10,0.01)['q']:.3f} / q{fs(n,0.10,0.10)['q']:.3f}", f"q{S['eqd_choice']['q']:.3f} ({f2(S['eqd_choice']['xi'])}), N_u = {S['eqd_choice']['nu']:,}",
            (f"q{st['q']:.3f} ({f2(st['xi'])})" if st else "none"), f"q{D[n]['hi']['q_u']:.3f} ({f2(D[n]['hi']['xi'])})"]
TABLE("Table 8. Threshold chosen by three automated rules (quantile of the register; ξ̂ at that threshold in parentheses)",
      ["Register", "ForwardStop from q0.50, α 0.05", "ForwardStop from q0.25", "ForwardStop from q0.10", "ForwardStop from q0.10, α 0.01 / 0.10", "EQD rule (Murphy et al.)", "Stability rule", "High threshold (fixed)"],
      [selrow(n) for n in names],
      note="Note. Candidate grid: quantiles 0.10 to 0.95 in steps of 0.025 with at least 40 exceedances; Anderson–Darling p-values from 150 parametric-bootstrap replications; EQD = expected quantile discrepancy averaged over 100 bootstrap refits at 500 probability points, scaled by the median excess; stability rule = lowest candidate whose 95 percent profile interval contains every shape estimate at higher candidates with at least 25 exceedances.",
      widths=[2.3, 2.3, 2.0, 2.0, 2.4, 2.9, 1.9, 1.9], size=7.5)
H("4.2.2  Threshold Dependence of the U.S. Capital Figures", 3)
P(f"Table 9 traces the U.S. fit across seven thresholds. The shape declines from {f2(L50['xi'])} at the median through {f2(LAD['0.75']['xi'])} at the 75th and "
  f"{f2(LAD['0.85']['xi'])} at the 85th percentile to {f2(L90['xi'])} at the 90th, where {L90['nu']} exceedances remain; the profile interval at the 90th percentile, "
  f"{f2(L90['xi_ci'][0])} to {f2(L90['xi_ci'][1])}, contains every lower estimate, whereas the interval at the median, {f2(US['xi_ci'][0])} to {f2(US['xi_ci'][1])}, "
  f"excludes the high-threshold value. The ratio of tail value-at-risk to value-at-risk at 99.5 percent falls from {ratio_med_US:.1f} to {ratio[nUS]:.1f} along "
  f"the same path, and the 1-in-200-year aggregate at the 2024 frequency from USD {bn(L50['agg_p995_2024'])} billion to USD {bn(L90['agg_p995_2024'])} billion, "
  f"with the intermediate thresholds in between. The median-threshold figure exceeds a tenth of U.S. output; it is the arithmetic consequence of a shape "
  f"near one and the practical reason for treating that fit as an upper bound. The high-threshold figure is the one the diagnostics support: the mean-excess "
  f"plot in Figure 4 bends rather than straightens below the 90th percentile, the shape trace drifts out of the median fit's profile band as the threshold "
  f"rises, the expected-quantile-discrepancy rule selects the same threshold independently, and the return-level curve in Figure 5 passes through the "
  f"empirical points instead of above them. Its own uncertainty is nonetheless large, a bootstrap interval of USD {bn(BOOT['ci'][0])} to {bn(BOOT['ci'][1])} "
  f"billion, and that width, not the point, is what a supervisor should carry. Two further readings of Table 9 are worth drawing out. The 2015–2024 mean "
  f"frequency, which smooths the last decade rather than extrapolating the trend to a single year, gives a 1-in-200 aggregate of USD "
  f"{bn(L90['agg_p995_recent'])} billion at the high threshold, so the choice between a fitted rate and a recent average moves the figure by roughly an "
  f"eighth while the choice of threshold moves it by a factor of {L50['agg_p995_2024']/L90['agg_p995_2024']:.0f}; the severity model, not the frequency "
  f"model, is where the capital uncertainty lives. And the Monte-Carlo coefficient of variation of {100*MC['cv']:.1f} percent confirms that 40,000 simulated "
  f"years are enough for the quantile; the bootstrap band is wide because {L90['nu']} exceedances cannot pin the shape down, not because the simulation is "
  f"short.", indent=True)
TABLE("Table 9. U.S. billion-dollar disasters: shape, tail ratio and 1-in-200-year annual aggregate by threshold (USD billion, 2024 prices)",
      ["Threshold quantile", "u (USD bn)", "N_u", "ξ̂ (95% profile CI)", "VaR 99.5% per event", "TVaR 99.5% per event", "TVaR ÷ VaR", "1-in-200 aggregate, 2024 rate", "1-in-200 aggregate, 2015–24 rate"],
      [[f"q{q}", f"{LAD[q]['u']/1000:.1f}", str(LAD[q]["nu"]), f"{f2(LAD[q]['xi'])} ({f2(LAD[q]['xi_ci'][0])}, {f2(LAD[q]['xi_ci'][1])})", bn(LAD[q]["var995"]), f0(LAD[q]["tvar995"] / 1000) if LAD[q]["tvar995"] and math.isfinite(LAD[q]["tvar995"]) else "∞",
        (f"{LAD[q]['ratio']:.1f}" if LAD[q]["ratio"] else "∞"), bn(LAD[q]["agg_p995_2024"]), bn(LAD[q]["agg_p995_recent"])] for q in ("0.50", "0.60", "0.70", "0.75", "0.80", "0.85", "0.90")],
      note=f"Note. Each row refits the generalized Pareto distribution above the stated quantile and re-simulates 40,000 compound-Poisson years with the empirical body below it. The q0.90 row reports the 40,000-year simulation of Table 6. Monte-Carlo coefficient of variation across five seeds: {100*MC['cv']:.1f} percent at q0.90 and {100*MCA['cv']:.1f} percent at q0.50, where the shape near one makes the simulated quantile itself unstable. Bootstrap interval of the q0.90 aggregate at the 2024 rate: USD {bn(BOOT['ci'][0])}–{bn(BOOT['ci'][1])} billion (200 resamples).",
      widths=[2.0, 1.6, 1.0, 2.6, 1.8, 1.9, 1.3, 2.3, 2.3], size=8)
FIG(f"{FIGS}/fig4_threshold.png", "Figure 4. Threshold diagnostics for the U.S. disaster and Danish fire registers: mean-excess function (top) and shape estimate by threshold on the grid from the 10th percentile (bottom), with the 95 percent profile band of the ForwardStop fit and the thresholds chosen by the ForwardStop, EQD and stability rules and the fixed high threshold.", width_cm=14)
H("4.2.3  High-Threshold Refits, Intervals and the Hill Check", 3)
P(f"At the high threshold the two fire estimates ease from {f2(DK['xi'])} to {f2(DK['hi']['xi'])} (Danish) and from {f2(NO['xi'])} to {f2(NO['hi']['xi'])} (Norwegian), "
  f"movements that stay inside the profile intervals of the median fits, and the high-threshold return levels in Table 4 lie close to the median ones. For "
  f"the two small catastrophe registers the high threshold leaves {NZ['hi']['nu']} and {AU['hi']['nu']} exceedances and intervals ({f2(NZ['hi']['xi_ci'][0])} to "
  f"{f2(NZ['hi']['xi_ci'][1])}; {f2(AU['hi']['xi_ci'][0])} to {f2(AU['hi']['xi_ci'][1])}) too wide to be informative, so the median fit is the usable one there. The "
  f"shape-stability panels of Figure 4 show the Danish trace staying inside the profile band across the grid and the U.S. trace drifting out of it, and the "
  f"intervals behave as small-sample theory predicts: narrow for the fire registers, wide and right-skewed for the catastrophe registers, with the U.S. "
  f"upper limit at {f2(US['hi']['xi_ci'][1])} even at the high threshold. The inability to exclude ξ ≥ 1 in the three catastrophe registers is therefore a "
  f"property of the data, not of one threshold. The Hill estimates in Table 2 agree with the maximum-likelihood shapes within their intervals, so the "
  f"heaviness of the tail does not depend on the generalized Pareto family being the right one.", indent=True)
FIG(f"{FIGS}/fig5_returnlevel.png", "Figure 5. Return-level curves at the ForwardStop threshold (solid) and the high threshold (dashed) against empirical return periods (grey points) for the U.S., Danish and New Zealand registers; the dotted line marks 200 events.")
P(f"The headline findings survive these checks with one qualification that the paper now states as a result rather than a caveat. Every register keeps a "
  f"Pareto-type tail at every threshold, the fire shapes remain above 0.5 and inside their intervals, the lognormal fitted above the threshold narrows but does not close the gap at "
  f"the extreme quantiles and never reproduces the tail mean, and tail value-at-risk exceeds value-at-risk at every fit where it exists. The U.S. capital figures, however, "
  f"are a function of the threshold to within a factor of about {L50['agg_p995_2024']/L90['agg_p995_2024']:.0f}, and no goodness-of-fit rule resolves that; the "
  f"quantile-discrepancy rule, the stability diagnostic and the plausibility of the return levels do.", indent=True)

# ------------------------------------------------------------------ 4.3 DISCUSSION
H("4.3  Discussion", 2)
P(f"The five registers, drawn from three continents and two perils, agree on the order of magnitude of the tail. Shape parameters between "
  f"{f2(min(xi_head.values()))} and {f2(max(xi_head.values()))} place catastrophe and large-fire losses among the heaviest tails in applied statistics, heavier "
  f"than equity returns and comparable to operational and cyber losses (Chavez-Demoulin et al., 2016; Eling & Wirfs, 2019). The Danish estimate of "
  f"{f2(DK['xi'])} sits at the upper end of the 0.5 to 0.7 range that McNeil (1997) obtained with hand-picked thresholds, the verdict of infinite variance agrees "
  f"with the formal test of Wong et al. (2021), and the Swedish windstorm and large-claim tails of Rootzén and Tajvidi (1997) and Cebrián et al. (2003) are "
  f"of the same order, so the result is not an artefact of one peril or one register. Two consequences follow. The variance exists in none of the "
  f"registers, so any pricing or capital rule built on a standard deviation, including the standard-deviation premium principle that Chao (2022) applies to "
  f"catastrophe layers, estimates a quantity that is not there. And in the three catastrophe registers the data cannot exclude a shape of one, at which "
  f"the tail mean itself fails; the response is not to abandon tail value-at-risk but to report the shape interval beside it, to cap the modelled severity at "
  f"a defensible physical maximum when the interval crosses one, and to read the resulting figure as a lower bound.", indent=True)
P(f"On threshold selection the evidence qualifies, without contradicting, the case for automation. Bader, Yan and Zhang's (2018) rule performed as designed: "
  f"the generalized Pareto distribution is indeed adequate from the median upward in every register. But adequacy on registers that begin at a reporting "
  f"threshold is nearly guaranteed, and the rule then returns the floor of its grid, as Table 8 shows from three starting points. Murphy, Tawn and Varty's "
  f"(2025) quantile-discrepancy rule, which asks a stronger question, picked the U.S. threshold that the stability diagnostic and the return-level plot "
  f"support, and for the fire registers it picked thresholds at which the shape is within a few hundredths of the median fit. This is the caution of "
  f"Scarrott and MacDonald (2012), that no single criterion suffices, restated on five registers with a practical corollary: a goodness-of-fit selector "
  f"should be paired with a discrepancy or stability selector, and the capital figure should be reported across the thresholds they bracket. New Zealand "
  f"marks the limit of the method altogether. With {NZ['n']} events and one earthquake that is most of all recorded loss, the fitted tail is governed by a "
  f"single observation, the shape interval runs from {f2(NZ['xi_ci'][0])} to {f2(NZ['xi_ci'][1])} and the fitted 99.5 percent quantile falls below the empirical "
  f"one; extreme value theory can bound what such a register supports, and no more, which is why the headline ranges above exclude it.", indent=True)
P(f"For capital the results supply three numbers a regime should carry. The first is the ratio of tail value-at-risk to value-at-risk at the calibration "
  f"level, between {min(ratio.values()):.1f} and {max(ratio.values()):.1f} here and discarded by a quantile-only rule. The second is the 1-in-200 annual "
  f"aggregate, which for the United States is about two and a half times the worst observed year at the high threshold and rises with the frequency trend; "
  f"the trend of {F['trend_pct']:.1f} percent a year matches the figure Smith and Katz (2013) reported, and the reading here follows theirs and that of Pielke et "
  f"al. (2008) in attributing part of it to exposure growth and reporting rather than hazard alone, while its direction agrees with Barthel and Neumayer "
  f"(2012) for normalised U.S. insured losses. The third is the extrapolated layer cost: a layer no observed event has reached still carries a positive "
  f"expected loss under the fitted tail, which is why such layers are priced and bought and which extends McNeil's (1997) layer-pricing use of the model "
  f"beyond the record. For a market like Egypt's, where two-fifths of fire premium is retained and the rest ceded, those layer prices translate directly "
  f"into the question of where the retention should sit relative to modelled return levels.", indent=True)
P("The findings also bear on how a supervisor should read a catastrophe model submitted for approval. A model that reports a single threshold, a point "
  "estimate of the shape and a 99.5 percent quantile has withheld the three facts that decide whether the figure is credible: whether the shape interval "
  "crosses one, how the quantile moves across defensible thresholds, and how much expected loss lies beyond it. None of the three requires a different "
  "model; each is a by-product of the estimation already performed, and the cost of requiring them is a few lines in a reporting template. The same holds "
  "for a reinsurance buyer deciding a retention: the return-level curve and its interval, not the quantile at one threshold, are what the decision turns "
  "on.", indent=True)
P("The two regimes are at different stages. Saudi Arabia's framework takes effect in 2027 with a standard formula and an internal-model option; whether its "
  "catastrophe calibration imports European scenarios or rests on regional loss records is not yet public, and the evidence here says what it should "
  "report either way, a shape interval and a tail value-at-risk beside the quantile. Egypt's task comes earlier. Decision 148/2025 has no catastrophe "
  "module, the statistical book reports fire claims only in aggregate, and no event-level register exists for the storms, floods and fires the market pays "
  "for; this is the data scarcity that the G20 Sustainable Finance Working Group (2025) names first and that Holzheu and Turner (2018) map for the region. "
  "The 2018/19 loss ratio in Table 7 is the argument for a register, a catastrophe loading in the interim and retentions set against return levels, and "
  "Section 5.1 states them as recommendations to the bodies concerned.", indent=True)

# ------------------------------------------------------------------ 5 CONCLUSION
H("5.  Conclusion and Policy Implications", 1)
H("5.1  Conclusion and Regulatory Implications", 2)
P(f"The three questions can now be answered. On RQ1, the tails are Pareto-type with shape parameters of {f2(min(xi_head.values()))} to "
  f"{f2(max(xi_head.values()))}, the variance exists nowhere, the mean is in doubt in the three catastrophe registers, and the answer depends on the threshold "
  f"only in the U.S. record, where the shape moves from {f2(US['xi'])} to {f2(US['hi']['xi'])} and a goodness-of-fit selector cannot tell; a quantile-discrepancy "
  f"selector and the stability trace can. On RQ2, the lognormal fitted to all data captures {100*min(under.values()):.0f} to {100*max(under.values()):.0f} percent of "
  f"the generalized Pareto 99.5 percent quantile and {100*min(under_tr[n] for n in EXNZ):.0f} to {100*max(under_tr[n] for n in EXNZ):.0f} percent when fitted above the same "
  f"threshold, so the understatement that matters for capital lies beyond the quantile, in the tail mean, and tail value-at-risk exceeds value-at-risk by a factor of {min(ratio.values()):.1f} to {max(ratio.values()):.1f}. On RQ3, the U.S. frequency "
  f"of billion-dollar events has risen by {F['trend_pct']:.1f} percent a year, the 1-in-200-year aggregate at the current rate is about USD {bn(A24['p995'])} "
  f"billion within a bootstrap band of USD {bn(BOOT['ci'][0])} to {bn(BOOT['ci'][1])} billion, and Egypt's fire line shows the same tail in aggregate form, one "
  f"year in seven with a loss ratio of {100*lr['2018/19']:.0f} percent; both regimes need a catastrophe module that carries a tail value-at-risk and a return "
  f"level rather than a premium share or a quantile alone.", indent=True)
P(f"For Egypt's Financial Regulatory Authority three measures follow. A mandatory event-level large-loss register for fire and property, with a reporting "
  f"threshold and price adjustment in the manner of the Danish and Norwegian data, is the precondition for any tail estimate, since Table 7 shows that the "
  f"statistical book's aggregates reveal the footprint of a heavy tail but not its shape. Until that register holds a decade of events, the fire line should "
  f"carry an explicit catastrophe loading in the solvency calculation in place of the premium-based margin of Decision 148/2025, which would have read "
  f"2018/19 and 2019/20 identically. And on a line that cedes {100*(1-EGF['y2025']['retention']):.0f} percent of its premium, the Authority should expect "
  f"reinsurance retentions to be set against modelled return levels of the kind in Table 4 rather than against premium volume. The register cannot be "
  f"built by the regulator alone: Misr Insurance and the Insurance Federation of Egypt, which already compile the market statements behind Table 7, are the "
  f"natural hosts of a pooled large-loss database on the Danish model, with a common threshold, anonymised event records and annual price adjustment.", indent=True)
P(f"For Saudi Arabia's Insurance Authority the catastrophe component of the framework that takes effect on 1 January 2027 should be calibrated in two ways "
  f"the evidence supports. Whatever stress is prescribed should be checked against a generalized Pareto return level fitted to Gulf and regional loss "
  f"records rather than imported unchanged from European scenarios, and because no published event-level register exists for the flood and storm events "
  f"to which the Kingdom is exposed, a national loss register built with the same threshold and indexation discipline is the precondition for that check. "
  f"Internal models approved under the new regime should be required to report the shape interval and a tail value-at-risk alongside the 99.5 percent "
  f"value-at-risk, since Table 3 shows the quantile alone omits an expected tail loss of {min(ratio.values()):.1f} to {max(ratio.values()):.1f} times its own size, and "
  f"to state the threshold at which the severity was fitted, since Table 9 shows how far the capital figure moves with it.", indent=True)
P(f"For reinsurers and for the International Association of Insurance Supervisors, whose capital standard the national regimes follow, the finding that the "
  f"variance exists in none of the five registers means that the standard-deviation premium principle, and any capital charge scaled by a standard "
  f"deviation, is estimating a quantity that is not there. The layer costs of Table 6, which assign USD {LAY['100bn xs 100bn']['gpd']*F['rate_2024_fit']/1000:.2f} "
  f"billion a year to a layer no observed event has reached, and the ratios of Table 3 are the measures that should replace it in pricing excess-of-loss "
  f"layers and in calibrating capital for heavy-tailed lines. The event that matters to an insurer is the one it has not yet seen, and estimating it honestly includes reporting how wide "
  f"the interval is.", indent=True)
H("5.2  Limitations of the Study", 2)
P(f"Seven limitations apply. The catastrophe registers are short, and the New Zealand and Australian lists end in 2014; the U.S. record is total economic "
  f"rather than insured loss and, as Smith and Katz (2013) show, carries its own biases; the fire data are three decades old, although their tails remain "
  f"the benchmark. Losses are analysed in local units without normalisation across registers. The goodness-of-fit selector returns the floor of its grid "
  f"on truncated registers, so the thresholds reported as automated are, for that rule, choices of grid; the paper mitigates this with two further rules "
  f"but does not remove the judgement. The U.S. capital figures depend on the threshold to within a factor of about {L50['agg_p995_2024']/L90['agg_p995_2024']:.0f}, the "
  f"high-threshold fit rests on {US['hi']['nu']} exceedances, and the Australian shape is similarly threshold-dependent. The bootstrap intervals hold the selection step fixed and the compound-Poisson model "
  f"treats events as independent and severity as stationary, which ignores clustering within seasons, any trend in severity and the mixture of exposure "
  f"growth and hazard in the frequency trend. The Kolmogorov–Smirnov diagnostic is approximate even with a bootstrap p-value, and the New Zealand fit is "
  f"governed by one observation. Finally, Egypt's evidence is a market aggregate and part of it is reported in press accounts of official statements, so "
  f"the inference about its tail is indirect.", indent=True)
H("5.3  Future Research", 2)
P("The results suggest five propositions for further work.", body=True)
for t in [f"**P1.** Observed catastrophe and large-fire registers with more than 1,000 events have shape parameters between 0.6 and 0.9; registers with fewer than 300 events cannot exclude ξ ≥ 1.",
          "**P2.** On registers that begin at a reporting threshold, goodness-of-fit selectors choose the lowest candidate offered, whereas quantile-discrepancy and stability selectors choose higher thresholds; the two families diverge most where the shape trace is steepest.",
          "**P3.** The ratio of tail value-at-risk to value-at-risk at 99.5 percent on generalized Pareto tails exceeds two in every property-catastrophe register, so a quantile-only calibration omits at least half of the expected tail loss.",
          "**P4.** In markets with a rising event frequency the 1-in-200-year annual aggregate rises faster than the mean annual loss, so capital calibrated on average loss ratios falls behind.",
          "**P5.** Market-level loss ratios in emerging-market fire lines show one year in five to ten with a ratio more than twice the median, the aggregate signature of a shape above 0.5; an event-level register would raise the modelled 1-in-200 aggregate for such a line relative to a premium-based margin by a factor exceeding two."]:
    P(t, body=True, after=4)
P("P1 to P4 can be tested by replicating the procedure on other national registers; P5 requires the Egyptian and Gulf data that Section 5.1 calls for.", body=True)

if not BLIND:
    H("Declarations", 1)
    P(f"**Data and code availability.** The NOAA/Climate Central record and the CASdatasets files are public; the FRA statistical books are published on fra.gov.eg. The Python scripts that reproduce Tables 1–9 and Figures 1–5, the merged data and the results files are openly available at {REPO} (release v1.0.0).", after=2)
    _p = P("", align="j", after=6); _r = _p.add_run("Zenodo DOI: to be inserted after release"); _r.font.name = FONT; _r.font.size = Pt(12); _r.font.highlight_color = WD_COLOR_INDEX.YELLOW
    P("**Funding.** None.   **Conflicts of interest.** None.   **Ethics.** Not applicable; the study uses published aggregate and open data.", after=6)
    P("**Author contribution.** The author is solely responsible for the conception, analysis and writing of this article.", after=6)

H("References", 1)
refs = [
 "Al-Mal. (2026a, September 8). ارتفاع تعويضات تأمين الحريق لتسجل 1.53 مليار جنيه خلال 10 سنوات [Fire insurance claims rise to EGP 1.53 billion over ten years; statements by the Chairman of the Insurance Federation of Egypt]. Al-Mal News. https://almalnews.com/2134241/",
 "Al-Mal. (2026b, September). حصة تأمين الحريق من أقساط السوق 18% و42% معدل الاحتفاظ خلال 2025 [Fire insurance share of market premiums 18% and retention 42% in 2025; statements by the FRA Deputy Chairman]. Al-Mal News. https://almalnews.com/2134273/",
 "Al-Monitor. (2020, March 16). Egypt's 'dragon' storm leaves at least 20 dead. Al-Monitor. https://www.al-monitor.com/originals/2020/03/egypt-dragon-storm-rains-killing-20.html",
 "Artzner, P., Delbaen, F., Eber, J.-M., & Heath, D. (1999). Coherent measures of risk. Mathematical Finance, 9(3), 203–228. https://doi.org/10.1111/1467-9965.00068",
 "Bader, B., Yan, J., & Zhang, X. (2018). Automated threshold selection for extreme value analysis via ordered goodness-of-fit tests with adjustment for false discovery rate. The Annals of Applied Statistics, 12(1), 310–329. https://doi.org/10.1214/17-AOAS1092",
 "Balkema, A. A., & de Haan, L. (1974). Residual life time at great age. The Annals of Probability, 2(5), 792–804. https://doi.org/10.1214/aop/1176996548",
 "Barthel, F., & Neumayer, E. (2012). A trend analysis of normalized insured damage from natural disasters. Climatic Change, 113(2), 215–237. https://doi.org/10.1007/s10584-011-0331-2",
 "Beirlant, J., Goegebeur, Y., Segers, J., & Teugels, J. (2004). Statistics of extremes: Theory and applications. Wiley. https://doi.org/10.1002/0470012382",
 "Cebrián, A. C., Denuit, M., & Lambert, P. (2003). Generalized Pareto fit to the Society of Actuaries' large claims database. North American Actuarial Journal, 7(3), 18–36. https://doi.org/10.1080/10920277.2003.10596098",
 "Chao, W. (2022). Pricing catastrophe reinsurance under the standard deviation premium principle. AIMS Mathematics, 7(3), 4472–4484. https://doi.org/10.3934/math.2022249",
 "Chavez-Demoulin, V., Embrechts, P., & Hofert, M. (2016). An extreme value approach for modeling operational risk losses depending on covariates. Journal of Risk and Insurance, 83(3), 735–776. https://doi.org/10.1111/jori.12059",
 "Climate Central. (2026, March 9). U.S. billion-dollar weather and climate disasters: 2025 in review. Climate Central. https://www.climatecentral.org/report/us-billion-dollar-weather-and-climate-disasters-2025",
 "Coles, S. (2001). An introduction to statistical modeling of extreme values. Springer. https://doi.org/10.1007/978-1-4471-3675-0",
 "Danielsson, J., de Haan, L., Peng, L., & de Vries, C. G. (2001). Using a bootstrap method to choose the sample fraction in tail index estimation. Journal of Multivariate Analysis, 76(2), 226–248. https://doi.org/10.1006/jmva.2000.1903",
 "Davison, A. C., & Smith, R. L. (1990). Models for exceedances over high thresholds. Journal of the Royal Statistical Society: Series B, 52(3), 393–425. https://doi.org/10.1111/j.2517-6161.1990.tb01796.x",
 "Drees, H., & Kaufmann, E. (1998). Selecting the optimal sample fraction in univariate extreme value estimation. Stochastic Processes and their Applications, 75(2), 149–172. https://doi.org/10.1016/S0304-4149(98)00017-9",
 "Dutang, C., & Charpentier, A. (2020). CASdatasets: Insurance datasets (R package version 1.0-11) [Data set]. http://cas.uqam.ca",
 "Eling, M., & Wirfs, J. (2019). What are the actual costs of cyber risk events? European Journal of Operational Research, 272(3), 1109–1119. https://doi.org/10.1016/j.ejor.2018.07.021",
 "Embrechts, P., Klüppelberg, C., & Mikosch, T. (1997). Modelling extremal events for insurance and finance. Springer. https://doi.org/10.1007/978-3-642-33483-2",
 "Embrechts, P., Resnick, S. I., & Samorodnitsky, G. (1999). Extreme value theory as a risk management tool. North American Actuarial Journal, 3(2), 30–41. https://doi.org/10.1080/10920277.1999.10595797",
 "European Commission. (2015). Commission Delegated Regulation (EU) 2015/35 supplementing Directive 2009/138/EC (Solvency II), Articles 119–135 (natural catastrophe risk sub-module). Official Journal of the European Union, L 12.",
 "Financial Regulatory Authority. (2024). Insurance statistical book 2022/2023. Arab Republic of Egypt. https://fra.gov.eg",
 "Financial Regulatory Authority. (2025a). Insurance statistical book 2023/2024. Arab Republic of Egypt. https://fra.gov.eg",
 "Financial Regulatory Authority. (2025b, August 5). FRA issues new rules for the financial solvency margin to enhance the stability of the insurance sector: Board Decision No. 148 of 2025 on solvency standards for insurance and reinsurance companies. Arab Republic of Egypt. https://fra.gov.eg/en/?p=17204237",
 "G20 Sustainable Finance Working Group. (2025). Identify and address insurance protection gaps (Input paper). G20 South Africa.",
 "Gilli, M., & Këllezi, E. (2006). An application of extreme value theory for measuring financial risk. Computational Economics, 27(2–3), 207–228. https://doi.org/10.1007/s10614-006-9025-7",
 "Holzheu, T., & Turner, G. (2018). The natural catastrophe protection gap: Measurement, root causes and ways of addressing underinsurance for extreme events. The Geneva Papers on Risk and Insurance — Issues and Practice, 43(1), 37–71. https://doi.org/10.1057/s41288-017-0075-y",
 "Insurance Authority. (2026, April 5). The Insurance Authority announces the transition to the risk-based capital framework from 1 January 2027 [News release]. Kingdom of Saudi Arabia. https://www.ia.gov.sa/en/media-center/news/104",
 "Katz, R. W. (2002). Stochastic modeling of hurricane damage. Journal of Applied Meteorology, 41(7), 754–762. https://doi.org/10.1175/1520-0450(2002)041<0754:SMOHD>2.0.CO;2",
 "Kellner, R., & Gatzert, N. (2013). Estimating the basis risk of index-linked hedging strategies using multivariate extreme value theory. Journal of Banking & Finance, 37(11), 4353–4367. https://doi.org/10.1016/j.jbankfin.2013.07.043",
 "McNeil, A. J. (1997). Estimating the tails of loss severity distributions using extreme value theory. ASTIN Bulletin, 27(1), 117–137. https://doi.org/10.2143/AST.27.1.563210",
 "McNeil, A. J., Frey, R., & Embrechts, P. (2015). Quantitative risk management: Concepts, techniques and tools (Rev. ed.). Princeton University Press.",
 "Müller-Bloch, C., & Kranz, J. (2015). A framework for rigorously identifying research gaps in qualitative literature reviews. In Proceedings of the 36th International Conference on Information Systems (ICIS 2015), Fort Worth, TX. Association for Information Systems.",
 "Murphy, C., Tawn, J. A., & Varty, Z. (2025). Automated threshold selection and associated inference uncertainty for univariate extremes. Technometrics, 67(2), 215–224. https://doi.org/10.1080/00401706.2024.2421744",
 "NOAA National Centers for Environmental Information. (2025). U.S. billion-dollar weather and climate disasters, 1980–2024 [Data set]. https://www.ncei.noaa.gov/access/billions/",
 "Northrop, P. J., & Coleman, C. L. (2014). Improved threshold diagnostic plots for extreme value analyses. Extremes, 17(2), 289–303. https://doi.org/10.1007/s10687-014-0183-z",
 "Pickands, J. (1975). Statistical inference using extreme order statistics. The Annals of Statistics, 3(1), 119–131. https://doi.org/10.1214/aos/1176343003",
 "Pielke, R. A., Gratz, J., Landsea, C. W., Collins, D., Saunders, M. A., & Musulin, R. (2008). Normalized hurricane damage in the United States: 1900–2005. Natural Hazards Review, 9(1), 29–42. https://doi.org/10.1061/(ASCE)1527-6988(2008)9:1(29)",
 "Robinson, K. A., Saldanha, I. J., & McKoy, N. A. (2011). Development of a framework to identify research gaps from systematic reviews. Journal of Clinical Epidemiology, 64(12), 1325–1330. https://doi.org/10.1016/j.jclinepi.2011.06.009",
 "Rockafellar, R. T., & Uryasev, S. (2002). Conditional value-at-risk for general loss distributions. Journal of Banking & Finance, 26(7), 1443–1471. https://doi.org/10.1016/S0378-4266(02)00271-6",
 "Rootzén, H., & Tajvidi, N. (1997). Extreme value statistics and wind storm losses: A case study. Scandinavian Actuarial Journal, 1997(1), 70–94. https://doi.org/10.1080/03461238.1997.10413979",
 "Scarrott, C., & MacDonald, A. (2012). A review of extreme value threshold estimation and uncertainty quantification. REVSTAT — Statistical Journal, 10(1), 33–60.",
 "Schneider, L. F., Krajina, A., & Krivobokova, T. (2021). Threshold selection in univariate extreme value analysis. Extremes, 24(4), 881–913. https://doi.org/10.1007/s10687-021-00405-7",
 "Smith, A. B., & Katz, R. W. (2013). US billion-dollar weather and climate disasters: Data sources, trends, accuracy and biases. Natural Hazards, 67(2), 387–410. https://doi.org/10.1007/s11069-013-0566-5",
 "Smith, R. L. (1987). Estimating tails of probability distributions. The Annals of Statistics, 15(3), 1174–1207. https://doi.org/10.1214/aos/1176350499",
 "Swiss Re Institute. (2026). Natural catastrophes in 2025: The persistent rise of wildfire and storm risk (sigma No. 1/2026). Swiss Re. https://www.swissre.com/institute/research/sigma-research/sigma-2026-01-natcat-2025-wildfire-storm-risk.html",
 "Wong, T. S. T., Li, W. K., & Yu, P. L. H. (2021). A new test for tail index with application to Danish fire loss data. Journal of Statistical Computation and Simulation, 91(18), 3880–3893. https://doi.org/10.1080/00949655.2021.1954647",
]
for ref in refs:
    p = P(ref, align="l", size=10.5, after=3); p.paragraph_format.left_indent = Cm(1.0); p.paragraph_format.first_line_indent = Cm(-1.0)

name = "EVT_Catastrophe_Losses_Manuscript_v4_BLINDED.docx" if BLIND else "EVT_Catastrophe_Losses_Manuscript_v4.docx"
doc.save(f"{VER}/{name}"); print("saved", name)
if not BLIND:
    main = sum(v for k, v in WC.items() if k in "12345")
    json.dump({"main_text": main, "sections": {**{k: WC.get(k, 0) for k in ("abstract", "1", "2", "3", "4", "5")}}, "method": "Sections 1-5 body paragraphs; excludes abstract, headings, tables, captions, notes, equations, declarations and references"}, open(f"{HERE}/wordcount.json", "w"), indent=2)
    print("wordcount", main, {k: WC.get(k, 0) for k in ("abstract", "1", "2", "3", "4", "5")})
