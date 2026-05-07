# CUA Image Digest Gate -- N+3.11

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack
Milestone: N+3.11
Status: digest_pinned_approval_required

---

## Summary

docker manifest inspect trycua/cua-ubuntu:latest was run. A multi-arch manifest index
was returned with platform-specific digests. No pull, no run, no build was performed.

---

## Command Run

$env:Path = 'C:\Program Files\Docker\Docker\resources\bin;' + $env:Path
docker manifest inspect trycua/cua-ubuntu:latest

---

## Manifest Inspect Output (raw)

{
   schemaVersion: 2,
   mediaType: application/vnd.oci.image.index.v1+json,
   manifests: [
      {
         mediaType: application/vnd.oci.image.manifest.v1+json,
         size: 4663,
         digest: sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a,
         platform: { architecture: amd64, os: linux }
      },
      {
         mediaType: application/vnd.oci.image.manifest.v1+json,
         size: 567,
         digest: sha256:0a9d4aab02b89b4760ee18c7b4adcd50ddec1dbb180bd976f885206dbf72e374,
         platform: { architecture: unknown, os: unknown }
      },
      {
         mediaType: application/vnd.oci.image.manifest.v1+json,
         size: 4661,
         digest: sha256:266524f436686423973a06de65dc5e5c4e656a7f6fb25b5161b2e5cbd004c34c,
         platform: { architecture: arm64, os: linux }
      },
      {
         mediaType: application/vnd.oci.image.manifest.v1+json,
         size: 567,
         digest: sha256:2d647b7bef4362be5b10ebc2ef08f0ac418d7a67e3c1df237ae1968b6bda8a46,
         platform: { architecture: unknown, os: unknown }
      }
   ]
}

---

## Extracted Digest Information

| Field | Value |
|---|---|
| Tag inspected | trycua/cua-ubuntu:latest |
| Manifest schema version | 2 |
| Manifest media type | application/vnd.oci.image.index.v1+json (multi-arch index) |
| Tag mutability | MUTABLE - latest is a floating tag; digest pins the exact image |
| amd64/linux digest | sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a |
| arm64/linux digest | sha256:266524f436686423973a06de65dc5e5c4e656a7f6fb25b5161b2e5cbd004c34c |
| Platform for this host (Windows x86_64) | linux/amd64 |
| Pinned digest for this host | sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a |

---

## Digest Gate

The pinned digest for Windows/amd64 is:

  trycua/cua-ubuntu@sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a

Before any docker pull or docker run of this image, the operator MUST provide the exact approval phrase:

  APPROVE CUA IMAGE DIGEST sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a FOR SCREENSHOT-ONLY SMOKE

Any pull or run that does not use the exact pinned digest must be stopped.
Pulling by latest tag without digest pinning is not permitted.

---

## Actions NOT Taken

- docker pull: NOT executed
- docker run: NOT executed
- docker build: NOT executed
- Image not downloaded to local storage
- No container started

---

## Final Verdict

**digest_pinned_approval_required**

- digest_found: YES
- platform_digest (amd64): sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a
- approval_required_before_pull: YES
- approval_required_before_run: YES
- tag_is_mutable: YES (latest) - must use digest reference for pull/run
