const typeboxStub = `
export const Type = {
  Object: () => undefined,
  String: () => undefined,
  Optional: (id) => id,
};
`;

const piUsageStub = `
export function activeSessionId() { return null; }
export function activeUsageRoot() { return null; }
export function newSessionId() { return "test"; }
export function createPiCaptureFile() { return null; }
export function capturePiFile() {}
export function capturePiStream() {}
export const INLINE_CAPTURE_ENV = {};
export const SESSION_ENV = {};
export const USAGE_ROOT_ENV = "USAGE_ROOT";
`;

const apiStub = `
export const ExtensionAPI = class {};
`;

// OpenCode plugin API (ST-0403): Plugin.define returns its definition as it is.
const opencodePluginStub = `
export const Plugin = { define: (definition) => definition };
`;

export async function resolve(specifier, context, nextResolve) {
  if (specifier === "typebox") {
    return { url: "data:text/javascript," + encodeURIComponent(typeboxStub), shortCircuit: true };
  }
  if (specifier === "@earendil-works/pi-coding-agent") {
    return { url: "data:text/javascript," + encodeURIComponent(apiStub), shortCircuit: true };
  }
  if (specifier === "@opencode-ai/plugin") {
    return { url: "data:text/javascript," + encodeURIComponent(opencodePluginStub), shortCircuit: true };
  }
  if (specifier.endsWith("pi-usage.ts") || specifier === "./pi-usage.ts") {
    return { url: "data:text/javascript," + encodeURIComponent(piUsageStub), shortCircuit: true };
  }
  return nextResolve(specifier, context);
}
