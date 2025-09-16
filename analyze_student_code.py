#!/usr/bin/env python3
"""Prototype: analyze_student_code.py
- Loads an open-source code model (tokenizer + model via transformers)
- Sends a structured prompt asking for: summary, likely misconceptions, two probing questions, one tiny test case
- Saves JSONL output for downstream evaluation

Notes:
- For local testing use smaller models or run on GPU.
- This prototype uses the text-generation pipeline for clarity; production should use optimized inference (bitsandbytes / accelerate / vllm).
"""

import argparse
import json
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

DEFAULT_MODEL = "bigcode/starcoder"  # change to starcoder2-7b or a local checkpoint

PROMPT_TEMPLATE = """Student code (Python):
---
{code}
---

Task:
1) In 1-2 sentences, summarize what the student's code attempts to do.
2) Identify the single most likely conceptual error or misconception (one sentence).
3) Produce exactly two short probing questions (each 1-2 sentences) that elicit the student's reasoning without giving the solution.
4) Suggest one tiny test case the student should run and what they should *predict* before running it.
5) Output the result as JSON with keys: summary, misconception, probes (list), test_case, predict.
Only output valid JSON.
"""


def run_on_example(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    gen = pipeline("text-generation", model=model, tokenizer=tokenizer, device_map='auto' if hasattr(model, 'is_loaded_in_8bit') else None)

    example_code = """def foo(a):
    s = 0
    for i in range(len(a)):
        s += i
    return s
"""

    prompt = PROMPT_TEMPLATE.format(code=example_code)
    out = gen(prompt, max_new_tokens=256, do_sample=False)[0]["generated_text"]

    # Try to recover JSON from the model output
    json_start = out.find('{')
    json_text = out[json_start:]
    try:
        data = json.loads(json_text)
    except Exception as e:
        # Fallback: attempt to extract lines manually (best-effort)
        data = {'raw': out}
    # save
    out_path = OUTPUT_DIR / "example_result.jsonl"
    with open(out_path, 'w') as fh:
        fh.write(json.dumps({'model': model_name, 'prompt': prompt, 'output': data}, indent=2))
    print(f"Saved example output to {out_path}")


def generate_for_submission(model_name, submission_path):
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    gen = pipeline("text-generation", model=model, tokenizer=tokenizer)

    submissions = []
    with open(submission_path) as fh:
        for line in fh:
            submissions.append(json.loads(line.strip()))

    results = []
    for s in submissions:
        code = s.get('code', '')
        prompt = PROMPT_TEMPLATE.format(code=code)
        out = gen(prompt, max_new_tokens=256, do_sample=False)[0]["generated_text"]
        json_start = out.find('{')
        json_text = out[json_start:]
        try:
            data = json.loads(json_text)
        except:
            data = {'raw': out}
        results.append({'id': s.get('id'), 'model': model_name, 'prompt': prompt, 'output': data})

    # write results
    out_file = OUTPUT_DIR / f"results_{Path(submission_path).stem}.jsonl"
    with open(out_file, 'w') as fh:
        for r in results:
            fh.write(json.dumps(r) + "\n")
    print(f"Saved {len(results)} results to {out_file}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default=DEFAULT_MODEL, help='HuggingFace model id to use')
    parser.add_argument('--example', action='store_true', help='Run example and exit')
    parser.add_argument('--submissions', type=str, help='Path to JSONL file with student submissions (one JSON per line: {"id":..., "code":...})')
    args = parser.parse_args()

    if args.example:
        run_on_example(args.model)
    elif args.submissions:
        generate_for_submission(args.model, args.submissions)
    else:
        print("Run with --example or provide --submissions path.")
