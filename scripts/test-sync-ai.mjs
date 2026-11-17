import test from 'node:test';
import assert from 'node:assert/strict';
import { mergeRules,sections } from './sync-ai.mjs';
const upstream='# First\n'+Array.from({length:30},(_,i)=>'DOMAIN,host'+i+'.test').join('\n')+'\n\n# OpenAI\nDOMAIN,upstream-openai.test\n\n# OpenRouter\nDOMAIN,upstream-router.test\n\n# Last\nDOMAIN,tail.test\n';
const personal='# OpenAI\n#DOMAIN,disabled.test\n# DOMAIN,disabled-with-space.test\nDOMAIN,personal-openai.test\n# OpenRouter\nDOMAIN,personal-router.test\n';
test('replaces only the two personal sections, preserving comments',()=>{
 const result=mergeRules(upstream,personal);
 assert.ok(result.includes('#DOMAIN,disabled.test'));
 assert.ok(result.includes('DOMAIN,personal-openai.test'));
 assert.ok(!result.includes('upstream-openai.test'));
 assert.ok(!result.includes('upstream-router.test'));
 const before=sections(upstream).parts,after=sections(result).parts;
 for(let i=0;i<before.length;i++)if(['First','Last'].includes(before[i].name))assert.equal(before[i].text,after[i].text);
 assert.equal(mergeRules(upstream,personal),result);
});
test('new upstream provider and changed non-personal rules sync automatically',()=>{
 const next=upstream.replace('DOMAIN,tail.test','DOMAIN,new-tail.test')+'\n# Future Provider\nDOMAIN,new-provider.test\n';
 const result=mergeRules(next,personal);
 assert.ok(result.endsWith('# Future Provider\nDOMAIN,new-provider.test\n'));
 assert.ok(result.includes('DOMAIN,new-tail.test'));
 assert.ok(result.includes('DOMAIN,personal-router.test'));
});
test('a provider inserted between the personal sections is not swallowed',()=>{
 const next=upstream.replace('# OpenRouter','# New Between\nDOMAIN,between.test\n\n# OpenRouter');
 assert.ok(mergeRules(next,personal).includes('# New Between\nDOMAIN,between.test\n\n'));
});
test('missing or duplicate boundary fails instead of overwriting personal rules',()=>{
 assert.throws(()=>mergeRules(upstream.replace('# OpenAI','# Renamed'),personal),/Missing or duplicate/);
 assert.throws(()=>mergeRules(upstream+'\n# OpenAI\nDOMAIN,duplicate.test\n',personal),/Missing or duplicate/);
});
test('invalid personal scope, HTTP error pages, and partial downloads fail',()=>{
 assert.throws(()=>mergeRules(upstream,personal+'\n# Extra\nDOMAIN,extra.test\n'),/Personal file/);
 assert.throws(()=>mergeRules('<html>Error</html>',personal),/HTML/);
 assert.throws(()=>mergeRules('# OpenAI\nDOMAIN,short.test',personal),/small upstream/);
});
test('personal edits become the new preserved values',()=>{
 const changed=personal.replace('personal-openai.test','new-personal.test');
 const result=mergeRules(upstream,changed);
 assert.ok(result.includes('DOMAIN,new-personal.test'));
 assert.ok(!result.includes('DOMAIN,personal-openai.test'));
});
