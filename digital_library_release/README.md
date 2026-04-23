# EDU-CIRCUIT-HW Data Package README

This README is prepared for the Georgia Tech Digital Library upload of the EDU-CIRCUIT-HW data package.

## Suggested Item Abstract

EDU-CIRCUIT-HW is an anonymized dataset for studying multimodal handwritten recognition and downstream grading on authentic university-level STEM coursework. The release contains student handwritten circuit-analysis solutions collected from the Spring 2025 offering of ECE 2040 at the Georgia Institute of Technology, together with model-generated transcripts, grading metadata, rubric files, split metadata, and expert-rectified reference transcripts for a subset of samples with identified recognition errors. The package is designed to support research on how visual recognition errors from multimodal large language models propagate into downstream educational tasks such as rubric-based grading and error analysis.

## Suggested Item Description

This upload contains the data assets associated with the EDU-CIRCUIT-HW project, a benchmark of authentic university-level handwritten circuit-analysis solutions from Georgia Tech's Spring 2025 ECE 2040 course. The package is organized around four top-level directories:

1. `Screenshot_output_anon/`
   Contains the anonymized original student handwritten solution images, organized by homework, student, and question. This directory also includes split metadata (`obsetf_involved_data.csv`, `test_involved_data.csv`, `debug_involved_data.csv`), question-level rubric files in JSON format, grading reports (`obset.xlsx`, `valset1.csv`), and auxiliary manual annotation material used during dataset construction.

2. `Observationset_Final/`
   Contains multimodal model recognition outputs for the observation subset. Subdirectories are grouped by model version (including Gemini 2.5 Pro, Gemini 3, GPT-5.1, Claude Sonnet 4.5, and Qwen3-VL variants). Each sample folder stores recognized Markdown transcripts (`*_markdown.md`) and the paired source image pages used for transcription (`*_source.png`).

3. `Valset/`
   Contains model recognition outputs for the held-out evaluation subset, organized in the same per-sample structure as `Observationset_Final/`. In the current release, this directory includes outputs for Gemini 2.5 Pro, Gemini 3, and GPT-5.1.

4. `Rectified_recognized_markdown_done_Anon/`
   Contains expert-rectified Gemini-2.5-Pro transcripts for the subset of observation-set samples that required manual correction after recognition error review. These files serve as the released reference set for recognition-error analysis and human-in-the-loop evaluation. Each corrected sample includes a rectified Markdown transcript and its paired source image page.

The split metadata enumerate 513 observation-set records and 828 held-out evaluation records across 62 unique question IDs. Problem statements are not distributed in this package because they are tied to copyrighted course materials. The dataset collection and release were prepared for research use under the EDU-CIRCUIT-HW project.

## Directory Overview

### 1. `Screenshot_output_anon/`

Primary contents:

- Original anonymized student handwritten solution images in `.png` format
- Split metadata in `.csv` format
- Grading reports in `.xlsx` / `.csv`
- Rubric definitions in `.json`
- Auxiliary manual annotation / working files used during dataset preparation

Organization:

```text
Screenshot_output_anon/
|-- Homework1/
|   |-- student_2/
|   |   |-- 1.5-2.png
|   |   |-- 1.5-3.png
|   |   |-- 3.6-1_(1).png
|   |   `-- 3.6-1_(2).png
|   `-- ...
|-- manually_checked_TA_label/
|-- rubric_outputs/
|-- set_splitting/
`-- Manual_drawn_recognition_error_onenote_Anon/
```

Important files:

- `set_splitting/obsetf_involved_data.csv`: observation-set split metadata
- `set_splitting/test_involved_data.csv`: held-out evaluation split metadata
- `manually_checked_TA_label/obset.xlsx`: observation-set grading report
- `manually_checked_TA_label/valset1.csv`: held-out evaluation grading report
- `rubric_outputs/P*.json`: question-level rubric definitions

### 2. `Observationset_Final/`

Primary contents:

- Model-recognized transcripts for the observation subset
- Paired source-image copies used by each model pipeline

Top-level model folders observed in the release:

- `v6_claude_sonnet4p5`
- `v6_Gemini_2p5`
- `v6_Gemini_3`
- `v6_gpt5p1`
- `v6_qwen3vl8bthinking`
- `v6_qwen3vlplus`
- `v6_qwen3vlplus_backup`

Representative per-sample layout:

```text
Observationset_Final/
`-- v6_Gemini_2p5/
    `-- Homework_collected_database_trial_Homework1_student_2/
        `-- models/
            `-- gemini-2.5-pro/
                `-- Compare/
                    |-- 1_5-2_markdown.md
                    |-- 1_5-2_source.png
                    |-- 3_6-1_1_markdown.md
                    `-- 3_6-1_1_source.png
```

Notes:

- File names use underscores in place of dots within question IDs, for example `1_5-2_markdown.md` corresponds to question `P1.5-2`.
- Multi-page student solutions may appear as indexed files such as `3_6-1_1` and `3_6-1_2`.

### 3. `Valset/`

Primary contents:

- Model-recognized transcripts for the held-out evaluation subset
- Paired source-image copies used by each model pipeline

Top-level model folders observed in the release:

- `v6_Gemini_2p5`
- `v6_Gemini_3`
- `v6_gpt5p1`

Representative per-sample layout:

```text
Valset/
`-- v6_Gemini_2p5/
    `-- Homework_collected_database_trial_Homework1_student_10/
        `-- models/
            `-- gemini-2.5-pro/
                `-- Compare/
                    |-- 1_5-2_markdown.md
                    |-- 1_5-2_source.png
                    |-- 3_6-1_markdown.md
                    `-- 3_6-1_source.png
```

### 4. `Rectified_recognized_markdown_done_Anon/`

Primary contents:

- Expert-rectified Gemini-2.5-Pro transcripts for a subset of observation-set samples
- Paired source images for the corrected samples

Representative layout:

```text
Rectified_recognized_markdown_done_Anon/
`-- Final_4_LLM_judge/
    `-- Homework_collected_database_trial_Homework1_student_21/
        `-- models/
            `-- gemini-2.5-pro/
                `-- Compare/
                    |-- 1_5-2_markdown.md
                    |-- 1_5-2_source.png
                    |-- 3_2-6_markdown.md
                    `-- 3_2-6_source.png
```

Notes:

- This directory is not a full duplicate of the observation set.
- It contains only the samples that were manually rectified during expert review and are intended to serve as released reference transcripts for recognition-error analysis.

## File Naming Notes

- Homework folders follow `Homework1`, `Homework2`, etc.
- Student folders follow `student_2`, `student_31`, etc.
- Question IDs in image folders generally use dots and parentheses, for example `3.6-1_(1).png`.
- Question IDs in recognized transcript folders use underscores, for example `3_6-1_1_markdown.md`.

## Important Usage Notes

- The dataset contains anonymized student work only; no problem statements are included.
- Question statements are tied to copyrighted course materials and therefore are omitted from the release.
- The package is intended for research on handwritten STEM solution recognition, recognition-error analysis, and downstream rubric-based grading.
- When comparing model outputs to expert references, users should treat the rectified transcripts as the released reference subset rather than assume every observation-set sample has a manual correction file.

## Contact / Citation

Project: EDU-CIRCUIT-HW  
Paper: "Evaluating Multimodal Large Language Models on Real-World University-Level STEM Student Handwritten Solutions"  
Venue: ACL Findings 2026
