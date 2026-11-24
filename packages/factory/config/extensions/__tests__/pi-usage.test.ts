// pi-usage.ts bridges Pi streams to the usage-capture runtime of a project.
// It must never disturb the measured run: every failure removes what it
// staged and returns. The tests build a fake usage root in a temporary folder.
//
// envelope-loader.mjs stubs any import ending in "pi-usage.ts"; a "?realN"
// query keeps the real module, and a fresh N gives fresh module state.
//
// Run: node --experimental-strip-types --import ./envelope-loader.mjs --test ./pi-usage.test.ts
import { test, afterEach } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import {
  chmodSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  realpathSync,
  rmSync,
  statSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

type Usage = typeof import("../pi-usage.ts");

// One shared instance serves every test that keeps no state across calls;
// loadFresh gives the tests of the cached usage root and the fallback session id their own.
let counter = 0;
async function load(): Promise<Usage> {
  return (await import("../pi-usage.ts?real")) as Usage;
}
async function loadFresh(): Promise<Usage> {
  return (await import(`../pi-usage.ts?fresh${counter++}`)) as Usage;
}

const ROOT_ENV = "PI_AGENT_FACTORY_USAGE_ROOT";
const SESSION_ENV = "PI_AGENT_FACTORY_SESSION_ID";
const savedEnv = { root: process.env[ROOT_ENV], session: process.env[SESSION_ENV] };
const cleanups: Array<() => void> = [];
afterEach(() => {
  for (const key of [ROOT_ENV, SESSION_ENV]) delete process.env[key];
  while (cleanups.length) cleanups.pop()!();
});
process.on("exit", () => {
  if (savedEnv.root !== undefined) process.env[ROOT_ENV] = savedEnv.root;
});

type RootOptions = { git?: boolean; ready?: boolean; state?: string | null; scripts?: boolean };

// A usage root. The fake bootstrap script records its arguments in spawned.json.
function makeRoot({ git = false, ready = true, state, scripts = true }: RootOptions = {}, fixed?: string) {
  let root: string;
  if (fixed) {
    root = fixed;
    rmSync(root, { recursive: true, force: true });
    mkdirSync(root);
  } else {
    root = realpathSync(mkdtempSync(join(tmpdir(), "pi-usage-")));
    cleanups.push(() => rmSync(root, { recursive: true, force: true }));
  }
  const af = join(root, ".agent-factory");
  const scriptDir = join(af, "factory", "scripts");
  mkdirSync(scriptDir, { recursive: true });
  mkdirSync(join(af, "usage", "runtime", "bin"), { recursive: true });
  mkdirSync(join(af, "usage", "control", "pending"), { recursive: true });
  mkdirSync(join(af, "usage", ".capture"), { recursive: true });
  writeFileSync(join(af, "install.json"), "{}");
  if (scripts) writeFileSync(join(scriptDir, "usage-capture"), "");
  writeFileSync(join(scriptDir, "usage-capture-runtime"), "#!/bin/sh\nexit 0\n");
  chmodSync(join(scriptDir, "usage-capture-runtime"), 0o755);
  writeFileSync(
    join(scriptDir, "pi-capture-bootstrap.mjs"),
    `import { writeFileSync, renameSync } from "node:fs";
const out = ${JSON.stringify(join(root, "spawned.json"))};
writeFileSync(out + ".tmp", JSON.stringify({ argv: process.argv.slice(2), cwd: process.cwd() }));
renameSync(out + ".tmp", out);
`,
  );
  if (ready) {
    writeFileSync(join(af, "usage", "runtime", ".requirements-sha256"), "x");
    writeFileSync(join(af, "usage", "runtime", "bin", "python"), "");
  }
  const stateText = state === undefined ? JSON.stringify({ mode: "active", generation: "g1" }) : state;
  if (stateText !== null) writeFileSync(join(af, "usage", "control", "state.json"), stateText);
  if (git) {
    execFileSync("git", ["init", "--quiet", "-b", "dev", root]);
    execFileSync("git", ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "--quiet", "--allow-empty", "-m", "i"], {
      cwd: root,
    });
  }
  const capture = join(af, "usage", ".capture");
  const pending = join(af, "usage", "control", "pending");
  return { root, capture, pending, spawned: join(root, "spawned.json") };
}

