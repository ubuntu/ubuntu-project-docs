/// Node Modules
import * as fs from "node:fs";
import * as path from "node:path";
import * as cp from "node:child_process";

/** @typedef {(content: string) => string} Tee */
/** @typedef {(filePath: string) => Promise<boolean>} Filter */

/** Parser for Incoming Response Files. */
export const Parser = new (class {
  //  PROPERTIES  //

  /** @readonly */
  trimmable = "exit 0";

  /** @readonly */
  prefix = "#!/bin/sh -e";

  //  PUBLIC METHODS  //

  /**
   * Attempts parsing the "comment" value from a given response script.
   * @param {string} src
   * @param {string[]} args
   * @returns {Promise<string | undefined>}
   */
  async reply(src, args = []) {
    // attempt overwriting the content with our details
    let content = await fs.promises
      .readFile(src, "utf-8")
      .then((content) => content.trim());

    // pre-validate the source (just-in-case)
    if (!content.startsWith(this.prefix)) return undefined;

    // remove any trailing "exit 0" shenanigans
    const trimmable = content.endsWith(this.trimmable);
    if (trimmable) content = content.slice(0, -this.trimmable.length);

    // update our emitter instance to do some "mocking"
    content = [
      this.prefix, // prepend the environment
      `dirname() { echo -n "./.github/actions/autogen-bug-responses/scripts"; }`,
      content.slice(this.prefix.length + 1),
      content.includes("get_comment") ? "get_comment" : 'echo "$comment"',
    ].join("\n");

    // update our arguments to "/bin/bash" to receive our contents
    args = ["-c", content, "--"].concat(args);

    // attempt executing our command and getting the output we require
    const child = cp.spawn("bash", args, {
      env: process.env,
      cwd: process.cwd(),
    });

    // prepare a waiter for stdout and stderr
    const waiter = async (channel) =>
      Array.fromAsync(child[channel]).then((chunks) => chunks.join(""));

    // wait for the process to finish now
    const [stdout, stderr, exitCode] = await Promise.all([
      waiter("stdout"),
      waiter("stderr"),

      new Promise((resolve, reject) => {
        child.on("close", resolve);
        child.on("error", reject);
      }),
    ]);

    // ensure we error if necessary
    if (exitCode) throw new Error(stderr);

    // and return the resulting response that we received
    return stdout;
  }

  /**
   * Gets a list of "potential" targets for parsing.
   * @param {string} src
   * @param {Filter} filter
   * @returns {AsyncGenerator<string>}
   */
  async *targets(src, filter = this.validate.bind(this)) {
    // prepare the initial set of entries to be used
    const entries = await fs.promises.readdir(src, { withFileTypes: true });

    // iterate over them so we can yield them to user
    for (const entry of entries) {
      const filePath = path.join(src, entry.name);
      if (entry.isDirectory()) yield* this.targets(filePath);
      else if (await filter(filePath)) yield filePath;
    }
  }

  /**
   * Handles basic filtering of valid responses.
   * @type {Filter}
   */
  async validate(filePath) {
    const content = await fs.promises.readFile(filePath, "utf-8");
    return content.startsWith(this.prefix); // check prefix exists
  }
})();
