# Conflict Resolution Report - 1
**Date:** February 18, 2026
**Project:** DA5402-MLOps-JAN26
**Pull Request:** #4 (Feature/speech synth worker)

## 1. Conflict Overview
**Conflict Status:** Resolved
**File Involved:** `app.py`
**Branches:**
* **Source Branch:** `feature/speech_synth_worker` (Incoming changes)
* **Target Branch:** `main` (Base branch)

## 2. Nature of the Conflict
Upon attempting to merge Pull Request #4, GitHub detected a merge conflict in `app.py`.

* **The Issue:** The incoming changes from the `speech-synth` feature branch were inserted in the middle of the existing `image-generate` endpoint on the `main` branch. This resulted in the logic for the Image Generation endpoint being split into two disconnected fragments, with the new Speech Synthesis code sandwiched between them.
* **Visual Evidence:** The conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) clearly showed the new `speech_endpoint` interrupting the flow of the existing code.

![Conflict](imgs/Conflict_1.png)
![Conflict View - Code Split 1](imgs/Conflict_2.png)
![Conflict View - Code Split 2](imgs/Conflict_3.png)

## 3. Resolution Strategy
**Method:** Manual Code Restructuring via GitHub Web Editor

**Steps Taken:**
1.  **Identification:** Located the two separated fragments of the `image-generate` logic and the inserted `speech-synth` block.
2.  **Consolidation:** Moved the detached latter half of the `image-generate` logic up to rejoin it with its definition, restoring the function's integrity.
3.  **Reordering:** Placed the entire `speech_endpoint` function block *below* the fully completed `image-generate` endpoint to ensure clean function separation.
4.  **Cleanup:** Removed all Git conflict markers to validate the Python syntax.

**Verification:**
The restructuring was successful, and GitHub confirmed that the branches could be merged automatically.

![Resolution](imgs/Resolution_1.png)
![Resolution Success - Ready to Merge](imgs/Resolution_2.png)

## 4. Final Outcome
* The `app.py` file is now syntactically correct with both endpoints functioning independently.
* The Pull Request is clear of conflicts and ready for merging.

# Conflict Resolution Report - 2

**Date:** February 18, 2026
**Project:** DA5402-MLOps-JAN26
**Pull Request:** #5 (chore/update-readme)
**Resolved By:** Adithya Sai Lenka (Developer B)

## 1. The Conflict Scenario
A merge conflict occurred in `README.md` when attempting to merge the `chore/update-readme` branch into `main`.

* **Developer A (Main Branch):** Had updated `README.md` with project metadata, team details, and documentation for the **Translation** and **Image Generation** endpoints.
* **Developer B (Feature Branch):** Had independently updated `README.md` to add installation steps and testing guides for the **NER** and **Speech Synthesis** endpoints.

Since both developers modified the same documentation sections (specifically the "Endpoints" table and "Setup" instructions) simultaneously, Git could not automatically determine which version to keep.

## 2. The Resolution
To resolve this, I manually edited the conflicting file to combine the contributions from both developers into a single, unified document.

* **Header & Team Info:** Kept the detailed team information and repository links from Developer A's version.
* **Endpoints Table:** Merged the rows to include all four endpoints: `/translate`, `/image-generate`, `/ner`, and `/speech`.
* **Setup Instructions:** Combined the API key setup (for Developer A's services) with the local model download instructions (for Developer B's NER service).
* **Testing Guide:** Appended the specific `curl` commands and testing steps for the NER and Speech endpoints below the existing documentation for Translation and Image Generation.

## 3. Outcome
The final `README.md` now provides a complete project overview, listing all dependencies and providing testing instructions for the full suite of 4 AI microservices. The code was successfully committed and the feature branch was merged.