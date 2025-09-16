# Evaluating Open Source Models for Student Competence Analysis

## Two-paragraph Research Plan

**Paragraph 1 — Approach to identifying & evaluating models**  
I will identify candidate open-source models by (1) prioritizing models explicitly trained or fine-tuned on source code, (2) preferring permissive licenses and active community support, and (3) selecting models available at multiple sizes so I can trade off latency vs performance. For each candidate (example candidates: StarCoder / StarCoder2 and Code Llama) I’ll run rapid sanity tests on held-out Python tasks (HumanEval-style samples and simple student submissions) to validate basic code understanding, then narrow to 1–2 models for deeper testing. I will prioritize models that support instruction-following and can produce structured outputs (e.g., JSON) so we can automatically parse their diagnoses and prompts.

**Paragraph 2 — How I would test / validate applicability to high-level competence analysis**  
For the chosen model I will build a three-stage pipeline: (A) static analysis + unit tests to capture syntax/behavioural correctness, (B) the model for *explain-and-probe* outputs (generate conceptual observations and follow-up prompts), and (C) an evaluation layer (automated + human). I will validate usefulness by (1) using labeled student-code datasets (IntroClass / CodeSearchNet / HumanEval as anchors) to measure detection precision of common bug classes, (2) running human rater studies where graders score generated prompts on whether they *elicit reasoning* without giving the solution, and (3) small AB tests with learners to measure whether prompts increase conceptual explanations or next-attempt success.

---

## Reasoning (Required)

### What makes a model suitable for high-level competence analysis?
1. **Code understanding & explanation ability** — trained on code + natural language so it can describe intent, patterns, and likely misconceptions.  
2. **Instruction following / structured output** — must reliably follow prompts that ask it to identify concepts, explain reasoning, and produce probing questions.  
3. **Context capacity & multi-step reasoning** — to inspect code, tests, and prior student attempts together.  
4. **Practical constraints** — license, inference cost, and deployability (local vs cloud) to protect student data and control costs.

### How to test whether a model generates meaningful prompts
1. **Dataset & ground truth:** create or adapt labeled student submissions with tagged misconceptions. Use public anchors (IntroClass, CodeSearchNet, HumanEval) and add instructor labels.  
2. **Automated checks:** verify generated prompts do not contain direct solutions and that suggested micro-tests would expose the bug.  
3. **Human-eval rubric (1–5):** Elicitation, Non-spoiling, Targeting, Actionability. Collect ratings from multiple graders and report mean + agreement scores.  
4. **Learner AB test:** compare model-generated prompts to baseline hints; measure improvement in next-attempt correctness and self-reported clarity.

### Trade-offs: accuracy, interpretability & cost
- Larger models = higher accuracy but higher inference cost and latency.  
- Hybrid approach (static analysis + model) improves interpretability and reduces hallucination risk.  
- On-prem/local inference increases ops cost but improves privacy.

### Chosen model (example evaluation)
**StarCoder / StarCoder2 (BigCode)** — chosen because it’s explicitly trained on source code, available in multiple sizes, and has active community support. Strengths: good code understanding baseline, multiple sizes for prototyping. Limitations: not pedagogy-tuned (needs instruction tuning on educator data), can hallucinate explanations, and requires curated prompts and evaluation.

---

## Quick environment & setup

```bash
# create env
python -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Files included
- `analyze_student_code.py` — prototype script to run model analysis and generate prompts.
- `requirements.txt` — Python packages required.
- `rubric.md` — human evaluation rubric for generated prompts.
- `dataset_schema.json` — example JSON schema for storing student submissions and annotations.
- `README.md` — this file (you are reading it).
- `.gitignore` — recommended ignores.

---

## How to run the prototype (local)
1. Clone the repo and create a Python virtualenv as above.
2. Edit `MODEL` variable in `analyze_student_code.py` to choose a model (e.g., `bigcode/starcoder` or `bigcode/starcoder2-7b`).
3. Run a quick local test:
```bash
python analyze_student_code.py --example
```
This will run the prototype prompt on a short sample, produce JSON output and save results to `outputs/`.

---

## Evaluation checklist (to include in submission)
- [ ] Collect 200–500 student Python submissions (mix of correct/incorrect).  
- [ ] Annotate ~100 with instructor-labeled misconceptions.  
- [ ] Run model to generate explanations + prompts; store outputs in JSONL.  
- [ ] Human-rate 100 model outputs using the rubric.  
- [ ] Produce a results summary (mean scores, Cohen’s kappa, precision/recall on bug detection).  
- [ ] If feasible, run a small AB pilot with learners.

---

## Submission & sharing
1. Push the repo to GitHub (public).  
2. Include this README and the `rubric.md`, `dataset_schema.json`, `analyze_student_code.py`.  
3. Email the GitHub link to `pythonsupport@fossee.in` with subject `Screening Task 3 Submission - <Your Name>` and a short message summarizing your work.

Good luck — this README is formatted to drop directly into your repository as the core submission document.
