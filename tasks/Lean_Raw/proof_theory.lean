import Mathlib

-- Proof Theory: P186, T1.9
theorem PT_1 {R : Sort u → Sort u → Prop} (h₁ : ∀ x, ∀ y, R x y → R y x) (h₂ : ∀ x, ∀ y, ∀ z, R x y ∧ R y z →  R x z) (h₃ : ∀ x, ∃ y, R x y) : ∀ x, R x x := by sorry
  -- intro x
  -- cases (h₃ x) with
  -- | intro y hxy =>
  --   have hyx := h₁ x y hxy
  --   exact h₂ x y x ⟨hxy, hyx⟩

-- Recursive Theory: P52, T18
theorem PT_2 : ack x (y + 1) < ack (x + 1) y := by sorry
