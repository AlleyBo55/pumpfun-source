/* PREPARED ONLY. Root must admit this exact source before it imports SDKs. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const Module = require('node:module');
const [graphArg, fixtureArg, expectedArg, modulesArg, outputArg] = process.argv.slice(2);
if (![graphArg, fixtureArg, expectedArg, modulesArg, outputArg].every(Boolean)) throw Error('Five exact paths required');
const graph = fs.realpathSync(graphArg);
const output = path.resolve(outputArg);
const fixture = JSON.parse(fs.readFileSync(fixtureArg));
const oracle = JSON.parse(fs.readFileSync(expectedArg));
const modules = JSON.parse(fs.readFileSync(modulesArg));
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
let phase = 'bootstrap';
const blocked = [], moduleAttempts = [], addonAttempts = [], rows = [];
function deny(kind) {
  return function () {
    const record = {phase, kind, denied: true}; blocked.push(record);
    throw Object.assign(Error('OFFLINE_EXPERIMENT_DENIED: ' + kind), {code: 'OFFLINE_EXPERIMENT_DENIED'});
  };
}
for (const name of ['node:http', 'node:https']) {
  const object = require(name);
  for (const key of ['request', 'get']) object[key] = deny(name + '.' + key);
}
const net = require('node:net');
net.connect = deny('net.connect'); net.createConnection = deny('net.createConnection');
net.Socket.prototype.connect = deny('net.Socket.connect');
const tls = require('node:tls'); tls.connect = deny('tls.connect');
require('node:http2').connect = deny('http2.connect');
require('node:dgram').createSocket = deny('dgram.createSocket');
const dns = require('node:dns');
for (const key of Object.keys(dns)) if (/^(lookup|resolve|reverse)/.test(key) && typeof dns[key] === 'function') dns[key] = deny('dns.' + key);
const dnsPromises = require('node:dns/promises');
for (const key of Object.keys(dnsPromises)) if (typeof dnsPromises[key] === 'function') dnsPromises[key] = deny('dns.promises.' + key);
globalThis.fetch = deny('global.fetch');
if (typeof globalThis.WebSocket !== 'undefined') globalThis.WebSocket = deny('global.WebSocket');
const childProcess = require('node:child_process');
for (const key of ['spawn', 'spawnSync', 'exec', 'execSync', 'execFile', 'execFileSync', 'fork']) childProcess[key] = deny('child_process.' + key);

// Integrity observation only: return the genuine loader's result unchanged.
// No fake package exports, account data, provider or Connection is supplied.
const realLoad = Module._load, realResolve = Module._resolveFilename;
function checkedModule(filename) {
  const absolute = fs.realpathSync(filename);
  const relative = path.relative(graph, absolute).split(path.sep).join('/');
  if (!(relative in modules) || relative.startsWith('../') || hash(absolute) !== modules[relative]) {
    blocked.push({phase, kind: 'unlocked-module', filename, denied: true});
    throw Error('Module is not an authenticated graph file: ' + relative);
  }
  return relative;
}
Module._load = function (request, parent, isMain) {
  let filename;
  try { filename = realResolve.call(Module, request, parent, isMain); }
  catch (error) {
    moduleAttempts.push({phase, request, resolved: null, code: error.code || null});
    throw error;
  }
  if (!Module.isBuiltin(filename)) {
    const relative = checkedModule(filename);
    moduleAttempts.push({phase, request, resolved: relative});
  }
  return Reflect.apply(realLoad, this, arguments);
};
const realDlopen = process.dlopen;
process.dlopen = function (module, filename, flags) {
  const relative = checkedModule(filename);
  const record = {phase, file: relative, sha256: modules[relative], state: 'STARTED'};
  addonAttempts.push(record);
  try {
    const result = Reflect.apply(realDlopen, this, arguments);
    record.state = 'LOADED';
    return result;
  } catch (error) {
    record.state = 'LOAD_ERROR';
    record.error = {name: error.name, message: error.message, code: error.code || null, stack: error.stack};
    throw error;
  }
};
function serialize(ix, expected) {
  return {programId: ix.programId.toBase58(), dataHex: Buffer.from(ix.data).toString('hex'),
    keys: ix.keys.map((item, index) => ({index, idlName: expected.keys[index]?.idlName || null,
      key: item.pubkey.toBase58(), isSigner: item.isSigner, isWritable: item.isWritable}))};
}
function compare(actual, expected) {
  const differences = [];
  for (const key of ['programId', 'dataHex']) if (actual[key] !== expected[key]) differences.push(key);
  if (actual.keys.length !== expected.keys.length) differences.push('keys.length');
  for (const [i, want] of expected.keys.entries()) {
    const got = actual.keys[i];
    if (!got) continue;
    for (const key of ['index', 'idlName', 'isSigner', 'isWritable']) if (got[key] !== want[key]) differences.push('keys.' + i + '.' + key);
    if (want.key !== null && got.key !== want.key) differences.push('keys.' + i + '.key');
  }
  return differences;
}
function publicInputs(value) {
  if (value && typeof value.toBase58 === 'function') return value.toBase58();
  if (Array.isArray(value)) return value.map(publicInputs);
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, publicInputs(item)]));
  return value;
}
function loadedModules() {
  return Object.keys(require.cache).filter(file => path.resolve(file) !== __filename).map(file => {
    const relative = checkedModule(file);
    return {file: relative, sha256: hash(file), nativeAddon: file.endsWith('.node')};
  }).sort((a, b) => a.file.localeCompare(b.file));
}
function checkpoint(state, error = null) {
  const result = {state, phase, node: process.version, versions: process.versions, platform: process.platform, arch: process.arch,
    graphRoot: graph, fixtureSha256: hash(fixtureArg), expectedSha256: hash(expectedArg),
    rows, blocked, moduleAttempts, addonAttempts, loadedModules: loadedModules(), error,
    randomOverride: false, targetVMs: 0, compilers: 0, installations: 0,
    interpretation: 'Actual public compiled SDK instruction wrappers on synthetic inputs; no valid state or contract identity claim'};
  fs.writeFileSync(output, JSON.stringify(result, null, 2) + '\n');
}
(async () => {
  phase = 'load-genuine-web3';
  const rootRequire = Module.createRequire(path.join(graph, 'package.json'));
  const pumpRequire = Module.createRequire(path.join(graph, 'node_modules/@pump-fun/pump-sdk/package.json'));
  const swapRequire = Module.createRequire(path.join(graph, 'node_modules/@pump-fun/pump-swap-sdk/package.json'));
  const web3s = [rootRequire('@solana/web3.js'), pumpRequire('@solana/web3.js'), swapRequire('@solana/web3.js')];
  for (const web3 of new Set(web3s)) {
    for (const name of ['getAccountInfo', 'getAccountInfoAndContext', 'getMultipleAccountsInfo', 'getMultipleAccountsInfoAndContext',
      'sendTransaction', 'sendRawTransaction', 'simulateTransaction', 'requestAirdrop', 'confirmTransaction']) {
      if (typeof web3.Connection.prototype[name] === 'function') web3.Connection.prototype[name] = deny('Connection.' + name);
    }
    for (const type of [web3.Transaction, web3.VersionedTransaction]) {
      if (!type) continue;
      for (const name of ['sign', 'partialSign', 'addSignature']) {
        if (typeof type.prototype[name] === 'function') type.prototype[name] = deny(type.name + '.' + name);
      }
    }
  }
  phase = 'load-public-compiled-SDKs';
  const main = rootRequire('@pump-fun/pump-sdk');
  const pumpAmm = rootRequire('@pump-fun/pump-sdk/swap');
  const swapAmm = rootRequire('@pump-fun/pump-swap-sdk');
  const contexts = {
    '@pump-fun/pump-sdk': {instance: main.PUMP_SDK, web3: web3s[1]},
    '@pump-fun/pump-sdk/swap': {instance: pumpAmm.PUMP_AMM_SDK, web3: web3s[1]},
    '@pump-fun/pump-swap-sdk': {instance: swapAmm.PUMP_AMM_SDK, web3: web3s[2]},
  };
  checkpoint('LOADED_NOT_YET_CALLED');
  for (const spec of oracle.rows) {
    phase = spec.id;
    const context = contexts[spec.public_entry];
    const fn = context.instance[spec.method];
    if (typeof fn !== 'function') throw Error('Missing public SDK method: ' + spec.id);
    const key = name => new context.web3.PublicKey(oracle.key_values[name]);
    const token = new context.web3.PublicKey(fixture.quoteTokenProgram);
    const record = {id: spec.id, publicEntry: spec.public_entry, method: spec.method,
      ownerClass: Object.getPrototypeOf(context.instance).constructor.name,
      compiledFunctionSource: Function.prototype.toString.call(fn), state: 'STARTED', blockedBefore: blocked.length};
    record.compiledFunctionSha256 = crypto.createHash('sha256').update(record.compiledFunctionSource).digest('hex');
    rows.push(record); checkpoint('OBSERVATIONS_IN_PROGRESS');
    try {
      let instruction;
      if (spec.method === 'setCoinCreator') {
        record.actualArguments = spec.id.endsWith('-supplied') ? [key('pool').toBase58(), key('baseMint').toBase58()] : [key('pool').toBase58()];
        checkpoint('OBSERVATIONS_IN_PROGRESS');
        instruction = spec.id.endsWith('-supplied') ? await fn.call(context.instance, key('pool'), key('baseMint')) : await fn.call(context.instance, key('pool'));
      } else if (spec.id.includes('-curve-')) {
        const args = {payer: key('payer'), mint: key('baseMint'), quoteMint: new context.web3.PublicKey(fixture.curveQuoteMint)};
        if (spec.method === 'sweepCreatorFeeInstruction') args.creator = key('coinCreator');
        else args.recipient = key('protocolRecipient');
        record.actualArguments = publicInputs(args); checkpoint('OBSERVATIONS_IN_PROGRESS');
        // quoteTokenProgram deliberately omitted: exercise the public default.
        instruction = await fn.call(context.instance, args);
      } else {
        const args = {payer: key('payer'), poolKey: key('pool'), quoteTokenProgram: token,
          pool: {quoteMint: key('ammQuoteMint'), poolQuoteTokenAccount: key('poolQuoteTokenAccount'), coinCreator: key('coinCreator'), isMayhemMode: false}};
        if (spec.method === 'sweepProtocolFeeInstruction') args.globalConfig = {
          protocolFeeRecipients: [key('protocolRecipient')], reservedFeeRecipient: key('reservedRecipient'), reservedFeeRecipients: []};
        record.actualArguments = publicInputs(args); checkpoint('OBSERVATIONS_IN_PROGRESS');
        instruction = await fn.call(context.instance, args);
      }
      record.state = 'CONSTRUCTED'; record.instruction = serialize(instruction, spec.expected);
      record.differences = compare(record.instruction, spec.expected);
      record.fullyCompared = spec.fully_compared_if_constructed;
    } catch (error) {
      record.state = 'ERROR_OBSERVED';
      record.error = {name: error.name, message: error.message, code: error.code || null, stack: error.stack};
    }
    record.blockedAfter = blocked.length; checkpoint('OBSERVATIONS_IN_PROGRESS');
  }
  phase = 'finalize';
  const positiveFailed = rows.some(row => oracle.rows.find(spec => spec.id === row.id).fully_compared_if_constructed &&
    (row.state !== 'CONSTRUCTED' || row.differences.length !== 0 || row.blockedAfter !== row.blockedBefore));
  // Omitted-baseMint rows are observations, never rewritten as successful SDK
  // construction. Their actual failure or partial-oracle construction is retained.
  const infrastructureViolation = blocked.some(row => ['bootstrap', 'load-genuine-web3', 'load-public-compiled-SDKs', 'finalize'].includes(row.phase) || row.kind === 'unlocked-module' || row.kind.startsWith('child_process.') || /\.(sign|partialSign|addSignature)$/.test(row.kind));
  checkpoint(positiveFailed || infrastructureViolation ? 'OBSERVATION_COMPLETE_WITH_UNRESOLVED_FAILURES' : 'OBSERVATION_COMPLETE');
  process.exitCode = positiveFailed || infrastructureViolation ? 1 : 0;
})().catch(error => {
  try { checkpoint('BOOTSTRAP_OR_OBSERVER_FAILURE', {name: error.name, message: error.message, code: error.code || null, stack: error.stack}); }
  catch (writeError) { console.error(writeError.stack); }
  console.error(error.stack); process.exitCode = 1;
});
