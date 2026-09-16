# Repository profiles (v0.2.0)

```bash
oss-launch-check . --profile docs --format json
oss-launch-check . --profile library --min-score 80 --fail-on-error
```

| Profile | Package manifest required for points | Validation |
| --- | --- | --- |
| library (default) | Yes | Test files |
| app | Yes | Test files |
| docs | No | Test files or scripts/validate* / scripts/check* |
| dataset | No | Test files or scripts/validate* / scripts/check* |
| template | No | Test files or scripts/validate* / scripts/check* |

Excluded checks are removed from both the score and denominator. Reports name the
profile; compare scores only under the same profile. Security, license and community
checks remain active in every profile. Profiles evaluate repository structure; they
do not prove that a dataset has lawful provenance or that an application is secure.

Pair with agent-repo-kit:

```bash
agent-repo-kit create useful-links --template awesome-list
oss-launch-check useful-links --profile docs
```
