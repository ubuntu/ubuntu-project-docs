/// Node Modules
import * as fs from "node:fs";
import * as path from "node:path";
import * as cp from "node:child_process";

/// Action Modules
import { Inputs } from "../inputs/index.js";

/** Repository Version Control. */
export const Control = new (class {
  //  PUBLIC METHODS  //

  /**
   * Handles cloning required repositories.
   * @param url
   * @param dst
   * @param suffix
   */
  async clone(
    url = Inputs.repository,
    dst = Inputs.vendor,
    suffix = Inputs.suffix,
  ) {
    // prepare the resulting source responses
    const responses = path.join(dst, suffix);

    // ignore if the directory already exists
    if (fs.existsSync(responses)) return responses;

    // show the repository that we will be cloning
    console.info(`Cloning Repository: ${url}`);

    // clone the repository in question using "sparse" settings
    await this.git("clone", ["--depth", "1", url, dst]);

    // and resolve the resulting details
    return responses;
  }

  /**
   * Handles executing "git" commands.
   * @param {string} command
   * @param  {string[]} args
   * @param {cp.SpawnOptions} options
   */
  async git(command, args, options = {}) {
    // prepare the command to be spawned
    const child = cp.spawn("git", [command].concat(args), {
      stdio: "inherit",
      ...options,
    });

    // and await for it to be completed
    return new Promise((resolve, reject) => {
      child.on("close", resolve);
      child.on("error", reject);
    });
  }

  /**
   * Handles cleaning up target repositories.
   * @param target
   */
  async cleanup(target = Inputs.vendor) {
    await fs.promises.rm(target, {
      force: true,
      maxRetries: 3,
      recursive: true,
      retryDelay: 300,
    });
  }
})();
