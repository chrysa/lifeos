<!-- GENERATED from standards/STANDARDS.chrysa.md by scripts/gen_agent_views.py — do not edit.
Canonical source of truth is the canon; edit there, then run `make gen-agent-views` to regenerate every view.
-->
# Cross-cutting stack

> Detail for the slim core in `CLAUDE.md`. **Generated** from `standards/STANDARDS.chrysa.md` — do not edit here; edit the canon and regenerate.

## Cross-cutting stack (settled ADRs — do not relitigate)

This canon stays **product-agnostic**: it mandates functional categories (a reverse proxy, an
error-tracking service, a local model runtime, a semantic-version tool…), never a named vendor.
The concrete products and versions the ecosystem has actually settled on — the answer to "which
tool implements each category" — live in the annexe
[`STACK.chrysa.md`](https://github.com/chrysa/shared-standards/blob/main/standards/annexes/STACK.chrysa.md).
That record deliberately names products; where it and this canon disagree, **this file wins**.
