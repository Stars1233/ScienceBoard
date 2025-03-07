import Mathlib

open ZFSet

-- Set Theory: P100, T4
def ST_1
  (X : ZFSet)
  : ((IsTransitive X) ↔ (X ⊆ powerset X)) ∧ ((IsTransitive X) ↔ ((⋃₀ X : ZFSet) ⊆ X))
  := by sorry


open Ordinal Cardinal

-- Set Theory: P126, T11
def ST_2
  (α : Ordinal)
  (p₁ : IsLimit α)
  (p₂ : α < ord ℵ₁)
  : cof α = ℵ
  := by sorry

open Ordinal Cardinal

-- Set Theory: P117, T33
def ℷ (κ : Cardinal) : Cardinal := κ ^ cof (ord κ)
def ST_3
  (p : 𝔠 > ℵ_ (ord ℵ₁))
  : (ℷ (ℵ_ ω) = 2 ^ ℵ₀) ∧ (ℷ (ℵ_ <| ω_ 1) = 2 ^ ℵ₁)
  := by sorry
