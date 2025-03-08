import Mathlib

-- Abstract Algebra: P39, T7
theorem AA_1
  [Group G]
  [IsCyclic G]
  (N : Subgroup G)
  [Pow (G ⧸ N) ℤ]
  : IsCyclic (G ⧸ N)
  := by sorry

-- Abstract Algebra: P77, T8
theorem AA_2
  [Ring R]
  (N : Ideal R)
  [DivisionRing (R ⧸ N)]
  (a : R)
  : (∃ t : N, t = a * a) → (∃ t' : N, t' = a)
  := by sorry

-- Abstract Algebra: P110, T4
theorem AA_3
  {K E F : Set α}
  [Field K]
  [Field E]
  [Field F]
  [Algebra F E]
  [Algebra F K]
  (h₁ : F ⊆ E) (h₂ : E ⊆ K)
  (h₃ : Normal F K)
  : Nonempty (Algebra E K) ∧ ([Algebra E K] → (Normal E K))
  := by sorry
