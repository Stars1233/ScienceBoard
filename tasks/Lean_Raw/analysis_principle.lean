import Mathlib

-- Analysis: P144, T15
theorem AP_1
  (S : Set ℝ)
  (f f' : ℝ → ℝ)
  (h₁ : ∀ x ∈ S, HasDerivWithinAt f (f' x) S x)
  (h₂ : ∃ M : ℝ, ∀ x ∈ S, |f' x| ≤ M)
  : UniformContinuousOn f S
  := by sorry

-- Analysis: P___
theorem AP_2
  : 0 = 1
  := by sorry
