# ⚡ Locator Resolution – Minimal Instruction Spec

## 🎯 Goal

Implement dynamic locator resolution for Playwright agent.

---

## 🧠 Rule

* DO NOT hardcode locators in generated scripts
* ALWAYS resolve locators at runtime

---

## 🧩 Pipeline

```text
Planner → LocatorResolver → Generator → Executor
```

---

## 📌 Planner Output (Contract)

```json
{"action": "click", "target": "login_button"}
```

---

## 🧱 Locator Resolver

### Interface

```python
resolve(page, target) -> locator
```

---

## 🔌 Strategy Order (MANDATORY)

1. **Repo Strategy**
2. **Snapshot Strategy**
3. **Fallback Strategy**

---

## 🧩 Resolution Logic

```text
if repo has target:
    return repo locator

else if snapshot match:
    return generated locator

else:
    return fallback locator
```

---

## 📂 Structure

```bash
locator/
  engine.py
  strategies/
    repo.py
    snapshot.py
    fallback.py
```

---

## ⚙️ Generator Rule

### ALWAYS generate:

```python
locator = resolve_locator(page, "target")
locator.click()
```

### NEVER generate:

```python
page.get_by_role(...)
```

---

## 🧠 Snapshot Strategy

### Steps:

1. `snapshot = page.accessibility.snapshot()`
2. flatten tree
3. match:

   * target ↔ name
   * target ↔ role
4. build locator:

```python
get_by_role(role, name=name)
```

---

## 🔁 Optional Learning

```python
if snapshot_success:
    save_to_repo(target, locator)
```

---

## ⚠️ Constraints

* Repo = primary source
* Snapshot = fallback only
* No locator logic in planner
* No snapshot during generation

---

## 🧠 Principles

* Late binding (resolve at runtime)
* Separation:

  * Planner → WHAT
  * Resolver → WHERE
  * Generator → HOW
* Pluggable strategies

---

## 🚀 Result

* Reusable scripts
* Self-healing capability
* No regeneration needed on UI change

---