// The shared module instance caches its usage root, so its tests rebuild this one path.
const sharedPath = realpathSync(mkdtempSync(join(tmpdir(), "pi-usage-shared-")));
process.on("exit", () => rmSync(sharedPath, { recursive: true, force: true }));
const sharedRoot = (options: RootOptions = {}) => makeRoot(options, sharedPath);

async function spawnedArgs(path: string) {
  for (let i = 0; i < 200; i++) {
    if (existsSync(path)) return JSON.parse(readFileSync(path, "utf-8")) as { argv: string[]; cwd: string };
    await new Promise((r) => setTimeout(r, 25));
  }
  assert.fail("the capture bootstrap never ran");
}

const arg = (argv: string[], name: string) => argv[argv.indexOf(name) + 1];

test("pi-usage: activeUsageRoot falls back to the working directory and publishes it", async () => {
  const { activeUsageRoot } = await loadFresh();
  const r = makeRoot({ scripts: false });
  assert.equal(activeUsageRoot(r.root), r.root);
  assert.equal(process.env[ROOT_ENV], r.root);
  assert.equal(activeUsageRoot("/elsewhere"), r.root, "the first answer is cached");
});

test("pi-usage: activeUsageRoot derives the primary checkout from a linked worktree", async () => {
  const { activeUsageRoot } = await loadFresh();
  const r = makeRoot({ git: true });
  const linked = join(r.root, "..", `${r.root.split("/").pop()}-linked`);
  execFileSync("git", ["worktree", "add", "--quiet", "-b", "side", linked], { cwd: r.root });
  cleanups.push(() => rmSync(linked, { recursive: true, force: true }));
  assert.equal(activeUsageRoot(linked), r.root);
});

test("pi-usage: activeUsageRoot accepts an inherited root equal to the working directory when git gives none", async () => {
  const { activeUsageRoot } = await loadFresh();
  const r = makeRoot();
  process.env[ROOT_ENV] = r.root;
  assert.equal(activeUsageRoot(r.root), r.root);
});

test("pi-usage: activeUsageRoot rejects an inherited root that is not trustworthy", async () => {
  const git = makeRoot({ git: true });
  const plain = makeRoot();
  const noInstall = makeRoot();
  rmSync(join(noInstall.root, ".agent-factory", "install.json"));
  const noScript = makeRoot({ scripts: false });
  const cases: Array<[string, string, string]> = [
    ["relative path", "relative/dir", plain.root],
    ["unnormalized path", `${plain.root}/../${plain.root.split("/").pop()}`, plain.root],
    ["disagrees with derived", plain.root, git.root],
    ["differs from the working directory", git.root, plain.root],
    ["no install manifest", noInstall.root, noInstall.root],
    ["no capture script", noScript.root, noScript.root],
  ];
  for (const [label, inherited, cwd] of cases) {
    const { activeUsageRoot } = await loadFresh();
    process.env[ROOT_ENV] = inherited;
    assert.equal(activeUsageRoot(cwd), cwd, label);
  }
});

// The coverage report keeps the last module instance it lists, so the shared
// instance below is imported only after every fresh one.
test("pi-usage: activeUsageRoot derives the root from git, accepts the agreeing inherited root and caches it", async () => {
  const { activeUsageRoot } = await load();
  const r = sharedRoot({ git: true });
  process.env[ROOT_ENV] = r.root;
  assert.equal(activeUsageRoot(r.root), r.root);
  assert.equal(process.env[ROOT_ENV], r.root);
  assert.equal(activeUsageRoot("/elsewhere"), r.root, "the first answer is cached");
});

test("pi-usage: the default export is an extension factory that does nothing", async () => {
  const mod = await load();
  assert.equal(mod.default({} as never), undefined);
});

test("pi-usage: newSessionId returns a fresh pi- id each time", async () => {
  const { newSessionId } = await load();
  const a = newSessionId();
  assert.match(a, /^pi-[0-9a-f-]{36}$/);
  assert.notEqual(a, newSessionId());
});

test("pi-usage: activeSessionId prefers the session file, then the environment, then one stable fallback", async () => {
  const { activeSessionId } = await load();
  assert.equal(activeSessionId({ getSessionFile: () => "/x/y/abc.jsonl" }), "abc");
  process.env[SESSION_ENV] = "from-env";
  assert.equal(activeSessionId({ getSessionFile: () => undefined }), "from-env");
  delete process.env[SESSION_ENV];
  const fallback = activeSessionId();
  assert.match(fallback, /^pi-/);
  assert.equal(activeSessionId({ getSessionFile: () => undefined }), fallback);
});

