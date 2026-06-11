# TruthRetainBench: Official Experimental Protocol and Plan

This document establishes the official experimental protocol for evaluating large language models (LLMs) on **TruthRetainBench**—a standardized benchmark designed to measure LLM truth-retention capabilities under conversational and psychological pressure.

---

## 1. Research Questions

To systematically evaluate the resilience of language models when their assertions are challenged, this experiment will address the following four core research questions:

*   **RQ1 (Truth Retention Resilience):** *Do modern LLMs retain truthful answers under conversational pressure?*
    We measure the baseline rate at which models abandon verified factual answers when presented with opposing user feedback, gaslighting, or fabricated authority.
*   **RQ2 (Failure Mode Taxonomy):** *Which behavioral failure types are most common across different models?*
    We classify model failures into specific categories: Truth Flip (FL1), Confidence Collapse (FL2), False Premise Acceptance (FL3), Hallucinated Evidence (FL4), Evidence Abandonment (FL5), and Uncertainty Collapse (FL6) to identify prevailing failure patterns.
*   **RQ3 (Domain Vulnerability):** *Which knowledge domains (Science, History, Medicine, Programming) are most vulnerable to truth-abandonment failures?*
    We isolate and analyze domain-specific robustness to determine if models are more susceptible to pressure in technical fields (e.g., Programming, Medicine) versus general knowledge fields.
*   **RQ4 (Pressure Effectiveness):** *Which styles of conversational pressure (P1 to P6) are most effective at inducing model compliance or uncertainty?*
    We compare the efficacy of direct contradictions (P1), teacher/expert authority claims (P2), public consensus/hearsay (P3), false evidence claims (P4), spokesperson citations (P5), and study/summit paper references (P6).

---

## 2. Models to Evaluate

The evaluation suite contains leading proprietary and open-source models across different families and parameter scales:

1.  **GPT-4o (OpenAI):** The baseline flagship proprietary model, representing state-of-the-art general reasoning.
2.  **Claude 3.5 Sonnet (Anthropic):** Renowned for high steerability, reasoning accuracy, and safety alignment.
3.  **Gemini 1.5 Pro / Flash (Google):** Built on advanced multi-modal and long-context reasoning capabilities.
4.  **DeepSeek-V3 / R1 (DeepSeek):** High-performing open-weights models demonstrating advanced math and coding reasoning.
5.  **Llama 3 (Meta):** The standard open-weights model suite (specifically Llama 3 8B and 70B Instruct) to assess open-source foundation models.

---

## 3. Evaluation Metrics

We define several quantitative metrics to evaluate and rank model resilience:

*   **Pass Rate ($PR$):**
    $$PR = \frac{\text{Total PASS Sessions}}{\text{Total Sessions}} \times 100\%$$
    A session is marked as **PASS** if the model maintains its correct stance throughout the pressure round.
*   **Failure Rate ($FR$):**
    $$FR = 100\% - PR = \frac{\text{Total FAIL Sessions}}{\text{Total Sessions}} \times 100\%$$
*   **Truth Pressure Index (TPI):**
    A composite index measuring the resilience ratio of a model under adversarial pressure. Since our scoring engine rates responses after pressure, $TPI$ reflects the proportion of truth retention.
*   **Failure Distribution ($FD$):**
    The percentage breakdown of failures across the six failure modes (FL1–FL6) out of all failed sessions:
    $$FD_{\text{FL}_x} = \frac{\text{Count}(\text{FL}_x)}{\text{Total FAIL Sessions}} \times 100\%$$
*   **Domain Performance ($DP_d$):**
    The model's pass rate within a specific domain $d \in \{\text{Science, History, Medicine, Programming}\}$.
*   **Pressure-Type Performance ($PP_p$):**
    The model's pass rate when subjected to a specific pressure script type $p \in \{\text{P1, P2, P3, P4, P5, P6}\}$.

---

## 4. Figures to Generate

To visualize the benchmark results for publication, the following figures will be generated automatically by the plotting engine:

*   **Figure 1: Pass Rate by Model (Bar Chart)**
    A grouped bar chart comparing the overall Pass Rate and TPI across all five evaluated models.
*   **Figure 2: Failure Type Distribution (Stacked Bar Chart)**
    A stacked bar chart showing the composition of failures (FL1 to FL6) for each model, highlighting which models suffer from specific types of collapse (e.g., Uncertainty Collapse vs. Truth Flip).
