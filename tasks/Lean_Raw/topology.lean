import Mathlib

open TopologicalSpace

-- Topology: P63, T12
theorem TP_1
  [TopologicalSpace X]
  [TopologicalSpace Y]
  (h₁ : X ≃ₜ Y)
  (h₂ : MetrizableSpace X)
  : MetrizableSpace Y
  := by sorry

-- Topology: P76, T2
theorem TP_2
  [TopologicalSpace X]
  (A B : Set X)
  (h : (derivedSet A) ⊆ B ∧ B ⊆ A)
  : IsClosed B
  := by sorry

-- Topology: P129, T13
theorem TP_3
  [TopologicalSpace X]
  [TopologicalSpace Y]
  (f : X → Y)
  (Z : Set X)
  (h₁ : Continuous f)
  (h₂ : IsConnected Z)
  : IsConnected {y : Y | ∃ z ∈ Z, f z = y}
  := by sorry

-- Topology: P170, T9
theorem TP_4
  [𝒯₁ : TopologicalSpace X]
  [𝒯₂ : TopologicalSpace X]
  (h : ∀ x : Set X, 𝒯₁.IsOpen x → 𝒯₂.IsOpen x)
  : (@T0Space X 𝒯₁ → @T0Space X 𝒯₂) ∧ (@T1Space X 𝒯₁ → @T1Space X 𝒯₂)
  := by sorry

-- Topology: P209, T2
theorem TP_5
  [TopologicalSpace X]
  [RegularSpace X]
  (A Y : Set X)
  (h₁ : IsCompact A)
  (h₂ : A ⊆ Y ∧ Y ⊆ Aᶜ)
  : IsCompact Y
  := by sorry
