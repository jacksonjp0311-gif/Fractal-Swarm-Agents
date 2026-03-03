from pathlib import Path

def write_memory(root, text):
    mem = Path(root) / "memory" / "memory.txt"
    mem.parent.mkdir(parents=True, exist_ok=True)
    with open(mem, "a", encoding="utf-8") as f:
        f.write(text + "\n")