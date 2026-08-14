// Node module-mocking loader: stubs run-agent.ts's external imports so its
// pure functions can be tested without a live pi runtime.
// Run: node --experimental-strip-types --import ./envelope-loader.mjs <test>.ts
import { register } from "node:module";

register(new URL("./envelope-resolver.mjs", import.meta.url), {
  parentURL: import.meta.url,
});
