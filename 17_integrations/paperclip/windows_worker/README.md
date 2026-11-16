# Paperclip reviewed Windows repair and bounded pairing recipe

Origin: https://github.com/paperclipai/paperclip.git. MIT notice retained.
This first-party patch recipe includes no vendor repository history, installed dependencies, credentials or runtime data.

Full-series has nine patches: four prerequisites, the four unchanged Windows worker/declaration repairs, and the C-P3-1 browser-await correction. See full-manifest.json and FULL-APPLY.md for every preimage/postimage tree/hash. The subset series/manifest.json retains the original four-repair provenance on5e55510 to e04 and is not the full public-upstream recipe.

Prerequisites1,2,4 are source-approved. The original prerequisite3 await was RED; append the correction, never treat original e04 as fixed. Exact accepted correction b32d26e53cb77b7d28f7f95bd95bfe35117eaa5f replaces an unbounded asynchronous opener await with operation cancellation/expiry, observes late resolve/reject and detaches its listener. It does not reverse an external opener that has no cancellation interface. No permissions or request bounds are relaxed.

Independent correction checks passed in separate selections: lifecycle14, pending-browser9, owner regressions13, privacy2; unchanged original reproducer copy now settles before callback release. Original failed receipt is retained.

Full public-upstream recipe reproduced treedf78771e6c9631a8d7edf6e9d0992570a6f3b432. With accepted narrow-save d2d7647, combined tree47f0df456dace03cb9918435f5f4424969b0e3a9 passed the independent affected cancellation/route/form checks recorded in the linked operation manifest. Full service/declaration dependency-closure build passed. Existing Node22.16, Vitest3.2.4 and installed pnpm10.33.0 were reused; source still declares pnpm9.15.4. A fixture-only userconfig disabled automatic manager provisioning and forced offline mode/Git Bash; no global config/install/download. The initial offline automatic-manager-resolution failure remains historical.

Source and combined synthetic acceptance are distinct from installed/native worker, authenticated board or real save acceptance. Preserve original corrected launcher13857ef and existing company/DB state. PR27 remains a source-only snapshot with omitted helper/runtime dependencies, not a portable installer. Hermes alone owns separately authorized build adoption, service lease/restart and rollback. No host action occurred.
