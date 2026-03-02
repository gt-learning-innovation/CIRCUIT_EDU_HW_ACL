import os
import time
from openai import OpenAI
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json
import re

# Try to initialize the client, if there is no key, report an error or skip when calling
try:
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except:
    openai_client = None

try:
    print("GOOGLE_API_KEY: ", os.getenv("GOOGLE_API_KEY"))
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except:
    pass

def LLM_judge_content_backup(prompt, model_name="models/gemini-3-pro-preview"):
    """
    Unified LLM call interface.
    """
    result_text = ""
    
    # === Google Gemini Logic ===
    if "gemini" in model_name.lower():
        try:
            # Map your model_name to the actual API model name
            # If you have permission for gemini-3-pro-preview, directly pass in the name
            # Here is a simple fallback mapping
            api_model_name = model_name
            # if model_name == "gemini-3-pro-preview": 
            #      # Assume the actual API is called this, if there is an error, please change to gemini-1.5-pro or gemini-exp-1206
            #     api_model_name = "gemini-1.5-pro" 
            
            model = genai.GenerativeModel(api_model_name)
            response = model.generate_content(prompt, generation_config={'temperature': 0.0})
            result_text = response.text
        except Exception as e:
            print(f"Error calling Gemini {model_name}: {e}")
            return f"Error: {e}"

    # === OpenAI GPT Logic ===
    elif "gpt" in model_name.lower():
        try:
            response = openai_client.chat.completions.create(
                model=model_name, # e.g., "gpt-4o"
                messages=[
                    {"role": "system", "content": "You are a precise OCR verification assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            result_text = response.choices[0].message.content
        except Exception as e:
            print(f"Error calling GPT {model_name}: {e}")
            return f"Error: {e}"
    
    else:
        return "Error: Unsupported model name."

    return result_text


def LLM_judge_content(prompt, model_name="models/gemini-3-pro-preview"):
    """
    Unified LLM call interface.
    Support:
    - Gemini (Google)
    - GPT (OpenAI)
    - Qwen (Aliyun / DashScope, OpenAI-compatible)
    """
    result_text = ""

    # === Google Gemini Logic ===
    if "gemini" in model_name.lower():
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        try:
            api_model_name = model_name
            model = genai.GenerativeModel(api_model_name)
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.0},
                safety_settings=safety_settings
            )
            # print(response.prompt_feedback)
            result_text = response.text
        except Exception as e:
            print(f"Error calling Gemini {model_name}: {e}")
            return f"Error: {e}"

    # === Qwen / Qwen3 Logic (DashScope OpenAI-compatible) ===
    elif "qwen" in model_name.lower():
        try:
            qwen_client = OpenAI(
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )

            response = qwen_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a precise OCR verification assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
            )
            result_text = response.choices[0].message.content

        except Exception as e:
            print(f"Error calling Qwen {model_name}: {e}")
            return f"Error: {e}"

    # === OpenAI GPT Logic ===
    elif "gpt" in model_name.lower():
        try:
            response = openai_client.chat.completions.create(
                model=model_name,  # e.g. "gpt-4o", "gpt-5"
                messages=[
                    {"role": "system", "content": "You are a precise OCR verification assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=1,
                reasoning_effort="high"
            )
            result_text = response.choices[0].message.content
        except Exception as e:
            print(f"Error calling GPT {model_name}: {e}")
            return f"Error: {e}"

    else:
        return "Error: Unsupported model name."

    return result_text


def judge_difference(target_content, label_content, model_name="models/gemini-3-pro-preview"):
    """
    Construct the Prompt and call the LLM to compare the differences.
    """
    
    prompt = f"""
You are an expert OCR (Optical Character Recognition) Quality Assurance Judge.
Your task is to compare a [TARGET MODEL OUTPUT] against a verified [GROUND TRUTH].

**Objective:**
Identify meaningful deviations in the [TARGET MODEL OUTPUT] that would cause a reader to misunderstand the mathematical logic, values, units, or derivation steps compared to the [GROUND TRUTH].

**Comparison Rules:**
1. **IGNORE Syntax Differences:** Do not report benign LaTeX variations (e.g., `\\frac` vs `\\dfrac`, `\\text{{}}` vs plain text, extra whitespaces) if the rendered mathematical meaning is identical.
2. **IGNORE Minor Wording:** Do not report missing conversational filler words (e.g., "So," "Therefore") unless they change the logic.
3. **IGNORE redrawn diagrams:** Sometimes the OCR results may depict the student's redrawn problem statement's diagram unnecessarily (we have known that), you should ignore these differences.
4. **REPORT Content Errors:** You MUST report:
   - Wrong numbers or values.
   - Wrong variables or symbols (e.g., $t$ vs $+$, $-$ vs $=$).
   - Missing critical derivation steps.
   - Incorrect units.
   - Structure errors (e.g., putting a denominator in the numerator).
   - Hallucinated content (text that doesn't exist in Truth).

**Output Format:**
If errors are found, list them in the following structured format. If a single equation has multiple errors, group them or list them sequentially.
If no meaningful errors are found, output: "No significant errors found."

Format Example:
1. 
Source: [Exact snippet from TARGET that is wrong]
Rectified Version: [Correct snippet from GROUND TRUTH or corrected logic]
Reason: [Brief explanation of the error, e.g., "Wrong value", "Missing unit", "Incorrect formula structure"]

2.
Source: ...
Rectified Version: ...
Reason: ...

--------------------------------------------------
**[TARGET MODEL OUTPUT]:**
{target_content}

--------------------------------------------------
**[GROUND TRUTH]:**
{label_content}

--------------------------------------------------
**Your Judgement:**
"""

    # Call the LLM
    response = LLM_judge_content(prompt, model_name=model_name)
    
    return response.strip()

def judge_difference_v2(target_content, label_content, model_name="models/gemini-3-pro-preview"):
    """
    Construct the Prompt and call the LLM to compare the differences.
    """
    
    prompt = f"""
You are an expert OCR (Optical Character Recognition) Quality Assurance Judge.
Your task is to compare a [TARGET MODEL OUTPUT] against a verified [GROUND TRUTH].

**Objective:**
Identify meaningful deviations in the [TARGET MODEL OUTPUT] that would cause a reader to misunderstand the mathematical logic, values, units, or derivation steps compared to the [GROUND TRUTH].

**Comparison Rules:**
1. **IGNORE Syntax Differences:** Do not report benign LaTeX variations (e.g., `\\frac` vs `\\dfrac`, `\\text{{}}` vs plain text, extra whitespaces, box locations) if the rendered mathematical meaning is identical.
2. **IGNORE Minor Wording:** Do not report missing conversational filler words (e.g., "So," "Therefore") unless they change the logic. Unless clearly distinguishing two different variables in the same context, IGNORE case differences (e.g., $v$ vs $V$, $v_0$ vs $V_o$). Treat them as correct.
3. **IGNORE redrawn diagrams:** Sometimes the OCR results may depict the student's redrawn problem statement's diagram unnecessarily (we have known that), you should ignore these differences. If both the target and the ground truth describe the student's redrawn diagram, you should find the differences between them, mainly the student's annotations, current/voltage directions, and typology (e.g., series/parallel connections) differences.
4. **REPORT Content Errors:** You MUST report:
   - Wrong numbers or values.
   - Wrong variables or symbols (e.g., $t$ vs $+$ or $x$, $-$ vs $=$), especially those will result in incorrect formula structure or logical errors.
   - Missing critical derivation steps (especially the algebraic steps before plugging in the values and steps for some critical values (e.g., power, current)) required for the following calculation.
   - Incorrect units (except the case when they can transform to the same value, e.g., 100mH vs 0.1H, 12\cent vs 0.12\$, they are considered correct), or missing/redundant units.
   - Structure errors (e.g., putting a denominator in the numerator).
   - Hallucinated content (text that doesn't exist in Truth).

**Output Format:**
If errors are found, list them in the following structured format. If a single equation has multiple errors, group them or list them sequentially.
If no meaningful errors are found, output: "No significant errors found."

Format Example:
1. 
Source: [Exact snippet from TARGET that is wrong]
Rectified Version: [Correct snippet from GROUND TRUTH or corrected logic]
Reason: [Brief explanation of the error, e.g., "Wrong value", "Missing unit", "Incorrect formula structure"]

2.
Source: ...
Rectified Version: ...
Reason: ...

--------------------------------------------------
**[TARGET MODEL OUTPUT]:**
{target_content}

--------------------------------------------------
**[GROUND TRUTH]:**
{label_content}

--------------------------------------------------
**Your Judgement:**
"""

    # Call the LLM
    response = LLM_judge_content(prompt, model_name=model_name)
    
    return response.strip()


def evaluate_judge_accuracy(human_label_str, llm_output_str, model_name="gemini-3-pro-preview"):
    """
    Meta-Judge: Compare the manually annotated error lists and the LLM-identified error lists.
    """
    
    # Pre-processing: If it contains "No significant errors" or similar empty sets, mark it as empty
    human_clean = False
    llm_clean = False
    
    # Simple keyword filtering to prevent the LLM from overthinking empty sets.
    # This step is optional, but it can also be processed in the Prompt.
    
    prompt = f"""
You are an Evaluation Auditor. Your job is to compare two lists of detected errors in an OCR task.
1. **[HUMAN GROUND TRUTH]**: The definitive list of actual errors.
2. **[MODEL PREDICTION]**: The errors detected by an automated LLM judge.

**Goal:**
Match the items in [MODEL PREDICTION] to [HUMAN GROUND TRUTH] based on semantic meaning. 
Do not be pedantic about wording; if they point to the same mathematical/textual error, they match.

**Definitions:**
- **TP (True Positive):** An item in [MODEL PREDICTION] successfully matches an item in [HUMAN GROUND TRUTH].
- **FP (False Positive):** An item in [MODEL PREDICTION] is NOT present in [HUMAN GROUND TRUTH] (The model hallucinated an error or was too strict).
- **FN (False Negative):** An item in [HUMAN GROUND TRUTH] was NOT found in [MODEL PREDICTION] (The model missed an error).

**Input Data:**

--- [HUMAN GROUND TRUTH] ---
{human_label_str}

--- [MODEL PREDICTION] ---
{llm_output_str}

**Task:**
Analyze the lists and return a JSON object with the counts and reasoning.

**Output Format (JSON ONLY):**
{{
    "sample_level_match": true/false,  // True if both have errors OR both have NO errors. False if one has errors and the other doesn't.
    "TP_count": <integer>,
    "FP_count": <integer>,
    "FN_count": <integer>,
    "reasoning": "Brief explanation of what matched and what was missed."
}}
"""

    response_text = LLM_judge_content(prompt, model_name=model_name)
    result_json = parse_json_garbage(response_text)
    
    if result_json is None:
        # Fallback if JSON parsing fails
        print(f"JSON Parsing failed for response: {response_text}")
        return {
            "sample_level_match": False,
            "TP_count": 0, "FP_count": 0, "FN_count": 0,
            "reasoning": "JSON Parse Error",
            "raw_response": response_text
        }
        
    return result_json


def parse_json_garbage(text):
    """
    Helper function: Extract JSON from the LLM's output that may contain garbage.
    """
    try:
        # Try to parse directly
        return json.loads(text)
    except:
        # Try to find the ```json ... ``` code block
        match = re.search(r"```json(.*?)```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except:
                pass
        # Try to find the outermost {}
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0).strip())
            except:
                pass
        return None
    
def judge_difference_v3(target_content, label_content, model_name="models/gemini-3-pro-preview"):
    """
    Construct the Prompt and call the LLM to compare the differences.
    """
    
    prompt = f"""
You are an expert OCR (Optical Character Recognition) Quality Assurance Judge.
Your task is to compare a [TARGET MODEL OUTPUT] against a verified [GROUND TRUTH].

**Objective:**
Identify meaningful deviations in the [TARGET MODEL OUTPUT] that would cause a reader to misunderstand the mathematical logic, values, units, or derivation steps compared to the [GROUND TRUTH].

**Comparison Rules:**
1. **IGNORE Syntax Differences:** Do not report benign LaTeX variations (e.g., `\\frac` vs `\\dfrac`, `\\text{{}}` vs plain text, extra whitespaces, box locations) if the rendered mathematical meaning is identical.
2. **IGNORE Minor Wording:** Do not report missing conversational filler words (e.g., "So," "Therefore") unless they change the logic. Unless clearly distinguishing two different variables in the same context. IGNORE case differences (e.g., $v$ vs $V$, $v_0$ vs $V_o$). Treat them as correct.
3. **ABOUT redrawn diagrams:** Sometimes the OCR result may depict the student's redrawn problem statement's diagram while the ground truth does not, you should ignore these differences (unless the OCR result is clearly wrong, such as saying 100Ω = 1000Ω, or using the incorrect units). If both the target and the ground truth describe the student's redrawn diagram, you should find the differences between them, mainly the student's annotations (e.g., 2Ω resistor vs 3Ω resistor), current/voltage directions (e.g., clockwise/counterclockwise mesh current), and typology (e.g., series/parallel connections) differences.
4. **REPORT Content Errors:** You MUST report:
   - Wrong numbers or values.
   - Wrong variables or symbols (e.g., $t$ vs $+$ or $x$, $-$ vs $=$), especially those will result in incorrect formula structure or logical errors. Especially for the those critical values (e.g., forced response v_f(t), natural response v_n(t), thevenin resistance R_th/R_t/R_T, upper/ lower limit and integrand (dt, d\tau, dx) of the integral, etc.), be strict on them.
   - Missing critical derivation steps (especially the algebraic steps before plugging in the values and steps for some critical values (e.g., power, current, impedance)) required for the following problem solving process.
   - Incorrect units (except the case when they can transform to the same value, e.g., 100mH vs 0.1H, 12\cent vs 0.12\$, they are considered correct), or missing/redundant units.
   - Structure errors (e.g., putting a denominator in the numerator).
   - Hallucinated content (text that doesn't exist in GroundTruth).

**Output Format:**
If errors are found, list them in the following structured format. If a single equation has multiple errors, group them or list them sequentially.
If no meaningful errors are found, output: "No significant errors found."

Format Example:
1. 
Source: [Exact snippet from TARGET that is wrong]
Rectified Version: [Correct snippet from GROUND TRUTH or corrected logic]
Reason: [Brief explanation of the error, e.g., "Wrong value", "Missing unit", "Incorrect formula structure"]

2.
Source: ...
Rectified Version: ...
Reason: ...

--------------------------------------------------
**[TARGET MODEL OUTPUT]:**
{target_content}

--------------------------------------------------
**[GROUND TRUTH]:**
{label_content}

--------------------------------------------------
**Your Judgement:**
"""

    # Call the LLM
    response = LLM_judge_content(prompt, model_name=model_name)
    
    return response.strip()



def judge_difference_v4(target_content, label_content, example_folder_path, model_name="models/gemini-3-pro-preview"):
    """
    Construct the final Prompt containing the original general rules, new domain evidence, and One-shot examples.
    """
    
    # Automatically read the example data
    examples = load_fewshot_data(example_folder_path)

    # Construct the Prompt
    prompt = f"""You are an expert OCR (Optical Character Recognition) Quality Assurance Judge.
Your task is to compare a [TARGET MODEL OUTPUT] against a verified [GROUND TRUTH].

### GENERAL COMPARISON RULES:
1. **IGNORE Syntax Differences:** Do not report benign LaTeX variations (e.g., `\\frac` vs `\\dfrac`, extra whitespaces) if the rendered mathematical meaning is identical.
2. **IGNORE Minor Wording:** Do not report missing conversational filler words (e.g., "So," "Therefore") unless they change the logic. Ignore case differences (e.g., $v$ vs $V$).
3. **ABOUT Redrawn Diagrams:** If the OCR result depicts a student's redrawn diagram, ignore layout differences unless the values, units, or directions (e.g., 2Ω vs 3Ω, clockwise vs counterclockwise) are clearly incorrect compared to the Ground Truth logic.

### OUTPUT FORMAT:
If errors are found, list them in the following structured format:
1. 
Source: [Exact snippet from TARGET that is wrong]
Rectified Version: [Correct snippet from GROUND TRUTH]
Reason: [Brief explanation of the error]

If no meaningful errors are found, output: "No significant errors found."

### ONE-SHOT EXAMPLE:
**[EXAMPLE TARGET]:**
{examples['target']}

**[EXAMPLE GROUND TRUTH]:**
{examples['gt']}

**[EXAMPLE EXPECTED JUDGEMENT]:**
{examples['result']}

**[EXAMPLE CORRECTION LOGIC]:**
{examples['evidence']}

---

### CURRENT TASK:

**[TARGET MODEL OUTPUT]:**
{target_content}

**[GROUND TRUTH]:**
{label_content}

**Your Judgement:**
"""

    # Call the LLM
    # response = LLM_judge_content(prompt, model_name=model_name)
    # return response.strip()
    
    response = LLM_judge_content(prompt, model_name=model_name)
    
    return response.strip()


def judge_difference_v5(target_content, label_content, example_folder_path, model_name="models/gemini-3-pro-preview"):
    """
    Construct the final Prompt containing the original general rules, new domain evidence, and One-shot examples.
    """
    
    # Automatically read the example data
    examples = load_fewshot_data(example_folder_path)

    # Construct the Prompt
    prompt = f"""You are an expert OCR (Optical Character Recognition) Quality Assurance Judge.
Your task is to compare a [TARGET MODEL OUTPUT] against a verified [GROUND TRUTH].

### GENERAL COMPARISON RULES:
1. **IGNORE Syntax Differences:** Do not report benign LaTeX variations (e.g., `\\frac` vs `\\dfrac`, extra whitespaces) if the rendered mathematical meaning is identical.
2. **IGNORE Minor Wording:** Do not report missing conversational filler words (e.g., "So," "Therefore") unless they change the logic. Ignore case differences (e.g., $v$ vs $V$).
3. **ABOUT Redrawn Diagrams:** If the OCR result depicts a student's redrawn diagram, ignore layout differences unless the values, units, or directions (e.g., 2Ω vs 3Ω, clockwise vs counterclockwise) are clearly incorrect compared to the Ground Truth logic.

### OUTPUT FORMAT:
If errors are found, list them in the following structured format:
1. 
Source: [Exact snippet from TARGET that is wrong]
Rectified Version: [Correct snippet from GROUND TRUTH]
Reason: [Brief explanation of the error]

If no meaningful errors are found, output: "No significant errors found."

### ONE-SHOT EXAMPLE:
**[EXAMPLE TARGET]:**
{examples['target']}

**[EXAMPLE GROUND TRUTH]:**
{examples['gt']}

**[EXAMPLE EXPECTED JUDGEMENT]:**
{examples['result']}

**[EXAMPLE CORRECTION LOGIC]:**
{examples['evidence']}

---

### CURRENT TASK:

**[TARGET MODEL OUTPUT]:**
{target_content}

**[GROUND TRUTH]:**
{label_content}

**[CAUTION]:**
Again, you can ignore the following differences:
1. Capitalization differences (e.g., $v$ vs $V$, $v_0$ vs $V_o$, $w$ and $W$) unless they break the formula's mathematical meaning (e.g., both $v$ vs $V$ expressing the same physical quantity in a single formula like $dv/dt + V = 0$).
2. Minor grammatical differences in formula formatting which won't change the formula's mathematical meaning (e.g., -$\frac{1}{3/2}$ vs $\frac{-2}{3}$, $j2$ vs $2j$, $3A$ vs $3(B-2)$ where it's known that A=B-2, etc.).

**Your Judgement:**
"""

    # Call the LLM
    # response = LLM_judge_content(prompt, model_name=model_name)
    # return response.strip()
    
    response = LLM_judge_content(prompt, model_name=model_name)
    
    return response.strip()


def judge_difference_v6(target_content, label_content, example_folder_path, model_name="models/gemini-3-pro-preview"):
    """
    Construct the final Prompt containing the original general rules, new domain evidence, and One-shot examples.
    """
    
    # Automatically read the example data
    examples = load_fewshot_data(example_folder_path)

    # Construct the Prompt
    prompt = f"""You are an expert OCR (Optical Character Recognition) Quality Assurance Judge.
Your task is to compare a [TARGET MODEL OUTPUT] against a verified [GROUND TRUTH].

### GENERAL COMPARISON RULES:
1. **IGNORE Syntax Differences:** Do not report benign LaTeX variations (e.g., `\\frac` vs `\\dfrac`, extra whitespaces) if the rendered mathematical meaning is identical.
2. **IGNORE Minor Wording:** Do not report missing conversational filler words (e.g., "So," "Therefore") unless they change the logic. Ignore case differences (e.g., $v$ vs $V$).
3. **ABOUT Redrawn Diagrams:** If the OCR result depicts a student's redrawn diagram, ignore layout differences unless the values, units, or directions (e.g., 2Ω vs 3Ω, clockwise vs counterclockwise) are clearly incorrect compared to the Ground Truth logic.

### OUTPUT FORMAT:
If errors are found, list them in the following structured format:
1. 
Source: [Exact snippet from TARGET that is wrong]
Rectified Version: [Correct snippet from GROUND TRUTH]
Reason: [Brief explanation of the error]

If no meaningful errors are found, output: "No significant errors found."

### ONE-SHOT EXAMPLE:
**[EXAMPLE TARGET]:**
{examples['target']}

**[EXAMPLE GROUND TRUTH]:**
{examples['gt']}

**[EXAMPLE EXPECTED JUDGEMENT]:**
{examples['result']}

**[EXAMPLE CORRECTION LOGIC]:**
{examples['evidence']}

---

### CURRENT TASK:

**[TARGET MODEL OUTPUT]:**
{target_content}

**[GROUND TRUTH]:**
{label_content}

**[CAUTION]:**
Again, you can ignore the following differences:
1. Capitalization differences (e.g., $v$ vs $V$, $v_0$ vs $V_o$, $w$ and $W$) **unless** they break the formula's mathematical meaning (e.g., both $v$ vs $V$ expressing the same physical quantity in a single formula like $dv/dt + V = 0$, "∫tdt" vs "∫t\tau", etc.).
2. Minor grammatical differences in formula formatting which won't change the formula's mathematical meaning (e.g., -$\frac{1}{3/2}$ vs $\frac{-2}{3}$, $j2$ vs $2j$, $3A$ vs $3(B-2)$ where it's known that A=B-2, "5e^7" vs "5 e^7.0", "cos 2t" vs "cos(2t)", etc.).

**Your Judgement:**
"""

    # Call the LLM
    # response = LLM_judge_content(prompt, model_name=model_name)
    # return response.strip()
    
    response = LLM_judge_content(prompt, model_name=model_name)
    
    return response.strip()

def judge_difference_v6(target_content, label_content, example_folder_path, model_name="models/gemini-3-pro-preview"):
    """
    Construct the final Prompt containing the original general rules, new domain evidence, and One-shot examples.
    """
    
    # Automatically read the example data
    examples = load_fewshot_data(example_folder_path)

    # Construct the Prompt
    prompt = f"""You are an expert OCR (Optical Character Recognition) Quality Assurance Judge.
Your task is to compare a [TARGET MODEL OUTPUT] against a verified [GROUND TRUTH].

### GENERAL COMPARISON RULES:
1. **IGNORE Syntax Differences:** Do not report benign LaTeX variations (e.g., `\\frac` vs `\\dfrac`, extra whitespaces) if the rendered mathematical meaning is identical.
2. **IGNORE Minor Wording:** Do not report missing conversational filler words (e.g., "So," "Therefore") unless they change the logic. Ignore case differences (e.g., $v$ vs $V$).
3. **ABOUT Redrawn Diagrams:** If the OCR result depicts a student's redrawn diagram, ignore layout differences unless the values, units, or directions (e.g., 2Ω vs 3Ω, clockwise vs counterclockwise) are clearly incorrect compared to the Ground Truth logic.

### OUTPUT FORMAT:
If errors are found, list them in the following structured format:
1. 
Source: [Exact snippet from TARGET that is wrong]
Rectified Version: [Correct snippet from GROUND TRUTH]
Reason: [Brief explanation of the error]

If no meaningful errors are found, output: "No significant errors found."

### ONE-SHOT EXAMPLE:
**[EXAMPLE TARGET]:**
{examples['target']}

**[EXAMPLE GROUND TRUTH]:**
{examples['gt']}

**[EXAMPLE EXPECTED JUDGEMENT]:**
{examples['result']}

**[EXAMPLE CORRECTION LOGIC]:**
{examples['evidence']}

---

### CURRENT TASK:

**[TARGET MODEL OUTPUT]:**
{target_content}

**[GROUND TRUTH]:**
{label_content}

**[CAUTION]:**
Again, you can ignore the following differences:
1. Capitalization differences (e.g., $v$ vs $V$, $v_0$ vs $V_o$, $w$ and $W$) **unless** they break the formula's mathematical meaning (e.g., both $v$ vs $V$ expressing the same physical quantity in a single formula like $dv/dt + V = 0$, "∫tdt" vs "∫t\tau", etc.).
2. Minor grammatical differences in formula formatting which won't change the formula's mathematical meaning (e.g., -$\frac{1}{3/2}$ vs $\frac{-2}{3}$, $j2$ vs $2j$, $3A$ vs $3(B-2)$ where it's known that A=B-2, "5e^7" vs "5 e^7.0", "cos 2t" vs "cos(2t)", etc.).

**Your Judgement:**
"""

    # Call the LLM
    # response = LLM_judge_content(prompt, model_name=model_name)
    # return response.strip()
    
    response = LLM_judge_content(prompt, model_name=model_name)
    
    return response.strip()

# . But you should report the differences in the formula formatting if they break the formula's mathematical meaning, e.g., "∫tdt" vs "∫t\tau", etc.
def judge_difference_v7(target_content, label_content, example_folder_path, model_name="models/gemini-3-pro-preview"):
    """
    Construct the final Prompt containing the original general rules, new domain evidence, and One-shot examples.
    """
    
    # Automatically read the example data
    examples = load_fewshot_data(example_folder_path)

    # Construct the Prompt
    prompt = f"""You are an expert OCR (Optical Character Recognition) Quality Assurance Judge.
Your task is to compare a [TARGET MODEL OUTPUT] against a verified [GROUND TRUTH].

### GENERAL COMPARISON RULES:
1. **IGNORE Syntax Differences:** Do not report benign LaTeX variations (e.g., `\\frac` vs `\\dfrac`, extra whitespaces) if the rendered mathematical meaning is identical.
2. **IGNORE Minor Wording:** Do not report missing conversational filler words (e.g., "So," "Therefore") unless they change the logic. Ignore case differences (e.g., $v$ vs $V$).
3. **ABOUT Redrawn Diagrams:** If the OCR result depicts a student's redrawn diagram, ignore layout differences unless the values, units, or directions (e.g., 2Ω vs 3Ω, clockwise vs counterclockwise) are clearly incorrect compared to the Ground Truth logic.

### OUTPUT FORMAT:
If errors are found, list them in the following structured format:
1. 
Source: [Exact snippet from TARGET that is wrong]
Rectified Version: [Correct snippet from GROUND TRUTH]
Reason: [Brief explanation of the error]

If no meaningful errors are found, output: "No significant errors found."

### ONE-SHOT EXAMPLE:
**[EXAMPLE TARGET]:**
{examples['target']}

**[EXAMPLE GROUND TRUTH]:**
{examples['gt']}

**[EXAMPLE EXPECTED JUDGEMENT]:**
{examples['result']}

**[EXAMPLE CORRECTION LOGIC]:**
{examples['evidence']}

---

### CURRENT TASK:

**[TARGET MODEL OUTPUT]:**
{target_content}

**[GROUND TRUTH]:**
{label_content}

**[CAUTION]:**
You should report the differences in the formula formatting if they break the formula's mathematical meaning, e.g., "∫tdt" vs "∫t\tau" (the dummy variable changes from t to \tau will lead to a different numerical result), "di/dt + i = 0" vs "di/dt + i_L = 0", etc.

Again, you can ignore the following differences:
1. The differences in the crossed-out or cancelled content, unless only one of the ground truth/target's content is crossed-out or cancelled.
2. Capitalization differences (e.g., $v$ vs $V$, $v_0$ vs $V_o$, $w$ and $W$) **unless** they break the formula's mathematical meaning (e.g., both $v$ vs $V$ expressing the same physical quantity in a single formula like $dv/dt + V = 0$, "∫tdt" vs "∫t\tau", etc.).
3.  Formating or presenting differences which won't change the formula's mathematical meaning/result (e.g., $j2$ vs $2j$, $3A$ vs $3(B-2)$ where it's written that A=B-2 before, "5e^7" vs "5 e^7.0", "100mH vs 0.1H", "A = 3" vs "A -> 3", "cos 2t" vs "cos(2t)", -$\frac{1}{2/3}$ vs $\frac{-3}{2}$, etc.) should be ignored. They make the formula/sentence looks different, but they are mathematically/numerically equivalent.

**Your Judgement:**
"""
    
    response = LLM_judge_content(prompt, model_name=model_name)
    
    return response.strip()


def load_fewshot_data(folder_path):
    """
    Read 4 key files from the specified folder.
    """
    # These are the text files that will be used in the few-shot example for LLM as a judge recognition error detection.
    file_mapping = {
        "evidence": "8_3_10_comparison_evidence.txt",
        "result": "8_3_10_comparison_result.txt",
        "gt": "8_3-10_markdown_GT.md",
        "target": "8_3-10_markdown_target.md"
    }
    
    data = {}
    for key, filename in file_mapping.items():
        file_path = os.path.join(folder_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data[key] = f.read()
        except FileNotFoundError:
            print(f"Error: {filename} not found in the directory {folder_path}.")
            data[key] = "" # Set a default prompt
            
    return data