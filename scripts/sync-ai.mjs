// Sync ConnersHua/RuleGo AI rules while preserving personal provider sections.
import { readFile, writeFile, rename } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { pathToFileURL } from 'node:url';

export const SOURCE='https://raw.githubusercontent.com/ConnersHua/RuleGo/master/Surge/Ruleset/Extra/AI.list';
export const PERSONAL='config/AI-personal.list';
const HEADERS=['OpenAI','OpenRouter'];
export function sections(text) {
  const normalized=text.replace(/\r\n/g,'\n');
  const matches=[...normalized.matchAll(/^# ([^>\n][^\n]*)$/gm)].filter(m=>!/^(?:DOMAIN|DOMAIN-SUFFIX|DOMAIN-KEYWORD|DOMAIN-WILDCARD)\s*,/.test(m[1]));
  if(!matches.length) throw new Error('No provider section headers');
  return {
    prefix:normalized.slice(0,matches[0].index),
    parts:matches.map((m,i)=>({
      name:m[1].trim(),
      text:normalized.slice(m.index,matches[i+1]?.index ?? normalized.length)
    }))
  };
}
function validateLines(text) {
  if(/<!doctype|<html/i.test(text)) throw new Error('Unexpected HTML');
  for(const line of text.split('\n')) {
    const value=line.trim();
    if(!value || value.startsWith('#')) continue;
    if(!/^(DOMAIN|DOMAIN-SUFFIX|DOMAIN-KEYWORD|DOMAIN-WILDCARD),[^,\s]+(?:,extended-matching)?$/.test(value)) {
      throw new Error('Unexpected rule syntax: '+line);
    }
  }
}
export function mergeRules(upstream,personal) {
  validateLines(upstream);
  validateLines(personal);
  const source=sections(upstream),custom=sections(personal);
  if(upstream.split('\n').filter(line=>/^(DOMAIN|DOMAIN-SUFFIX|DOMAIN-KEYWORD|DOMAIN-WILDCARD),/.test(line)).length<30) {
    throw new Error('Unexpectedly small upstream rule set');
  }
  if(custom.prefix.trim() || custom.parts.length!==2 ||
    HEADERS.some(name=>custom.parts.filter(s=>s.name===name).length!==1)) throw new Error('Personal file must contain only OpenAI and OpenRouter sections');
  const replacements=new Map(custom.parts.map(part=>[part.name,part.text.trimEnd()+'\n\n']));
  for(const name of HEADERS) {
    if(source.parts.filter(part=>part.name===name).length!==1) throw new Error('Missing or duplicate upstream section: '+name);
  }
  const merged=source.prefix+source.parts.map(part=>replacements.get(part.name) ?? part.text).join('');
  const output=sections(merged);
  // Validate the unchanged text of every other section, including future additions.
  for(let i=0;i<source.parts.length;i++) {
    const before=source.parts[i],after=output.parts[i];
    if(!after || before.name!==after.name) throw new Error('Provider order mismatch');
    if(!HEADERS.includes(before.name) && before.text!==after.text) throw new Error('Non-personal section changed: '+before.name);
    if(HEADERS.includes(before.name) && after.text!==replacements.get(before.name)) throw new Error('Personal section mismatch: '+before.name);
  }
  if(output.parts.length!==source.parts.length) throw new Error('Unexpected provider sections');
  return merged;
}
export async function main() {
  const personal=await readFile(PERSONAL,'utf8');
  let upstream,last;
  for(let attempt=0;attempt<3;attempt++) {
    try {
      const response=await fetch(SOURCE,{headers:{'User-Agent':'Surge'},signal:AbortSignal.timeout(30000)});
      if(!response.ok) throw new Error('HTTP '+response.status);
      upstream=await response.text();
      break;
    } catch(error) {last=error;}
  }
  if(!upstream) throw last || new Error('Empty upstream');
  const result=mergeRules(upstream,personal);
  const output='Ruleset/AI.list';
  await writeFile(output+'.tmp',result);
  await rename(output+'.tmp',output);
  const sha=createHash('sha256').update(upstream).digest('hex');
  console.log('Synced '+sections(result).parts.length+' providers; preserved personal OpenAI and OpenRouter. Upstream SHA-256: '+sha);
}
if(globalThis.process?.argv?.[1] && import.meta.url===pathToFileURL(globalThis.process.argv[1]).href) await main();
