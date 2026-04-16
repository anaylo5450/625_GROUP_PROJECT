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
