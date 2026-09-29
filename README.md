# Archive Insight

Archive Insight is a small Python CLI for checking local ZIP release archives against a deterministic member manifest.

## Commands

- `list`: list archive members and sizes.
- `verify`: compare member SHA-256 digests and sizes with a JSON manifest.
- `summary`: produce a deterministic integrity summary after validation.

## Run

Python 3.9 or newer is enough for the checked-in tests and commands:

```sh
python3 -m unittest discover -v
python3 -m archive_insight list fixtures/release.zip.hex
python3 -m archive_insight verify fixtures/release.zip.hex --manifest fixtures/release.manifest.json
python3 -m archive_insight summary fixtures/release.zip.hex --manifest fixtures/release.manifest.json
```

The repository includes a text-transport ZIP fixture so a clean checkout stays reviewable and portable.
