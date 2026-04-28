# CUA Image Digest Re-Check -- N+3.12

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.12
Status: digest_verified_unchanged / approval_still_required

---

## Summary

docker manifest inspect trycua/cua-ubuntu:latest run in N+3.12.
The linux/amd64 digest MATCHES the previously pinned value from N+3.11.
No change. No pull. No run.

---

## Command Run

powershell -NoProfile -Command "& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' manifest inspect trycua/cua-ubuntu:latest"

---

## Manifest Inspect Output (N+3.12)

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
      }
   ]
}

---

## Digest Comparison

| Field | N+3.11 (pinned) | N+3.12 (re-checked) | Match? |
|---|---|---|---|
| linux/amd64 digest | sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a | sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a | YES |

---

## Digest Gate Status

- Tag: trycua/cua-ubuntu:latest
- Pinned digest (linux/amd64): sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a
- Digest changed since N+3.11: NO
- Pull/run still requires image digest approval phrase
- Blocker doc: NOT REQUIRED (digest unchanged)

---

## Actions NOT Taken

- docker pull: NOT executed
- docker run: NOT executed
- docker build: NOT executed
- No container started
