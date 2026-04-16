---
session: 2026-04-16T00:00:00
status: partial
---
## Done
- Pulled origin/main (fast-forward to 0443ae0; restored flashcards.db to remote version)
- Created sprint-2 branch from main
- Rewrote README.md with correct project path, run instructions, DB schema, sprint status, team roster
- Closed GitHub issues #14 (US-4.1), #15 (US-4.2), #16 (US-4.3) — code was already complete in Sprint 1
- Moved issues #14, #15, #16 to Done on GitHub Projects board
- Created Project/ToDo.md with full Sprint 2 task breakdown and priority order

## Decisions
- README rewritten from scratch: old version had wrong path (flashcard_app/ vs src/625_GROUP_PROJECT/) and missing stats files
- US-4 issues closed without code change: routes were fully implemented in Sprint 1 (deck_controller.py)
- progress.md created this session (did not previously exist)

## Blockers
- none

## Next
- Task 3: Wire stats_overview.html and stats_deck.html with real data (US-7.2, US-7.3)
- Task 4: Add streak logic to stats_model.py and display in stats_overview.html (US-7.4)
- Task 5: Image upload — migrate flashcards table, add upload route, update card_form.html (US-5.4, US-5.5)

---
session: 2026-04-16T00:01:00
status: partial
---
## Done
- Reverted stats_overview.html, stats_deck.html, base.html to stubs — those issues (#29-32) are assigned to Sailor1976 (Frits), not eyeclept
- Confirmed GitHub assignees: eyeclept's Sprint 2 issues are #60, #42, #48, #49
- Updated ToDo.md to reflect only eyeclept-assigned tasks

## Decisions
- Stats template work committed in 01fbff0 was Frits' scope — reverted; Frits will own that work
- Board changes from earlier session were also reverted per user instruction; board will not be modified without explicit permission

## Blockers
- none

## Next
- #60: Hide answers before starting a study session
- #49: Restrict edit and delete to deck owner
- #48: Share deck directly with another user by username
- #42: Generate shareable link for a public deck

---
session: 2026-04-16T00:02:00
status: partial
---
## Done
- #60: Answers hidden by default on deck_view.html card list using visibility:hidden
- Show/Hide Answers toggle button added to section header
- GithubRef.md updated with sprint-2 branch, session rules (assignees, board, scope, issue interpretation)
- Committed as a8d1f61 on sprint-2

## Decisions
- Used visibility:hidden (not display:none) to preserve column layout while hiding text
- user-select:none on hidden answers prevents text selection revealing content
- Toggle is per-page (resets on navigate) — no persistence needed for this scope

## Blockers
- none

## Next
- #49: Restrict edit and delete to deck owner
- #48: Share deck directly with another user by username
- #42: Generate shareable link for a public deck

---
session: 2026-04-16T00:03:00
status: partial
---
## Done
- #49: is_owner flag computed in view_deck route and passed to deck_view.html
- Add Card, Edit Deck, card edit/delete buttons gated behind {% if is_owner %}
- Backend already enforced ownership via get_deck_by_id; this closes the UI gap for future public deck viewing
- Committed as 4aaaebf on sprint-2

## Decisions
- Toggle answers button left ungated — non-owners viewing a shared/public deck should still be able to reveal answers to study
- No new model function needed; is_owner derived from deck['user_id'] == session['user_id']

## Blockers
- none

## Next
- #48: Share deck directly with another user by username (requires new deck_shares table)
- #42: Generate shareable link for a public deck (requires public route without login_required)
