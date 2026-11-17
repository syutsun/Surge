import test from 'node:test';
import assert from 'node:assert/strict';
import {generateCalendar,SOURCE,SCRIPT_URL} from './build-wannianli.mjs';
const fixture='/*\n[filter_local]\nhost,ad.example.test,reject\n[rewrite_local]\n^https://example.test/endpoint url script-response-body '+SOURCE+'\n[mitm]\nhostname = example.test\n*/\n$done({body:$response.body});\n';
test('preserves upstream regex and script while converting only embedded rules',()=>{
 const result=generateCalendar(fixture);
 assert.equal(result.script,fixture);
 assert.deepEqual(result.rewrites,['^https://example.test/endpoint']);
 assert.deepEqual(result.routing,['DOMAIN,ad.example.test,REJECT']);
 assert.deepEqual(result.hosts,['example.test']);
 assert.ok(result.module.includes('script-path='+SCRIPT_URL+', requires-body=true'));
 assert.ok(!result.module.includes('script.hub'));
});
test('rejects HTML and empty upstream',()=>{
 assert.throws(()=>generateCalendar('<html>Unavailable</html>'),/HTML/);
 assert.throws(()=>generateCalendar(''),/Missing/);
});
test('fails on unsupported new actions rather than silently dropping rules',()=>{
 assert.throws(()=>generateCalendar(fixture.replace('script-response-body','new-action')),/Unsupported rewrite/);
});
test('fails if the embedded rule starts referencing a different script',()=>{
 assert.throws(()=>generateCalendar(fixture.replace(SOURCE,'https://example.test/other.js')),/Unsupported rewrite/);
});
test('rejects missing MITM and invalid JavaScript',()=>{
 assert.throws(()=>generateCalendar(fixture.replace('hostname = example.test','')),/Incomplete/);
 assert.throws(()=>generateCalendar(fixture+'const = ;'),SyntaxError);
});
