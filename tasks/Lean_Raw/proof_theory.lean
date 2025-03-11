import Mathlib

-- Proof Theory: P___
theorem PT_0
  {x y z : Sort u}
  {R : Sort u → Sort u → Prop}
  (h₁ : ∀ x, ∀ y, R x y → R y x)
  (h₂ : ∀ x, ∀ y, ∀ z, R x y ∧ R y z → R x z)
  (h₃ : ∀ x, ∃ y, R x y)
  : ∀ x, R x x
  := by sorry
