# Prerequisite fork patches — NOT INDEPENDENTLY APPROVED

These four predecessor source diffs bridge the pinned upstream
d0bdbe11a9624435b6dca3968389bd59c6a559a2 to fork base
5e55510dbeb869bacfcd843f975632dc739519af.

Content safety was checked before writing: no private absolute paths,
credential-shaped keys or authenticated URLs. Two account fields are explicitly
inert privacy-test markers; one authorization header interpolates a runtime
variable. No credential values were printed. See manifest.json.

This permits packaging for an independently checked public DRAFT recipe only.
The four patches have NOT received independent behavioral/source approval here.
Existing repair approvals do not extend to them. No merge/install/build/test or
service action was performed. MIT applies; retain ../LICENSE.upstream.
Use ../FULL-APPLY.md for the eight-patch sequence and verification commands.
