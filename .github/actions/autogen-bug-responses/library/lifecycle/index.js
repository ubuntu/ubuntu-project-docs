/// Node Modules
import * as os from "node:os";
import * as fs from "node:fs";
import * as path from "node:path";

/// Action Modules
import { Inputs } from "../inputs/index.js";
import { Control } from "../control/index.js";
import { Parser } from "../parser/index.js";
import { Renderer } from "../renderer/index.js";

/** Lifecyle Manager for Action. */
export const Lifecycle = new (class {
  //  PUBLIC METHODS  //

  /** Handles executing the action. */
  async execute() {
    // start by retrieving the repository to be generated from
    const responses = await Control.clone();

    // and attempt parsing our responses from incoming targets
    await Promise.all(
      Inputs.targets.map(async (target) => {
        if (typeof target.script === "undefined") return;
        const absolute = path.resolve(responses, target.script);
        target.reply ??= await Parser.reply(absolute, target.args);
      }),
    );

    // finally format each of the required sections
    const document = Renderer.merge(Inputs.targets);

    // write the generated result to a suitable location
    await fs.promises.mkdir(path.dirname(Inputs.output), { recursive: true });
    await fs.promises.writeFile(Inputs.output, document); // can safely write
  }

  /** Handles cleanup of the action. */
  async cleanup() {
    // remove the vendored directory as not useful anymore
    await Control.cleanup();
  }
})();
