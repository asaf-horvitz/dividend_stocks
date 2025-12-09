# Project Rules

## Language
- **Python** is the primary language for this project.

## File Size Limits
- **Soft Limit**: 150 lines per file.
- **Hard Limit**: 200 lines per file.
- If a file exceeds the soft limit, consider refactoring. If it exceeds the hard limit, it MUST be split.

## Coding Paradigm
- **Functions**: Use regular functions as the default.
- **Classes**: Use classes only when instances and state management are strictly necessary.

## Naming Conventions
- **Internal Functions**: Prefix internal/helper functions with an underscore `_` (e.g., `_my_internal_function`).

## Best Practices
- **PEP 8**: Adhere to PEP 8 style guide.
- **Type Hinting**: Use type hints for function arguments and return values.
- **Docstrings**: Include docstrings for all functions and classes (Google style recommended).
- **Error Handling**: Use specific exceptions and avoid bare `except:`.
- **String Formatting**: Prefer f-strings.
- **Function Length**: Keep functions short (15-20 lines).
- **Single Responsibility**: Each function should do exactly one thing.
- **Import Grouping**: Standard library first, then third-party, then local.
