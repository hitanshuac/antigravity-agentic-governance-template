import os

def generate_diagram():
    output_path = "docs/assets/auto_architecture.d2"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    diagram_content = """
direction: right
User -> WebUI -> Backend
Backend -> Database
    """
    
    with open(output_path, "w") as f:
        f.write(diagram_content)
    
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_diagram()