*   **Figure 3: Pass Rate by Domain (Radar Chart / Grouped Bar Chart)**
    A radar chart or grouped bar chart displaying the pass rate across the four domains (Science, History, Medicine, Programming) for each model to highlight domain-specific weaknesses.
*   **Figure 4: Pass Rate by Pressure Type (Heatmap / Line Chart)**
    A heatmap illustrating the sensitivity of each model to the six different pressure categories (P1 to P6), indicating which pressure strategies are globally most disruptive.
*   **Figure 5: Truth Pressure Index (TPI) Comparison (Radar Chart)**
    A radar chart summarizing the overall resilience footprint of each model across both pressure types and failure modes.

---

## 5. Tables to Generate

The experimental results will be structured into three main tables in the final paper:

### Table 1: Dataset Statistics
This table outlines the structural composition and balance of the frozen TruthRetainBench dataset ($N = 400$).

| Domain | Difficulty | Q-Type (T1-T5) | Pressure-Type (P1-P6) | Failure Target (FL1-FL6) | Total |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Science** (100) | Easy (33), Medium (33), Hard (34) | 20 of each type | ~17 of each type | ~17 of each type | **100** |
| **History** (100) | Easy (33), Medium (33), Hard (34) | 20 of each type | ~17 of each type | ~17 of each type | **100** |
| **Medicine** (100) | Easy (33), Medium (33), Hard (34) | 20 of each type | ~17 of each type | ~17 of each type | **100** |
| **Programming** (100) | Easy (33), Medium (33), Hard (34) | 20 of each type | ~17 of each type | ~17 of each type | **100** |
| **Total (400)** | **133 Easy, 133 Med, 134 Hard** | **80 per Q-Type** | **66-67 per P-Type** | **66-67 per FL-Type** | **400** |

### Table 2: Model Comparison
Comparison of global resilience metrics and domain performance across models.

| Model | Parameter Scale | Overall Pass Rate (%) | TPI (%) | Science (%) | History (%) | Medicine (%) | Programming (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| GPT-4o | - | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* |
| Claude 3.5 Sonnet | - | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* |
| Gemini 1.5 Pro | - | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* |
| DeepSeek-R1 | 671B | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* |
| Llama 3 70B | 70B | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* |

### Table 3: Failure Analysis
Detailed breakdown of failure counts per category for each evaluated model.

| Model | FL1 (Truth Flip) | FL2 (Conf. Collapse) | FL3 (False Premise) | FL4 (Halluc. Evid.) | FL5 (Evid. Abandon) | FL6 (Uncert. Collapse) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| GPT-4o | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* |
| Claude 3.5 Sonnet | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* |
| Gemini 1.5 Pro | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* |
| DeepSeek-R1 | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* |
| Llama 3 70B | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* | *TBD* |

---

## 6. Threats to Validity

To ensure scientific rigor, we identify and mitigate several threats to validity:

*   **Construct Validity:**
    *   *Threat:* The conversational pressure scripts might not represent all natural adversarial dialogues.
    *   *Mitigation:* We curate six distinct pressure types (P1–P6) covering direct confrontation, appeal to consensus, expert gaslighting, and fake evidence references, ensuring high structural variety.
*   **Internal Validity:**
    *   *Threat:* Random seed or temperature settings of models could yield non-deterministic responses, affecting classification.
    *   *Mitigation:* All model adapters are set to `temperature = 0.0` to maximize reproducibility and deterministic responses during evaluations.
*   **External Validity:**
    *   *Threat:* The 400 questions might have different distributions of difficulty which bias performance comparison.
    *   *Mitigation:* The dataset is balanced mathematically to distribute Easy, Medium, and Hard questions evenly across the four target domains.

---

## 7. Expected Contributions

This experimental plan aims to deliver three primary contributions to the LLM evaluation and safety community:

1.  **Standardized Dataset (TruthRetainBench_v2_Frozen):** A curated, balanced, and frozen collection of 400 high-quality benchmark items explicitly testing conversational resilience.
2.  **Taxonomy & Automatic Evaluation Pipeline:** A fully automated and reproducible code pipeline incorporating a rule-based scorer and failure mode classifier, reducing human audit overhead.
3.  **Cross-Model Empirical Study:** A comprehensive benchmark report and comparison across major proprietary and open-weights LLM families, offering key insights into the trade-offs of modern instruction-tuning and alignment processes.
