# Real TTS and Marketplace release checklist

This checklist separates source/CI validation from real model inference and from Marketplace publication. A green unit-test workflow is not evidence of speech generation.

## Real inference prerequisites

- [ ] Select a cloud GPU host only after measuring the model's VRAM/RAM and disk requirements on the chosen instance; hardware is not yet selected.
- [ ] Deploy the API to a host reachable by GitHub Actions over HTTPS.
- [ ] Configure `RINVO_WARMUP_ON_STARTUP=true` and verify `/ready` returns `200` after model initialization; keep `/health` for process liveness.
- [ ] Restrict inference concurrency initially (Rinvo currently serializes calls within one process); load-test before increasing worker/process counts.
- [ ] Capture warm-request p50/p95 latency, time-to-first-audio (not available for current full-WAV API), real-time factor, throughput, peak VRAM/RAM, and error rate on the exact deployed hardware.
- [ ] Install the upstream Chatterbox-Turbo runtime and verify model/checkpoint terms for the intended use.
- [ ] Configure the service with `RINVO_BACKEND=chatterbox_turbo`.
- [ ] Configure `RINVO_AUDIO_PROMPT_PATH` on the API host to an existing reference recording whose use is authorized. Never upload it to this repository.
- [ ] Confirm the deployed process can download/load model weights and has sufficient RAM/VRAM and disk space.
- [ ] Add repository Actions variable `RINVO_API_URL` (HTTPS base URL, no trailing slash required).
- [ ] If the deployment is protected by a bearer-token validating reverse proxy, add Actions secret `RINVO_API_TOKEN`. Do not use a token unless the proxy actually validates it; the API does not implement authentication by default.
- [ ] Run **Actions → Real TTS smoke test → Run workflow**. The workflow checks health/model endpoints, calls the repository's composite Action against the deployment, parses the returned WAV, rejects too-short/constant payloads, and uploads the WAV as a short-lived artifact.
- [ ] Review the workflow log and download/listen to the artifact. The automated checks validate the WAV container and non-constant samples; listening is still required for perceptual quality and correct voice.

The workflow is deliberately manual and fails with an actionable error when `RINVO_API_URL` is not configured. It does not install Chatterbox or claim that the API's health endpoint proves the model is loaded.

## GitHub Marketplace publication checklist

- [ ] Confirm README clearly states what runs on the workflow runner versus the separately hosted API.
- [ ] Confirm `action.yml` metadata, input/output names, branding, and composite implementation match.
- [ ] Keep unit tests for missing inputs, HTTP errors, invalid WAV responses, and token handling; test with a real deployed endpoint using the manual workflow above.
- [ ] Verify Action metadata and action/client.py from a clean GitHub Actions runner; test timeout and authentication behavior against the real endpoint.
- [ ] Decide and document a support policy, security reporting contact, API availability expectations, and data/logging behavior.
- [ ] Check the license and all model/runtime/asset licenses separately. Rinvo's source license does not grant rights to upstream weights or cloned voices.
- [ ] Create a human-reviewed release with a semantic version (for example `v0.1.0`) and immutable version tag. Update the README examples to a tag that actually exists.
- [ ] After release, create/update major-version tag (for example `v0`) only if you intend to maintain that compatibility promise; document how tags are updated.
- [ ] Review GitHub Marketplace listing requirements and submit the Action for publication from the repository's Releases/Marketplace flow. Publication is a separate GitHub-side approval/listing step and is not implied by a release tag.

## Engineering notes

- Rinvo prepares the Chatterbox-Turbo reference voice once at model initialization instead of passing the prompt path on every generation. This relies on the upstream `prepare_conditionals`/`generate` API and must be validated against the exact installed Chatterbox version in the real-inference smoke test.
- A process-local lock serializes inference until concurrent generation safety and GPU memory behavior are measured. Do not scale with multiple workers blindly; each worker may load another model copy.
- The current HTTP response is a complete WAV. Do not market it as streaming TTS or real-time conversational voice. Streaming requires a backend that emits incremental audio chunks, plus transport/client work; WebRTC and interruption handling are a later voice-agent layer.

## Current evidence status

- Repository code and mocked unit tests: inspectable in GitHub.
- Real Chatterbox-Turbo inference: **not verified until the manual smoke test runs successfully against a configured deployment and the resulting WAV is inspected**.
- GitHub Action against a live model-backed deployment: **not verified until the manual smoke test passes**.
- Marketplace listing: **not published by this checklist change**.

Do not commit model weights, reference recordings, deployment credentials, or generated speech artifacts.
