/** Cleanup the lifecycle for this action when requested. */
import("./lifecycle/index.js").then(({ Lifecycle }) => Lifecycle.cleanup());
