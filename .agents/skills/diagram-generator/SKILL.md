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

### The Strict AI Styling Pass (Aesthetics)
Because raw programmatic diagrams often lack visual flair, you MUST apply a stylistic pass using the `generate_image` tool if the diagram is meant for recruiter-facing or showcase assets. However, AI image generators inherently struggle with spelling. You must force the AI to preserve text.
1. Ensure the base code script is set to a solid dark mode background (`bgcolor="#0D1117"`). Do not use transparent backgrounds.
2. Run the code to output the base PNG.
3. Pass the base PNG path directly into the `generate_image` tool via the `ImagePaths` parameter.
4. Prompt the AI: *"Use the provided diagram as a strict structural base. Redraw it exactly node-for-node. The aesthetic MUST be a highly professional business dashboard and product showcase: add sleek borders, soft drop shadows, and a clean, high-end enterprise layout with glassmorphism and subtle glowing neon blue/purple accents. The layout must remain identical to the base image. CRITICAL INSTRUCTION: You MUST preserve the exact spelling of all text inside the nodes. Do not alter or hallucinate a single character of text. Include a distinct watermark reading exactly 'github.com/hitanshuac' in the bottom corner."*
5. Overwrite the original diagram with this new, stylized masterpiece.
6. Check `git status` and commit the new diagram.
