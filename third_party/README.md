# Third-Party References

Third-party repositories must not be copied into `src/`.

If a repository is cloned for reference, place it under this directory:

```text
third_party/<project-name>
```

This directory is ignored by Git except for this README. Record every reference in `docs/THIRD_PARTY.md` with:

- repository URL
- commit hash
- license
- reason for reference
- which parts may be borrowed conceptually
- whether it is a direct dependency

Phase 1 checked-out references:

- `LAMBDA`
- `data-formulator`
- `DeepAnalyze`
- `python-sdk`

These directories are intentionally ignored by the main repository. Use them as local references first when designing or implementing similar features.
