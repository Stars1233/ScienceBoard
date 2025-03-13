import Mathlib

open Cardinal MeasureTheory

-- Measure Theory: P27, 12
theorem MT_1 (𝒞 : Set (Set Ω)) (h : #𝒞 = ℵ₀) : #(generateSetAlgebra 𝒞) = ℵ₀ := by sorry

open MeasureTheory ENNReal Filter Topology

-- Measure Theory: P86, T5
theorem MT_2 [MeasurableSpace Ω] (μ_ : ℕ → Measure Ω) (f : Set Ω → ℝ≥0∞) (h₁ : ∀ n : ℕ, ∀ A : Set Ω, (μ_ n).measureOf A ≤ (μ_ (n + 1)).measureOf A) (h₂ : ∀ A : Set Ω, Tendsto (fun n => (μ_ n).measureOf A) atTop (𝓝 (f A))) : ∃ μ : Measure Ω, μ.measureOf = f := by sorry

open Set MeasureTheory Filter

-- Real Analysis: P66, T17
theorem MT_3 {a b : ℝ} {μ : Measure <| Icc a b} (f_ : ℕ → Icc a b → ℝ) (f : Icc a b → ℝ) (g : ℝ → ℝ) (h₁ : TendstoInMeasure μ f_ atTop f) (h₂ : ∃ M : ℝ, ∀ x : Icc a b, |f x| < M) (h₃ : ContinuousOn g univ) : TendstoInMeasure μ (fun n => g ∘ (f_ n)) atTop (g ∘ f)
  := by sorry

open MeasureTheory ProbabilityTheory Filter Topology

-- Probability Theory: P92, T48
theorem MT_4 [MeasureSpace Ω] [IsProbabilityMeasure (ℙ : Measure Ω)] (X : Ω → ℝ) {p : ℕ} {X : Ω → ℝ} (h₁ : p > 0) (h₂ : Integrable X) (h₃ : ∃ M : ℝ, 𝔼[fun ω => |X ω| ^ p] = M) : Tendsto (fun (x : ℝ) => (x ^ p) * (ℙ {ω : Ω | |X ω| > x}).toReal) atTop (𝓝 0) := by sorry
