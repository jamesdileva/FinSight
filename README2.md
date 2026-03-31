## ⚠️ Common Pitfalls (and Fixes)

### Misconception: “This is real-time”

✔ Reality:

> Uses **polling**, not real-time streaming

---

### Re-rendering entire UI repeatedly

✔ Fix:

* Conditional rendering (`children.length` check)
* Prevents flicker and performance issues

---

### Too much vertical stacking

✔ Fix:

* Grid layout
* Side-by-side charts
* Reduced scrolling

---

### Jittery UI animations

✔ Fix:

* Removed border animations
* Used transform + box-shadow transitions

---
