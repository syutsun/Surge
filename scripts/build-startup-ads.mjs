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

function targetRecords(text) {
  let section = '';
  const records = [];
  for (const line of text.split(/\r?\n/)) {
    if (line.startsWith('[')) { section = line; continue; }
    const disabled = line.startsWith('#');
    const value = line.replace(/^#+/, '');
    let pattern;
    if (section === '[Script]' && value.includes(' = type=')) {
      pattern = value.match(/, pattern=(.*?), script-path=/)?.[1]?.replace(/^"|"$/g, '');
    } else if (['[URL Rewrite]','[Map Local]'].includes(section) && /^(?:\^|http)/.test(value)) {
      pattern = value.split(/\s/)[0];
    } else if (section === '[Body Rewrite]' && value.startsWith('http-')) {
      pattern = value.split(/\s+/)[1];
    }
    if (pattern) records.push({section, value, pattern, disabled});
  }
  return records;
}
export function verifyCoverage(source, body) {
  const rules = [...new Set(source.split(/\r?\n/).filter(active).filter(line => /\surl\s/.test(line)))];
  const records = targetRecords(body);
  const consumed = new Set();
  for (const rule of rules) {
    const match = rule.match(/^(\S+)\s+url\s+(\S+)(?:\s+(.*))?$/);
    if (!match) throw new Error('Cannot parse upstream rule: '+rule);
    const [,pattern,action,arg] = match;
    const matches = records.map((record,index)=>({record,index})).filter(({record:t}) => {
      if (t.disabled || t.pattern !== pattern) return false;
      const out=t.value, section=t.section;
      if (action==='reject') return section==='[URL Rewrite]' && out.endsWith(' - reject');
      if (action==='reject-200') return section==='[Map Local]' && out.includes('data=" " status-code=200');
      if (action==='reject-dict') return section==='[Map Local]' && out.includes('data="{}" status-code=200');
      if (action==='reject-img') return section==='[Map Local]' && out.includes('data-type=tiny-gif status-code=200');
      if (action.startsWith('script-')) {
        const type=/^script-(request|analyze)/.test(action)?'http-request':'http-response';
        return section==='[Script]' && out.includes('type='+type+',') && out.includes('script-path='+arg+',') &&
          (!action.endsWith('-body') && action!=='script-analyze-echo-response' || out.includes('requires-body=true'));
      }
      if (action==='response-body' || action==='request-body') {
        const separator=' '+action+' ', split=arg.indexOf(separator);
        if (split<0) return false;
        const value=arg.slice(0,split)+'->'+arg.slice(split+separator.length);
        const type=action==='response-body'?'http-response':'http-request';
        return section==='[Script]' && out.includes('type='+type+',') &&
          decodeURIComponent(out.split('argument=')[1] || '')===value;
      }
      if (action==='jsonjq-response-body' || action==='jsonjq-request-body') {
        const type=action==='jsonjq-response-body'?'http-response-jq':'http-request-jq';
        return section==='[Body Rewrite]' && out.startsWith(type+' ') && out.endsWith(arg);
      }
      return false;
    });
    if (matches.length!==1) throw new Error('Rule identity/action mismatch: '+rule);
    consumed.add(matches[0].index);
  }
  if (records.filter(t=>!t.disabled).length!==consumed.size) throw new Error('Unexpected active output rules');
  // Keep all rules intentionally disabled by the author disabled.
  for (const line of source.split(/\r?\n/).filter(line=>/^\s*[#;]/.test(line))) {
    const pattern=line.replace(/^\s*[#;]\s*/,'').match(/^(\S+)\s+url\s+/)?.[1];
    if (pattern && !records.some(t=>t.disabled && t.pattern===pattern)) throw new Error('Disabled rule lost: '+pattern);
  }
  return consumed.size;
}
function restoreOriginalPatterns(sourceRules,body) {
  const normalized = pattern => pattern.replace(/\\\?([A-Za-z_][A-Za-z0-9_.-]*)(?![A-Za-z0-9_.-])/g, '\\?(?:[^#?&]+&)*$1');
  const replacements = new Map();
  for (const rule of sourceRules) {
    const pattern=rule.match(/^(\S+)\s+url\s+/)?.[1];
    if (pattern) {
      const key=normalized(pattern);
      if (replacements.has(key) && replacements.get(key)!==pattern) throw new Error('Ambiguous normalized pattern');
      replacements.set(key,pattern);
    }
  }
  for (const [from,to] of [...replacements].sort((a,b)=>b[0].length-a[0].length)) {
    if (from!==to) body=body.replaceAll(from,to);
  }
  return body;
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
  // Preserve the exact upstream regexes; the generic parser broadens query matching.
  const allSourceRules = source.split(/\r?\n/).map(line=>line.replace(/^\s*[#;]\s*/, '')).filter(line=>/^\S+\s+url\s/.test(line));
  body = restoreOriginalPatterns(allSourceRules, body);
  verifyCoverage(source, body);
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
  const canonicalRoute = line => line.replace(/\s/g,'').toUpperCase().replace(/^HOST-SUFFIX,/,'DOMAIN-SUFFIX,').replace(/^HOST,/,'DOMAIN,');
  if (JSON.stringify(sourceRouting.map(canonicalRoute).sort()) !== JSON.stringify(routing.map(e=>canonicalRoute(e.line)).sort())) throw new Error('Routing identity mismatch');
  console.log(JSON.stringify({
    source: SOURCE,
    sourceSha256: hash(source),
    parserCommit: PARSER_COMMIT,
    inputUrlRules: rules.length,
    convertedUniqueRules: converted,
    routingRules: routing.length,
    mitmHostnames: before.size
  }));
  return [
    '#!name=StartUpAds',
    '#!desc=StartUpAds',
    '', body.trim(), ''
  ].join('\n').replace(/[ \t]+$/gm, '');
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
  console.log(module.split('\n').slice(0,2).join('\n'));
}
if (globalThis.process?.argv?.[1] && import.meta.url === pathToFileURL(globalThis.process.argv[1]).href) await main();