test("pi-usage: canonicalPiModel maps a reported model to its model.conf row value", async () => {
  const { canonicalPiModel } = await load();
  const root = mkdtempSync(join(tmpdir(), "pi-usage-conf-"));
  cleanups.push(() => rmSync(root, { recursive: true, force: true }));
  mkdirSync(join(root, "config"));
  writeFileSync(
    join(root, "config", "model.conf"),
    [
      "# pi.commented = openrouter/skip/me",
      "",
      "claude.dev = claude-x",
      "pi.nolink",
      "pi.empty =",
      "pi.a = openrouter/z-ai/glm-5.2",
      "pi.b = openrouter/other/zed",
      "pi.c = exact/zed",
    ].join("\n"),
  );
  assert.equal(canonicalPiModel(root, undefined), undefined);
  assert.equal(canonicalPiModel(root, ""), "");
  assert.equal(canonicalPiModel(root, "z-ai/glm-5.2"), "openrouter/z-ai/glm-5.2");
  assert.equal(canonicalPiModel(root, "glm-5.2"), "openrouter/z-ai/glm-5.2");
  assert.equal(canonicalPiModel(root, "exact/zed"), "exact/zed");
  assert.equal(canonicalPiModel(root, "any/zed"), "openrouter/other/zed");
  assert.equal(canonicalPiModel(root, "unknown/model"), "unknown/model");
  assert.equal(canonicalPiModel(join(root, "nowhere"), "m/x"), "m/x");
});

test("pi-usage: createPiCaptureFile stages an empty private file in the capture folder", async () => {
  const { createPiCaptureFile } = await load();
  const r = sharedRoot();
  const file = createPiCaptureFile(r.root, "sess")!;
  assert.ok(file.startsWith(join(r.capture, "sess-")));
  assert.equal(statSync(file).mode & 0o777, 0o600);
  assert.equal(readFileSync(file, "utf-8"), "");
});

test("pi-usage: createPiCaptureFile returns nothing without a ready runtime", async () => {
  const { createPiCaptureFile } = await load();
  assert.equal(createPiCaptureFile(sharedRoot({ ready: false }).root, "s"), undefined);
});

test("pi-usage: createPiCaptureFile returns nothing when the capture folder is missing or redirected", async () => {
  const missing = sharedRoot();
  rmSync(missing.capture, { recursive: true });
  assert.equal((await load()).createPiCaptureFile(missing.root, "s"), undefined);

  const redirected = sharedRoot();
  const elsewhere = mkdtempSync(join(tmpdir(), "pi-usage-elsewhere-"));
  cleanups.push(() => rmSync(elsewhere, { recursive: true, force: true }));
  rmSync(redirected.capture, { recursive: true });
  symlinkSync(elsewhere, redirected.capture);
  assert.equal((await load()).createPiCaptureFile(redirected.root, "s"), undefined);
  assert.deepEqual(readdirSync(elsewhere), []);
});

test("pi-usage: capturePiStream writes the stream and registers one detached capture", async () => {
  const { capturePiStream } = await load();
  const r = sharedRoot({ git: true });
  capturePiStream(r.root, '{"a":1}', {
    sessionId: "sess",
    parentSessionId: "par",
    depth: 2,
    agent: "human",
    model: "m/x",
    exitStatus: "success",
  });
  const { argv, cwd } = await spawnedArgs(r.spawned);
  assert.equal(cwd, r.root);
  assert.equal(arg(argv, "--session"), "sess");
  assert.equal(arg(argv, "--depth"), "2");
  assert.equal(arg(argv, "--parent-session"), "par");
  assert.equal(arg(argv, "--agent"), "human");
  assert.equal(arg(argv, "--model"), "m/x");
  assert.equal(arg(argv, "--exit-status"), "success");
  assert.equal(arg(argv, "--branch"), "dev");
  assert.match(arg(argv, "--commit"), /^[0-9a-f]{40}$/);
  assert.equal(arg(argv, "--usage-generation"), "g1");
  assert.equal(arg(argv, "--cli"), "pi");
  const transcript = arg(argv, "--transcript");
  assert.equal(readFileSync(transcript, "utf-8"), '{"a":1}\n');
  assert.equal(statSync(transcript).mode & 0o777, 0o600);
  const marker = arg(argv, "--pending-marker");
  assert.deepEqual(JSON.parse(readFileSync(marker, "utf-8")).session_id, "sess");
  assert.equal(JSON.parse(readFileSync(marker, "utf-8")).generation, "g1");
});

