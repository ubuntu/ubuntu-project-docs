/// Actions Modules
import { Inputs } from "../inputs/index.js";

/** Formats Response Targets. */
export const Renderer = new (class {
  //  PUBLIC METHODS  //

  /**
   * Handles formatting a given target.
   * @param {import("../inputs").Target} target
   * @returns {string[]}
   */
  format(target) {
    // start with a suitable header if given
    const lines = this.textify(target.header, "\n## ");

    // pad the start with a separate line if needed
    if (lines.length && target.label) lines.push("");

    // prepend the label as needed
    lines.push(...this.textify(target.label, "\n### "));

    // bind the description if given one
    lines.push(...this.textify(target.describe, "\n"));

    // stop early if there is no reply available
    if (!target.reply) return lines;

    // bind the reply as necessary now
    return lines.concat([
      "",
      "```{code} none",
      ":class: codeblock-wrap",
      "",
      ...this.textify(target.reply),
      "```",
    ]);
  }

  /**
   * Merges all given targets together.
   * @param {import("../inputs").Target[]} targets
   */
  merge(targets) {
    // prepare the metadata section details to be used
    const header = this.textify(Inputs.config.header).join("\n");
    const footer = this.textify(Inputs.config.footer).join("\n");

    // prepare the baseline content to be emitted
    const content = targets.map((target) => this.format(target).join("\n"));

    // and merge all these items together now
    return [header, content.join("\n\n"), footer].join("\n\n") + "\n";
  }

  /**
   * Converts inputs to a singular text block array.
   * @param {import("../inputs").Text | undefined} text
   * @param {string} prefix
   * @returns {string[]}
   */
  textify(text, prefix = "") {
    // ignore if the given input is invalid
    if (typeof text === "undefined") return [];

    // convert to a series of lines
    const [initial, ...lines] = Array.isArray(text) ? text : [text];

    // ensure the output is suitably valid
    if (typeof initial !== "string") return [];

    // and prepend any given prefix to our items
    return [`${prefix}${initial}`].concat(lines).map((line) => line.trimEnd());
  }
})();
