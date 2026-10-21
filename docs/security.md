# Security and privacy

- Do not commit API keys, credentials, private recordings, or model weights.
- Avoid storing input text or audio unless required and clearly disclosed.
- If hosting publicly, add authentication, rate limits, request-size limits, concurrency limits, timeouts, and resource monitoring before exposing the service to the internet.
- Only use reference audio for voice cloning when you have appropriate authorization.
- Treat uploaded audio and text as untrusted input.
- Local deployments and hosted demos may have different logging and privacy behavior; document the actual configuration.
