import json

def inspect_markdown():
    notebook_path = "c:\\Users\\tsuma.thomas\\Documents\\Sunculture\\notebooks\\01_data_understanding.ipynb"
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    print("Notebook cells total:", len(nb['cells']))
    
    markdown_cells = [c for c in nb['cells'] if c['cell_type'] == 'markdown']
    print("Markdown cells count:", len(markdown_cells))
    
    print("\n--- Markdown Cells Content ---")
    for idx, cell in enumerate(markdown_cells):
        source = "".join(cell['source'])
        # Print first few lines or if it contains interesting text
        if len(source.strip()) > 0:
            print(f"\n[Cell {idx}]:")
            print(source[:500])
            if len(source) > 500:
                print("...")

if __name__ == "__main__":
    inspect_markdown()
