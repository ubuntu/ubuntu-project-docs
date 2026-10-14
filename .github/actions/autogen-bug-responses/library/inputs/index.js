/// Node Modules
import * as fs from "node:fs";
import * as path from "node:path";

/// Action Modules
import { Constants } from "../constants/index.js";

/** @exports @typedef {string | string[]} Text */

/**
 * @exports
 * @typedef {Object} Target
 * @property {string | undefined} label
 * @property {Text | undefined} header
 * @property {Text | undefined} describe
 * @property {Text | undefined} reply
 * @property {string | undefined} script
 * @property {string[] | undefined} args
 */

/**
 * @exports
 * @typedef {Object} Schema
 * @property {Target[]} targets
 * @property {Text | undefined} header
 * @property {Text | undefined} footer
 * @property {string | undefined} vendor
 * @property {string | undefined} output
 * @property {string | undefined} suffix
 * @property {string | undefined} repository
 */

/** Helper Class for Parsing Inputs. */
export const Inputs = new (class {
  //  PROPERTIES  //

  /** @readonly @type {Schema} */
  config;

  /** @readonly @type {string} */
  vendor;

  /** @readonly @type {string} */
  suffix;

  /** @readonly @type {string} */
  output;

  /** @readonly @type {Target[]} */
  targets;

  /** @readonly @type {string} */
  workspace;

  /** @readonly @type {string} */
  repository;

  //  CONSTRUCTORS  //

  /** Constructs the available inputs. */
  constructor() {
    // prepare a resolution handler for the path relative to the workspace
    const resolve = (/** @type {string[]} */ ...segments) =>
      path.join(this.workspace, ...segments);

    // get some working components as well
    const wsp = process.env["GITHUB_WORKSPACE"];
    if (!wsp) throw new Error("GITHUB_WORKSPACE not defined");
    this.workspace = path.resolve(wsp); // get canonical path

    // resolve the required inputs file from the environment
    const cfp = process.env["INPUT_CONFIG"] || Constants.config;
    this.config = JSON.parse(fs.readFileSync(resolve(cfp), "utf-8"));
    if (typeof this.config !== "object") throw new Error("Invalid config file");

    // assign our values from the base inputs
    this.suffix = this.config["suffix"] || Constants.suffix;
    this.output = resolve(this.config["output"] || Constants.output);
    this.vendor = resolve(this.config["vendor"] || Constants.vendor);
    this.repository = this.config["repository"] || Constants.repository;

    // ensure our targets are defaulted to an empty set
    this.targets = this.config["targets"] ?? [];
  }
})();
