// Convert only the configuration embedded in ddgksf2013's original script.
import { createHash } from 'node:crypto';
import { mkdir, writeFile, rename } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import vm from 'node:vm';

export const SOURCE = 'https://ddgksf2013.top/scripts/wannianli.vip.js';
export const SCRIPT_URL = 'https://raw.githubusercontent.com/syutsun/Surge/main/Scripts/wannianli.vip.js';
export function generateCalendar(source) {
  if (/<!doctype|<html/i.test(source.slice(0,300))) throw new Error('Upstream returned HTML');
  const header=source.match(/^\s*\/\*+([\s\S]*?)\*+\//)?.[1];
  if (!header || !source.includes('$done')) throw new Error('Missing original script/header');
  new vm.Script(source,{filename:'wannianli.vip.js'}); // syntax only; never run upstream code in CI
  let section='', hosts=[], routing=[], rewrites=[];
  for (const original of header.split(/\r?\n/)) {
    const line=original.trim();
    if (!line || /^(#|;|\/\/)/.test(line)) continue;
    if (/^\[.+\]$/.test(line)) {section=line.toLowerCase();continue;}
    if (section==='[filter_local]') {
      const m=line.match(/^(host|host-suffix)\s*,\s*([a-z0-9.-]+)\s*,\s*(reject|direct)\s*$/i);
      if (!m) throw new Error('Unsupported routing rule: '+line);
      routing.push((m[1].toLowerCase()==='host'?'DOMAIN':'DOMAIN-SUFFIX')+','+m[2]+','+m[3].toUpperCase());
    } else if (section==='[rewrite_local]') {
      const m=line.match(/^(\S+)\s+url\s+script-response-body\s+(\S+)$/);
      if (!m || m[2]!==SOURCE) throw new Error('Unsupported rewrite rule/script: '+line);
      rewrites.push(m[1]);
    } else if (section==='[mitm]') {
      if (!/^hostname\s*=/.test(line)) throw new Error('Unsupported MITM setting: '+line);
      hosts.push(...line.split('=').slice(1).join('=').split(',').map(s=>s.trim()).filter(Boolean));
    } else if (section) throw new Error('Unsupported upstream section: '+section);
  }
  if (!rewrites.length || !routing.length || !hosts.length) throw new Error('Incomplete upstream configuration');
  const digest=createHash('sha256').update(source).digest('hex');
  const output=[
    '#!name=万年历 Pro · 墨鱼原脚本',
    '#!desc=从墨鱼原脚本内嵌配置转换；需开启MITM并信任证书。',
    '#!author=@ddgksf2013',
    '#!category=应用增强',
    '# Source: '+SOURCE,
    '# Source SHA-256: '+digest,
    '# Rewrites: '+rewrites.length+'; routing rules: '+routing.length+'; MITM hostnames: '+hosts.length,
    '# Original script is mirrored byte-for-byte; no supplementary rules.',
    '',
    '[Rule]',...routing,'',
    '[Script]',
    ...rewrites.map((pattern,index) => 'Wannianli_'+(index+1)+' = type=http-response, pattern='+(pattern.includes(',')?JSON.stringify(pattern):pattern)+', script-path='+SCRIPT_URL+', requires-body=true, max-size=-1, timeout=60, script-update-interval=86400'),
    '',
    '[MITM]','hostname = %APPEND% '+hosts.join(', '),''
  ].join('\n');
  return {module:output,script:source,rewrites,routing,hosts,sha256:digest};
}
export async function main() {
  let source,lastError;
  for(let attempt=0;attempt<3;attempt++) {
    try {
      const response=await fetch(SOURCE,{headers:{'User-Agent':'Surge'},signal:AbortSignal.timeout(30000)});
      if(!response.ok) throw new Error('HTTP '+response.status);
      source=await response.text();
      break;
    } catch(error) {lastError=error;}
  }
  if(!source) throw lastError || new Error('Empty upstream response');
  const result=generateCalendar(source);
  for (const [path,text] of [['Module/Wannianli.sgmodule',result.module],['Scripts/wannianli.vip.js',result.script]]) {
    await mkdir(path.split('/').slice(0,-1).join('/'),{recursive:true});
    await writeFile(path+'.tmp',text);
    await rename(path+'.tmp',path);
  }
  console.log('Validated upstream: '+result.rewrites.length+' rewrites, '+result.routing.length+' routing rules, '+result.hosts.length+' MITM hosts; SHA-256 '+result.sha256);
}
if(globalThis.process?.argv?.[1] && import.meta.url===pathToFileURL(globalThis.process.argv[1]).href) await main();
