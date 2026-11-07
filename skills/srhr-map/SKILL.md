---
name: srhr-map
description: SRHR interactive map skill, under construction (phase b of 5). Not usable yet; refresh and publish modes arrive in later phases. Call by name only.
disable-model-invocation: true
---

# SRHR interactive map skill (under construction)

This folder holds the source of the SRHR map skill during its pilot. It is not usable yet.

What is here so far (phase b):

- `shared/srhr_data_contract.v1.json`: a byte-identical copy of the data contract shared with the SRHR Intelligence Tool. Never edit it here; it is copied from the canonical file and checked byte for byte.
- `contracts/`: one data contract per internal source file a colleague drops in. They name columns and rules only.
- `scripts/`: the checks that read those contracts.

**What this folder must never hold.** This repository is public. No register rows, organisation or country names, fund names, amounts, or local file paths. The register and the drop-in files live in the organisation's own storage.

If invoked now, say that the skill is under construction and stop.
