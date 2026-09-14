import os

DUMPER_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../dumper.txt"))

def generate_namespace_index(file_path=DUMPER_FILE_PATH) -> str:
    """
    Reads, increments, and returns a numeric string to be used as namespace.
    Ensures dumper.txt always has a valid integer.
    """
    try:
        # Create file if it doesn't exist
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("1")
            return "1"

        # Read and parse integer
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        try:
            current_value = int(content)
        except ValueError:
            raise ValueError("dumper.txt does not contain a valid integer.")

        # Increment and write back
        new_value = current_value + 1
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(new_value))

        return str(new_value)

    except Exception as e:
        print(f"[ERROR] Failed to read/write dumper.txt: {e}")
        raise
