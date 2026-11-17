# Bug responses generator

Runs every **Monday at 12:00 UTC** (and on demand via `workflow_dispatch`) to regenerate the current [`bug-responses.md`](docs/contributors/bug-triage/bug-responses.md) page.

## How it works

Generation occurs from two core inputs:

- [`inputs.json`](.github/actions/autogen-bug-responses/inputs.json) — The defining inputs for our bug-responses (eg: metadata).
- [`ubuntu-qa-tools`](https://code.launchpad.net/~ubuntu-bugcontrol/ubuntu-qa-tools/+git/ubuntu-qa-tools) — The upstream repository containing the `responses` directory of scripts.

When dispatched, this action will clone the upstream repository and execute each of the desired input `targets` that describe the metadata and accompanying response script to use to auto-generate documented responses.

### Adding targets

To add new targets, append a value to the `targets` array of the `inputs.json` file. A target can have the following properties:

```typescript
// Describes either a block of text of lines of text (array).
type Text = string | string[];

// All properties for a target are optional (and if omitted will output nothing).
interface Target {
  //  CORE FIELDS  //

  // Relative path for a `ubuntu-qa-tools/responses` script.
  script?: string;

  // Additional arguments to pass to the above script value (sometimes needed).
  args?: string[];

  // The generated response from the `script`. Can be overriden manually!
  reply?: Text;

  //  META FIELDS  //

  // A grouped title value assigned with `##` markdown annotation.
  header?: Text;

  // A labeled title value assigned with `###` markdown annotation.
  label?: Text;

  // A description added under a label from above.
  describe?: Text;
}
```

## Other configuration

The `inputs.json` file can be further configured for the following properties:

- `output` — Directory to output the generated document.
- `repository` — The `ubuntu-qa-tools` repository url to clone.
- `vendor` — Directory to place the cloned repository.
- `suffix` — Relative directory for expected response scripts.

> **Note:** These should not normally be touched unless the upstream repository has any breaking changes.

## Key considerations

The generation of `bug-responses.md` requires some important considerations:

1. Upstream currently keeps common responses inside scripts that are not easily parsable (inside `.sh` or `.py` files).
2. It will be prone to breakage as targets may not always map nicely to a response. Coincidentally when initially designing this, half of the bug-responses at the time were missing from the upstream source.
3. This is a _mostly_ simple solution that still requires a lot of heavy lifting from the `inputs.json` configuration of `targets`.
