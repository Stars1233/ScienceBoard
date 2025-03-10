import Mathlib

-- Analysis: P54, T13
theorem AP_1
  (A : ℝ)
  (f : ℝ → ℝ)
  (h₁ : A > 0)
  (h₂ : Tendsto f atBot (𝓝 A))
  : ∃ X : ℝ, X > 0 ∧ (∀ x < -X, A < 2 * f x ∧ 2 * f x < 3 * A)
  := by sorry

-- Analysis: P144, T15
theorem AP_2
  (S : Set ℝ)
  (f f' : ℝ → ℝ)
  (h₁ : ∀ x ∈ S, HasDerivWithinAt f (f' x) S x)
  (h₂ : ∃ M : ℝ, ∀ x ∈ S, |f' x| ≤ M)
  : UniformContinuousOn f S
  := by sorry

open Set

-- Analysis: P214, T5
theorem AP_3
  {a b : ℝ}
  (f : ℝ → ℝ)
  (h₁ : ContinuousOn f (Icc a b))
  (h₂ : (∫ x in a..b, (f x) ^ 2) = 0)
  : ∀ x ∈ Icc a b, f x = 0
  := by sorry
