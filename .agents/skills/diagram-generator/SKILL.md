---
name: Diagram Generator Skill
description: Instructions for programmatically generating high-fidelity architecture diagrams using Diagrams-as-Code to minimize LLM token usage and prevent image gibberish.
---

# Diagram Generator Skill

When instructed to update or generate an architecture diagram (e.g., during the `publish-showcase.md` workflow), you must **NEVER** use an AI image generator (like DALL-E or Imagen). Instead, you must use **Diagrams-as-Code** to generate pixel-perfect PNGs.

## Supported Tools
The Base Agentic Environment supports two industry-standard tools. Choose the right tool based on the diagram's requirements:

### 1. Python `diagrams` (mingrammer)
**Best for:** Cloud architecture, specific technology nodes (AWS, GCP, Python, Databases), and SRE visual flow.
- **Dependency:** Ensure `diagrams` is in `requirements.txt`.
- **Execution:** Create a script (e.g., `docs/generate_architecture.py`), define the nodes, and run it via `python <script>.py`. Ensure `graph_attr` and `cluster_attr` enforce Dark Mode (`bgcolor="#0D1117"`).
- **Note:** Graphviz must be installed on the system path.

### 2. D2 (Declarative Diagramming)
**Best for:** Fast sketch-style diagrams, generic software flowcharts, UML replacements, and abstract component logic.
- **Dependency:** D2 binary is pre-installed via winget.
- **Execution:** Create a `.d2` text file (e.g., `docs/architecture.d2`) with D2 syntax (`A -> B: request`).
- **Render:** Run `d2 docs/architecture.d2 docs/assets/architecture_diagram.png --theme=200 --sketch` (Theme 200 is mandatory for dark mode).

## Workflow Execution
1. Read the `README.md` to understand the conceptual relationships.
2. Select the appropriate tool.
3. Generate the code (Python or D2).
4. Run the code to output the base `docs/assets/architecture_diagram.png`.
5. **STRICT RULE:** NEVER run the output image through an AI Image Generator (like DALL-E) to apply a "stylistic pass". AI image generators inevitably corrupt the text, creating gibberish. You must rely 100% on the native output of the Python or D2 script to guarantee precision.
6. Check `git status` and commit the new diagram.
