// Build only ddgksf2013's original StartUpAds rules. No supplementary ad rules.
import { createHash } from 'node:crypto';
import { writeFile, mkdir, rename } from 'node:fs/promises';
import { dirname } from 'node:path';
import { pathToFileURL } from 'node:url';
import vm from 'node:vm';

export const SOURCE = 'https://ddgksf2013.top/rewrite/StartUpAds.conf';
export const PARSER_COMMIT = 'b8e405cba4e751feaacda97f2148bf3590b5c92d';
export const PARSER_SHA256 = 'b95ef99a043c934ff2870b8f973e749ea36c52837e704afaa6c68b138af2e483';
export const hash = text => createHash('sha256').update(text).digest('hex');
const TYPES = new Set(['reject','reject-200','reject-img','reject-dict','script-response-body','script-response-header','script-request-body','script-request-header','script-analyze-echo-response','response-body','request-body','jsonjq-response-body','jsonjq-request-body']);
const active = line => line.trim() && !/^\s*(#|;|\/\/)/.test(line);
function entries(text) {
  let section = '';
  const result = [];
  for (const line of text.split(/\r?\n/)) {
    if (/^\[/.test(line)) section = line.trim();
    else if (active(line)) result.push({ section, line });
  }
  return result;
}
export async function build({ source, parser, getText }) {
  if (hash(parser) !== PARSER_SHA256) throw new Error('Pinned parser checksum mismatch');
  if (/<html|<!doctype/i.test(source) || !source.includes('@ScriptName')) throw new Error('Source is not the original QX config');
  const input = source.split(/\r?\n/).filter(active);
  const rules = input.filter(line => /\surl\s/.test(line));
  if (rules.length < 400) throw new Error('Unexpectedly small upstream config');
  for (const line of rules) {
    const type = line.match(/\surl\s+(\S+)/)?.[1];
    if (!TYPES.has(type)) throw new Error('Unsupported new upstream action: ' + type);
  }
  // The parser reads remote resources through this adapter; no upstream script is executed.
  const cache = new Map([[SOURCE, source]]);
  async function cached(url) {
    if (!cache.has(url)) cache.set(url, await getText(url));
    return cache.get(url);
  }
  const notifications = [];
  const values = {};
  let watchdog;
  const result = await new Promise((resolve, reject) => {
    watchdog = setTimeout(() => reject(new Error('Conversion timed out')), 120000);
    const context = {
      $environment: { 'surge-version': '6.0' },
      $request: { url: 'http://script.hub/file/_start_/' + SOURCE + '/_end_/StartUpAds.sgmodule?type=qx-rewrite&target=surge-module&jqEnabled=true&n=' + encodeURIComponent('墨鱼去开屏2.0') },
      $persistentStore: { read: key => values[key] ?? null, write: (value,key) => (values[key]=value,true) },
      $notification: { post: (...args) => notifications.push(args) },
      $httpClient: { get: (options,callback) => {
        cached(options.url).then(body => callback(null,{status:200,headers:{}},body),error => callback(String(error),{status:500},''));
      }},
      $done: resolve, console: { log() {} }, setTimeout, clearTimeout, URL, TextEncoder, TextDecoder
    };
    try { vm.runInNewContext(parser, context, {timeout:30000}); } catch(error) { reject(error); }
  }).finally(() => clearTimeout(watchdog));
  if (result?.response?.status !== 200 || notifications.length) throw new Error('Conversion error: ' + JSON.stringify(notifications) + ' ' + result?.response?.body?.slice(0,200));
  let body = result.response.body;
  const firstSection = body.indexOf('[Rule]');
  if (firstSection < 0) throw new Error('Missing module sections');
  body = body.slice(firstSection);
  const originalScripts = new Set(rules.filter(line => /\surl\s+script-/.test(line)).map(line => line.trim().split(/\s+/).at(-1)));
  const binary = new Set();
  for (const url of originalScripts) {
    const script = await cached(url);
    if (script.includes('.bodyBytes')) binary.add(url);
  }
  let section = '', number = 0;
  body = body.split('\n').map(line => {
    if (line.startsWith('[')) section = line;
    if (section === '[Script]' && active(line) && !line.startsWith('[')) {
      number++;
      line = line.replace(/^([^=]+?)\s*=/, (_,name) => 'Moyu_' + String(number).padStart(3,'0') + '_' + name.trim() + ' =');
      const url = line.match(/script-path=([^,\s]+)/)?.[1];
      if (binary.has(url) && !line.includes('binary-body-mode=')) line += ', binary-body-mode=true';
    }
    return line;
  }).join('\n');
  const out = entries(body);
  const actionSections = new Set(['[URL Rewrite]','[Map Local]','[Body Rewrite]','[Script]']);
  const converted = out.filter(e => actionSections.has(e.section)).length;
  const uniqueInput = new Set(rules).size;
  if (converted !== uniqueInput) throw new Error('Coverage mismatch: ' + converted + ' != ' + uniqueInput);
  if (/https?:\/\/script\.hub\b/i.test(body)) throw new Error('Runtime Script Hub dependency');
  const sourceHosts = input.find(line => /^hostname\s*=/.test(line));
  const outputHosts = out.find(e => e.section === '[MITM]' && /^hostname\s*=/.test(e.line))?.line;
  const hosts = line => new Set(line?.split('=').slice(1).join('=').replace(/%APPEND%|%INSERT%/g,'').split(',').map(x=>x.trim()).filter(Boolean));
  const before = hosts(sourceHosts), after = hosts(outputHosts);
  if (!before.size || before.size !== after.size || [...before].some(h=>!after.has(h))) throw new Error('MITM hostname mismatch');
  const sourceRouting = input.filter(line => /^host(?:-suffix)?,/.test(line));
  const routing = out.filter(e=>e.section==='[Rule]');
  if (sourceRouting.length !== routing.length) throw new Error('Routing count mismatch');
  const upstreamDate = source.match(/@UpdateTime\s+(\S+)/)?.[1] || 'unknown';
  const sourceNotice = source.split('// ==/UserScript==')[0].split('\n').map(line=>'# '+line).join('\n');
  return [
    '#!name=墨鱼去开屏2.0 · 原规则自动转换',
    '#!desc=仅转换墨鱼原规则，无附加应用补丁；需开启MITM并信任证书。',
    '#!author=@ddgksf2013',
    '#!category=广告屏蔽',
    '# Source: '+SOURCE,
    '# Source update: '+upstreamDate,
    '# Source SHA-256: '+hash(source),
    '# Parser: https://github.com/Script-Hub-Org/Script-Hub/tree/'+PARSER_COMMIT,
    '# URL rules: '+rules.length+'; unique converted: '+converted,
    '# Routing rules: '+routing.length+'; MITM hostnames: '+before.size,
    '# Only format compatibility: unique script names and binary-body-mode.',
    sourceNotice, '', body.trim(), ''
  ].join('\n');
}
async function download(url) {
  let last;
  for (let attempt=0; attempt<3; attempt++) {
    try {
      const response = await fetch(url,{headers:{'User-Agent':'Surge'},signal:AbortSignal.timeout(30000)});
      if (!response.ok) throw new Error(url+': HTTP '+response.status);
      const text = await response.text();
      if (!text.trim() || /<!doctype html|<html/i.test(text.slice(0,300))) throw new Error(url+': unexpected HTML/empty response');
      return text;
    } catch(error) { last=error; }
  }
  throw last;
}
export async function main() {
  const [source, parser] = await Promise.all([
    download(SOURCE),
    download('https://raw.githubusercontent.com/Script-Hub-Org/Script-Hub/'+PARSER_COMMIT+'/Rewrite-Parser.js')
  ]);
  const module = await build({source,parser,getText:download});
  const output = 'Module/StartUpAds.sgmodule';
  await mkdir(dirname(output),{recursive:true});
  await writeFile(output+'.tmp',module);
  await rename(output+'.tmp',output);
  console.log(module.split('\n').slice(0,11).join('\n'));
}
if (globalThis.process?.argv?.[1] && import.meta.url === pathToFileURL(globalThis.process.argv[1]).href) await main();
