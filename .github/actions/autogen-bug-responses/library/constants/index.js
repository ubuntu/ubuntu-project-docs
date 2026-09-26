/** Constant Values. */
export const Constants = new (class {
  /** @readonly Default tools response suffix. */
  suffix = "responses";

  /** @readonly Default tools vendor to be used. */
  vendor = "vendors/ubuntu-qa-tools";

  /** @readonly Default generation output. */
  output = "docs/contributors/bug-triage/bug-responses.md";

  /** @readonly Default tools source to be used. */
  repository = "https://git.launchpad.net/ubuntu-qa-tools";

  /** @readonly Default configuration file to inherit. */
  config = "./.github/actions/autogen-bug-responses/inputs.json";
})();
