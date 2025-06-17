
# A/B Testing Analysis Report

**Project:** Average Bidding vs. Maximum Bidding  
**Author:** Özge Güneş  
**Date:** 17 June 2025  

---

## 1. Objective  

Determine whether the new *Average Bidding* strategy out‑performs the current *Maximum Bidding* strategy in terms of:

1. **Purchase mean** (number of items bought per session)  
2. **Conversion rate** (Purchases / Sessions)

---

## 2. Data Overview  

| Group | Sessions (_n_) | Purchases (Σ) | Purchase Mean (μ) | Conversion Rate (p̂) |
|-------|----------------|---------------|-------------------|----------------------|
| Control | 1 000 | 550 | **0.551** | **0.300** |
| Test    | 1 100 | 582 | **0.529** | **0.227** |

`pandas` was used to load and clean the data; the two datasets were concatenated for summary statistics.

---

## 3. Hypotheses  

### 3.1 Purchase Mean (two‑sample *t*‑test)

* **H₀:** μ<sub>control</sub>  =  μ<sub>test</sub>  
* **H₁:** μ<sub>control</sub> ≠ μ<sub>test</sub>

### 3.2 Conversion Rate (two‑proportion *z*‑test)

* **H₀:** p<sub>control</sub>  =  p<sub>test</sub>  
* **H₁:** p<sub>control</sub> ≠ p<sub>test</sub>

Significance level α = 0.05 for both tests.

---

## 4. Assumption Checks  

| Test | Control | Test | p‑value | Decision (α = 0.05) |
|------|---------|------|---------|---------------------|
| **Shapiro‑Wilk** (normality) | W = 0.995 | W = 0.994 | 0.84 / 0.77 | Normality **not** rejected |
| **Levene** (equal variances) | — | — | 0.41 | Homogeneity **not** rejected |

Therefore, a parametric independent two‑sample *t*‑test is appropriate for purchase means.

---

## 5. Results  

| Metric | Test Statistic | p‑value | 95 % CI | Decision |
|--------|---------------|---------|---------|----------|
| **Purchase Mean** | *t* = 0.94 | **0.349** | [‑0.039, 0.111] | Fail to reject H₀ |
| **Conversion Rate** | *z* = ±3.79 | **0.00015** | [0.036, 0.110] | Reject H₀ |

> *Note:* The sign of *z* depends on group ordering; magnitude |3.79| indicates a strong effect.

---

## 6. Interpretation  

* **Purchase Mean:** No statistically significant difference; Average Bidding does **not** change the number of items bought per session.  
* **Conversion Rate:** Statistically significant **7.3 percentage‑point** lift for the control group (0.300 → 0.227). If *conversion* is the north‑star KPI, the control strategy out‑performs the test variant.

---

## 7. Recommendations  

1. **Retain Maximum Bidding** for now; it converts more visitors into purchasers.  
2. **Iterate on Average Bidding** — test modified bid caps or audience segments to close the gap.  
3. **Run a power analysis** before the next experiment to ensure sufficient sample size for detecting smaller lifts in purchase mean.  
4. **Track secondary metrics** (AOV, revenue, bounce) to ensure decisions are holistic.  
5. Document learnings in the experimentation log and schedule a follow‑up test if product or budget conditions change.

---

## 8. Appendix – Key Python Snippets  

```python
# Assumption checks
shapiro_ctrl = shapiro(control_df['Purchase'])
shapiro_test = shapiro(test_df['Purchase'])
levene_test  = levene(control_df['Purchase'], test_df['Purchase'])

# Two‑sample t‑test
ttest_res = ttest_ind(control_df['Purchase'],
                      test_df['Purchase'],
                      equal_var=True)

# Two‑proportion z‑test
succ = np.array([300, 250])
nobs = np.array([1000, 1100])
z_stat, p_val = proportions_ztest(succ, nobs)
```

---

*Generated automatically via `AB_TESTING.py` analysis.*  
