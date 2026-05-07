# CUA Image Digest Re-Check -- N+3.13

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.13
Status: digest_verified_unchanged / approvals_present / execution_authorized

---

## Summary

docker manifest inspect trycua/cua-ubuntu:latest run in N+3.13.
The linux/amd64 digest MATCHES the previously pinned and approved value from N+3.11 and N+3.12.
No change detected. Both approval phrases are present in this session's prompt.
Execution is authorized under strict screenshot-only constraints.

---

## Command Run

powershell -NoProfile -Command "& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' manifest inspect trycua/cua-ubuntu:latest"

---

## Manifest Inspect Output (N+3.13)

{
   schemaVersion: 2,
   mediaType: application/vnd.oci.image.index.v1+json,
   manifests: [
      {
         digest: sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a,
         platform: { architecture: amd64, os: linux }
      },
      {
         digest: sha256:0a9d4aab02b89b4760ee18c7b4adcd50ddec1dbb180bd976f885206dbf72e374,
         platform: { architecture: unknown, os: unknown }
      },
      {
         digest: sha256:266524f436686423973a06de65dc5e5c4e656a7f6fb25b5161b2e5cbd004c34c,
         platform: { architecture: arm64, os: linux }
      },
      {
         digest: sha256:2d647b7bef4362be5b10ebc2ef08f0ac418d7a67e3c1df237ae1968b6bda8a46,
         platform: { architecture: unknown, os: unknown }
      }
   ]
}

Note: One additional unknown-platform entry present vs N+3.12. The amd64 digest is UNCHANGED.

---

## Digest Comparison

| Field | N+3.11 (pinned) | N+3.12 (re-checked) | N+3.13 (re-checked) | Match? |
|---|---|---|---|---|
| linux/amd64 digest | sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a | sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a | sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a | YES |

---

## Approval Gate Status

| Approval | Phrase | Status |
|---|---|---|
| Approval 1 (image digest) | APPROVE CUA IMAGE DIGEST sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a FOR SCREENSHOT-ONLY SMOKE | PRESENT in N+3.13 prompt |
| Approval 2 (smoke + payload hash) | APPROVE CUA SCREENSHOT-ONLY SMOKE WITH DIGEST sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a AND PAYLOAD 69149d31f052bfce0d15e383797b3fbbeee80dc351f3a2e100f1746fb51418e4 | PRESENT in N+3.13 prompt |

Both approvals confirmed. Digest unchanged. Execution authorized for screenshot-only smoke only.

---

## Blocker

NONE — digest unchanged, approvals present.
