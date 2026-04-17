# Lessons

## mypy configuration

mypy is a static type checker for Python. It reads type annotations and catches type errors
before runtime — things like assigning to the wrong attribute name in `__init__`, passing the
wrong type to a function, or accessing an attribute that doesn't exist.

It is configured in `pyproject.toml` under `[tool.mypy]`:

```toml
[tool.mypy]
strict = true
files = ["src"]
```

- `strict = true` enables the full set of checks (no implicit `Any`, no untyped functions, etc.)
- `files = ["src"]` limits checking to source code only, excluding tests and config files

Run it with:

```bash
uv run mypy src
```

`--strict` mode will be noisy on a fresh codebase — work through the errors progressively.
It catches entire classes of bugs (e.g. attribute name typos in `__init__`) that pytest cannot,
because pytest only finds errors at runtime when the bad line is actually executed.
