# Browser extension — `/browser-extension-builder` transcript

> **Status: PLACEHOLDER.** Fill in real run.

## Steps

1. Architecture decision: MV3 service worker + content script + popup.
2. `chrome.storage.local` for tracker DB.
3. CSP-safe injection.
4. Self-test: load unpacked, hit 5 sites, confirm trackers detected.
5. Security review pass.

## Output

- `outputs/<slug>/extension/` — unpacked extension folder.
- `outputs/<slug>/extension/SECURITY.md` — threat model.

## Honest debrief

- [TBD]
