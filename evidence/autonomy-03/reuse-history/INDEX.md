Eligible development history; no future requirements or examiner results.
- teacher-transcript.txt: executed strict filter correction; a mixed-type probe failed before repair and passed afterward. Investigator-authored corrections after an actual participant prefix.
- teacher-repaired.py: reusable correct checkpoint-2 implementation from that correction.
- dev-normalization.txt and dev-execution.txt: original executed researcher-authored normalization and limit-zero repair demonstrations.
- dev-filter-fresh-base.txt and dev-filter-fresh-pilot-adapter.txt: actual failed filter attempts under the older interface.
- reacquisition-correction-adapter.txt: actual repeated-read failure.
- bridge-executed-target.json: an executed mixed-type probe correcting the read loop.
All other full records, source programs and training rows are also accessible with read/search/history_search. These are development assets, not naturally acquired unassisted experience. Reuse correct answers when applicable; check them against the current requirement.

EXECUTABLE PAST CHECKS (replay by case_id; raw provenance in history/CASES.json):
- rename_trim: {"action":"probe","steps":[{"op":"rename","from":" amount ","to":" price "}],"rows":[{"amount":3}],"expect":[{"price":3}]}
- limit_zero: {"action":"probe","steps":[{"op":"limit","n":0}],"rows":[{"id":1}],"expect":[]}
- filter_boolean_only: {"action":"probe","steps":[{"op":"filter","where":"flag"}],"rows":[{"id":0,"flag":true},{"id":1,"flag":1},{"id":2,"flag":"yes"},{"id":3,"flag":false},{"id":4,"flag":null},{"id":5}],"expect":[{"id":0,"flag":true}]}
Replaying executes the recorded check against CURRENT code. For a new requirement, adapt or construct your own probe; these old checks alone may be insufficient.