test("pi-usage: capturePiStream keeps a stream that already ends in a newline and omits unset options", async () => {
  const { capturePiStream } = await load();
  const r = sharedRoot();
  capturePiStream(r.root, "line\n", {});
  const { argv } = await spawnedArgs(r.spawned);
  assert.equal(readFileSync(arg(argv, "--transcript"), "utf-8"), "line\n");
  assert.match(arg(argv, "--session"), /^pi-/);
  assert.equal(arg(argv, "--depth"), "0");
  for (const flag of ["--branch", "--commit", "--parent-session", "--agent", "--model", "--exit-status"]) {
    assert.equal(argv.includes(flag), false, flag);
  }
});

test("pi-usage: capturePiStream ignores an empty stream and a root without a ready runtime", async () => {
  const { capturePiStream } = await load();
  const r = sharedRoot();
  capturePiStream(r.root, "  \n", {});
  assert.deepEqual(readdirSync(r.capture), []);
  const idle = sharedRoot({ ready: false });
  capturePiStream(idle.root, "x", {});
  assert.deepEqual(readdirSync(idle.capture), []);
});

test("pi-usage: capturePiStream removes the staged file when registration fails", async () => {
  const { capturePiStream } = await load();
  const r = sharedRoot({ state: JSON.stringify({ mode: "removing", generation: "g1" }) });
  capturePiStream(r.root, "x", { sessionId: "s" });
  assert.deepEqual(readdirSync(r.capture), []);
  assert.deepEqual(readdirSync(r.pending), []);
  assert.equal(existsSync(r.spawned), false);
});

test("pi-usage: capturePiFile removes the transcript when the runtime is not ready", async () => {
  const { capturePiFile } = await load();
  const r = sharedRoot({ ready: false });
  const transcript = join(r.capture, "t.jsonl");
  writeFileSync(transcript, "x");
  capturePiFile(r.root, transcript, {});
  assert.equal(existsSync(transcript), false);
});

test("pi-usage: capturePiFile refuses a transcript outside the capture folder", async () => {
  const { capturePiFile } = await load();
  const r = sharedRoot();
  const outside = join(r.root, "outside.jsonl");
  writeFileSync(outside, "x");
  capturePiFile(r.root, outside, { sessionId: "s" });
  assert.equal(existsSync(outside), false);
  assert.deepEqual(readdirSync(r.pending), []);
  assert.equal(existsSync(r.spawned), false);
});

test("pi-usage: capturePiFile refuses a redirected pending folder", async () => {
  const { capturePiFile } = await load();
  const r = sharedRoot();
  const elsewhere = mkdtempSync(join(tmpdir(), "pi-usage-elsewhere-"));
  cleanups.push(() => rmSync(elsewhere, { recursive: true, force: true }));
  rmSync(r.pending, { recursive: true });
  symlinkSync(elsewhere, r.pending);
  const transcript = join(r.capture, "t.jsonl");
  writeFileSync(transcript, "x");
  capturePiFile(r.root, transcript, { sessionId: "s" });
  assert.equal(existsSync(transcript), false);
  assert.deepEqual(readdirSync(elsewhere), []);
});

test("pi-usage: capturePiFile fails quietly when the usage state is missing or has no generation", async () => {
  for (const state of [null, JSON.stringify({ mode: "active" })]) {
    const { capturePiFile } = await load();
    const r = sharedRoot({ state });
    const transcript = join(r.capture, "t.jsonl");
    writeFileSync(transcript, "x");
    capturePiFile(r.root, transcript, { sessionId: "s" });
    assert.equal(existsSync(transcript), false);
    assert.equal(existsSync(r.spawned), false);
  }
});

test("pi-usage: capturePiFile fails quietly when the bootstrap script is missing", async () => {
  const { capturePiFile } = await load();
  const r = sharedRoot();
  rmSync(join(r.root, ".agent-factory", "factory", "scripts", "pi-capture-bootstrap.mjs"));
  const transcript = join(r.capture, "t.jsonl");
  writeFileSync(transcript, "x");
  capturePiFile(r.root, transcript, { sessionId: "s" });
  assert.equal(existsSync(transcript), false);
  assert.deepEqual(readdirSync(r.pending), []);
});
