import test from 'node:test';
import assert from 'node:assert/strict';
import { verifyCoverage } from './build-startup-ads.mjs';

const source = String.raw`^https://example.test/ad\?id=1 url reject-200
^https://example.test/script url script-response-body https://example.test/original.js
^https://example.test/replace url response-body old response-body new
#^https://example.test/disabled url reject-200`;
const module = String.raw`[Map Local]
^https://example.test/ad\?id=1 data-type=text data=" " status-code=200
#^https://example.test/disabled data-type=text data=" " status-code=200
[Script]
one = type=http-response, pattern=^https://example.test/script, script-path=https://example.test/original.js, requires-body=true, timeout=60
two = type=http-response, pattern=^https://example.test/replace, script-path=https://example.test/helper.js, requires-body=true, argument=old-%3Enew`;

test('every original action is present and author-disabled rules stay disabled', () => {
  assert.equal(verifyCoverage(source,module),3);
});
test('same rule count with a changed regex must fail', () => {
  assert.throws(()=>verifyCoverage(source,module.replace('ad\\?id=1','ad\\?id=2')),/mismatch/);
});
test('query-order broadening must fail exact upstream matching', () => {
  assert.throws(()=>verifyCoverage(source,module.replace('ad\\?id=1','ad\\?(?:[^#?&]+&)*id=1')),/mismatch/);
});
test('wrong script path or missing body access must fail', () => {
  assert.throws(()=>verifyCoverage(source,module.replace('original.js','different.js')),/mismatch/);
  assert.throws(()=>verifyCoverage(source,module.replace('requires-body=true','requires-body=false')),/mismatch/);
});
test('changed replacement payload must fail', () => {
  assert.throws(()=>verifyCoverage(source,module.replace('old-%3Enew','old-%3Ewrong')),/mismatch/);
});
test('removed disabled rule or additional active rule must fail', () => {
  assert.throws(()=>verifyCoverage(source,module.replace('#^https://example.test/disabled data-type=text data=" " status-code=200','')),/Disabled rule lost/);
  assert.throws(()=>verifyCoverage(source,module+'\nthree = type=http-response, pattern=^https://extra.test, script-path=https://extra.test/ad.js'),/Unexpected/);
});
