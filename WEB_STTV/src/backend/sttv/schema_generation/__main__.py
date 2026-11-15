"""Explicit developer entry point: python -m sttv.schema_generation."""

from .generate import generate_schemas

if __name__ == "__main__":
    result = generate_schemas()
    print(result)
    raise SystemExit(0 if result["status"] == "success" else 1)
