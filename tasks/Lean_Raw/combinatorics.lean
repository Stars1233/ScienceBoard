import Mathlib

-- Number Theory: P47, T5
theorem CB_1
  {a p : ℕ}
  (h₁ : Nat.Prime p)
  (h₂ : Odd a)
  (h₃ : IsCoprime a p)
  : (a ^ (p - 1) + (p - 1) ^ a) ≡ 0 [ZMOD p]
  := by sorry

-- Graph Theory: P107, T33
theorem CB_2
  {n e : ℕ}
  {G : SimpleGraph V}
  [Fintype V]
  [Fintype G.edgeSet]
  [DecidableEq V]
  (h₁ : n = Fintype.card V ∧ e = Fintype.card G.edgeSet)
  (h₂ : ∀ v₁ : V, ∀ v₂ : V, ∃ w : G.Walk v₁ v₂, w.IsHamiltonian)
  : n ≥ 4 → 2 * e ≥ 3 * n + 1
  := by sorry

-- Computability Theory: P94, Lemma 3.1.3
theorem CB_3
  [Primcodable α]
  [Primcodable β]
  [Primcodable γ]
  [Primcodable δ]
  {p : α → Prop}
  {q : β → Prop}
  {r : γ → Prop}
  {s : δ → Prop}
  (h₁ : ManyOneEquiv p r)
  (h₂ : ManyOneEquiv q s)
  : ManyOneEquiv (Sum.elim p q) (Sum.elim r s)
  := by sorry
