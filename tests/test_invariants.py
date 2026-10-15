"""Real-repository copies exercise failures without mutating historical fixtures."""
import contextlib
import copy
import io
import os
import json
from pathlib import Path
import shutil
import tempfile
import subprocess
from unittest import mock
import unittest

from tools import check_invariants as check

ROOT = Path(__file__).resolve().parents[1]


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for path in check.documentation_paths(ROOT):
            target = self.root / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        shutil.copytree(ROOT / 'spec', self.root / 'spec')
        self.registry = json.loads((self.root / check.REGISTRY).read_text())

    def save(self):
        (self.root / check.REGISTRY).write_text(json.dumps(self.registry))

    def refresh(self):
        for path in check.documentation_paths(self.root):
            text = path.read_text()
            if check.BEGIN in text:
                begin, end = text.index(check.BEGIN), text.index(check.END) + len(check.END)
                path.write_text(text[:begin] + check.render_block(self.registry, path.relative_to(self.root).as_posix()) + text[end:])

    def test_repository(self):
        self.assertEqual(len(check.validate(self.root)['invariants']), 24)

    def test_negative_fixtures(self):
        cases = json.loads((ROOT / 'tests/fixtures/invariants/negative-cases.json').read_text())
        for case in cases:
            with self.subTest(case=case['name']):
                # Reset each case independently to the same verified source copy.
                for path in check.documentation_paths(ROOT):
                    target = self.root / path.relative_to(ROOT)
                    shutil.copyfile(path, target)
                self.registry = json.loads((ROOT / check.REGISTRY).read_text())
                doc = self.root / check.CORE
                mutation = case['mutation']
                if mutation == 'duplicate_id':
                    self.registry['invariants'].append(copy.deepcopy(self.registry['invariants'][0]))
                elif mutation == 'missing_id':
                    self.registry['invariants'].pop(0)
                elif mutation == 'dangling_reference':
                    doc.write_text(doc.read_text() + '\nQM-INV-999\n')
                elif mutation == 'mismatched_statement':
                    doc.write_text(doc.read_text().replace('MUST preserve', 'MAY discard', 1))
                elif mutation == 'missing_block':
                    doc.write_text(doc.read_text().replace(check.BEGIN, ''))
                elif mutation == 'duplicate_block':
                    doc.write_text(doc.read_text() + '\n' + check.render_block(self.registry, check.CORE))
                elif mutation == 'missing_document':
                    doc.unlink()
                elif mutation == 'changed_statement':
                    self.registry['invariants'][0]['statement'] += ' New obligation MUST apply.'
                else:
                    self.fail('unknown fixture mutation')
                self.save()
                with self.assertRaisesRegex(check.Invalid, case['error']):
                    check.validate(self.root)

    def test_coordinated_history_rewrite_is_rejected(self):
        self.registry['invariants'][0]['statement'] = 'Backends MUST discard active semantic contracts.'
        self.save()
        (self.root / check.BASELINE).write_text(json.dumps(self.registry))
        self.refresh()
        with self.assertRaisesRegex(check.Invalid, 'historical baseline content changed'):
            check.validate(self.root)

    def test_newline_normalization(self):
        for path in list(check.documentation_paths(self.root)) + [self.root / check.BASELINE]:
            path.write_bytes(path.read_bytes().replace(b'\n', b'\r\n'))
        check.validate(self.root)

    def test_malformed_numeric_reference(self):
        path = self.root / check.CORE
        path.write_text(path.read_text() + '\nQM-INV-0010\n')
        with self.assertRaisesRegex(check.Invalid, 'dangling invariant reference'):
            check.validate(self.root)

    def commit_accepted(self):
        def run(*args):
            return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.DEVNULL).decode().strip()
        run('init', '-q')
        run('add', '.')
        run('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'Accepted registry')
        return run('rev-parse', 'HEAD')

    def accept_minor(self):
        entry = copy.deepcopy(self.registry['invariants'][-1])
        entry['id'] = 'QM-INV-025'
        self.registry['invariants'].append(entry)
        self.registry['registry_version'] = '1.1.0'
        self.save()
        self.refresh()
        return self.commit_accepted()

    def test_latest_accepted_id_cannot_disappear(self):
        base = self.accept_minor()
        self.registry['invariants'].pop()
        self.save()
        self.refresh()
        with self.assertRaisesRegex(check.Invalid, 'missing frozen invariant ID: QM-INV-025'):
            check.validate(self.root, base)

    def test_addition_requires_increment_from_latest_accepted(self):
        base = self.accept_minor()
        entry = copy.deepcopy(self.registry['invariants'][-1])
        entry['id'] = 'QM-INV-026'
        self.registry['invariants'].append(entry)
        self.save()
        self.refresh()
        with self.assertRaisesRegex(check.Invalid, 'minor version increment'):
            check.validate(self.root, base)
        self.registry['registry_version'] = '1.2.0'
        self.save()
        self.refresh()
        check.validate(self.root, base)

    def test_accepted_history_rejects_recomputed_local_digest(self):
        base = self.commit_accepted()
        self.registry['invariants'][0]['statement'] = 'Backends MUST discard active semantic contracts.'
        self.save()
        history = self.root / check.BASELINE
        history.write_text(json.dumps(self.registry))
        self.refresh()
        digest = check.hashlib.sha256(history.read_bytes()).hexdigest()
        with mock.patch.object(check, 'BASELINE_SHA256', digest):
            with self.assertRaisesRegex(check.Invalid, 'accepted historical file changed'):
                check.validate(self.root, base)

    def test_latest_accepted_statement_cannot_change(self):
        base = self.accept_minor()
        self.registry['invariants'][-1]['statement'] += ' New requirement MUST apply.'
        self.save()
        self.refresh()
        with self.assertRaisesRegex(check.Invalid, 'frozen normative statement/title changed'):
            check.validate(self.root, base)

    def test_missing_accepted_registry_fails_closed(self):
        (self.root / check.REGISTRY).unlink()
        base = self.commit_accepted()
        self.save()
        with self.assertRaisesRegex(check.Invalid, 'outside initial foundation bootstrap'):
            check.validate(self.root, base)

    def test_unknown_accepted_ref_fails_closed(self):
        self.commit_accepted()
        with self.assertRaisesRegex(check.Invalid, 'cannot read accepted Git base'):
            check.validate(self.root, 'no-such-ref')

    def test_alphanumeric_reference_suffix(self):
        path = self.root / check.CORE
        path.write_text(path.read_text() + '\nQM-INV-001x\n')
        with self.assertRaisesRegex(check.Invalid, 'dangling invariant reference'):
            check.validate(self.root)

    def test_candidate_registry_symlink(self):
        base = self.commit_accepted()
        path = self.root / check.REGISTRY
        path.unlink()
        path.symlink_to('history/core-invariants-1.0.0.json')
        with self.assertRaisesRegex(check.Invalid, 'symlink'):
            check.validate(self.root, base)

    def test_candidate_history_symlink(self):
        base = self.commit_accepted()
        path = self.root / check.BASELINE
        path.unlink()
        path.symlink_to('../core-invariants.json')
        with self.assertRaisesRegex(check.Invalid, 'symlink'):
            check.validate(self.root, base)

    def test_history_directory_symlink(self):
        original = self.root / 'spec/history'
        original.rename(self.root / 'moved-history')
        original.symlink_to('../moved-history', target_is_directory=True)
        with self.assertRaisesRegex(check.Invalid, 'symlink'):
            check.validate(self.root)

    def test_accepted_history_unusual_names(self):
        paths = [self.root / 'spec/history' / name for name in ('core-invariants-é.json', 'tab\tfile.json', 'line\nfile.json')]
        for path in paths:
            path.write_text('{}\n')
        base = self.commit_accepted()
        check.validate(self.root, base)
        for path in paths:
            with self.subTest(name=path.name):
                path.write_text('{"changed":true}\n')
                with self.assertRaisesRegex(check.Invalid, 'accepted historical file changed'):
                    check.validate(self.root, base)
                path.write_text('{}\n')

    def test_new_history_gitlink_is_rejected(self):
        base = self.commit_accepted()
        path = self.root / 'spec/history/new-submodule'
        path.mkdir()
        subprocess.check_call(['git', '-C', str(self.root), 'update-index', '--add', '--cacheinfo',
                               '160000,' + base + ',spec/history/new-submodule'])
        with self.assertRaisesRegex(check.Invalid, 'not a regular blob'):
            check.validate(self.root, base)

    def test_non_utf8_history_name_is_rejected_before_acceptance(self):
        base = self.commit_accepted()
        name = os.fsencode(self.root / 'spec/history') + b'/invalid-\xff.json'
        with open(name, 'wb') as handle:
            handle.write(b'{}')
        with self.assertRaisesRegex(check.Invalid, 'valid UTF-8'):
            check.validate(self.root, base)

    def test_populated_contract_ancestor_gitlinks_are_rejected(self):
        base = self.commit_accepted()
        for name in ('spec', 'docs'):
            with self.subTest(ancestor=name):
                subprocess.check_call(['git', '-C', str(self.root), 'rm', '--cached', '-qr', name])
                subprocess.check_call(['git', '-C', str(self.root), 'update-index', '--add', '--cacheinfo',
                                       '160000,' + base + ',' + name])
                with self.assertRaisesRegex(check.Invalid, 'not a regular blob'):
                    check.validate(self.root, base)
                subprocess.check_call(['git', '-C', str(self.root), 'reset', '-q', base, '--', name])

    def test_duplicate_json_key(self):
        path = self.root / check.REGISTRY
        path.write_text(path.read_text().replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1'))
        with self.assertRaisesRegex(check.Invalid, 'duplicate JSON key'):
            check.validate(self.root)

    def test_bad_schema(self):
        for value in (True, 0, '1'):
            with self.subTest(value=value):
                self.registry['schema_version'] = value
                self.save()
                with self.assertRaisesRegex(check.Invalid, 'schema_version'):
                    check.validate(self.root)

    def test_unsafe_paths(self):
        for value in ('../escape.md', '/tmp/escape.md', 'docs/../README.md', 'docs//x.md', 'tools/x.md', 'docs\\x.md'):
            with self.subTest(value=value):
                self.registry['invariants'][0]['documents'] = [value]
                self.save()
                with self.assertRaises(check.Invalid):
                    check.validate(self.root)

    def test_missing_id_field(self):
        del self.registry['invariants'][0]['id']
        self.save()
        with self.assertRaisesRegex(check.Invalid, 'invalid invariant fields'):
            check.validate(self.root)

    def test_minor_addition(self):
        entry = copy.deepcopy(self.registry['invariants'][-1])
        entry['id'] = 'QM-INV-025'
        self.registry['invariants'].append(entry)
        self.save()
        with self.assertRaisesRegex(check.Invalid, 'minor version'):
            check.validate(self.root)
        self.registry['registry_version'] = '1.1.0'
        self.save()
        self.refresh()
        self.assertEqual(len(check.validate(self.root)['invariants']), 25)

    def test_major_bump_does_not_bypass_history(self):
        self.registry['registry_version'] = '2.0.0'
        self.save()
        with self.assertRaisesRegex(check.Invalid, 'major-version migration'):
            check.validate(self.root)

    def test_unregistered_block(self):
        path = self.root / 'UNREGISTERED.md'
        path.write_text(check.render_block(self.registry, check.CORE))
        with self.assertRaisesRegex(check.Invalid, 'unregistered controlled block'):
            check.validate(self.root)

    def test_unmarked_prose_is_explicitly_out_of_scope(self):
        path = self.root / 'README.md'
        path.write_text(path.read_text() + '\nAn ordinary prose edit.\n')
        check.validate(self.root)

    def test_cli_error(self):
        (self.root / check.REGISTRY).write_text('{')
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            self.assertEqual(check.main(['--root', str(self.root)]), 1)
        self.assertIn('invariant check failed', stderr.getvalue())

    def test_reversed_markers(self):
        path = self.root / check.CORE
        text = path.read_text().replace(check.BEGIN, 'TEMP').replace(check.END, check.BEGIN).replace('TEMP', check.END)
        path.write_text(text)
        with self.assertRaisesRegex(check.Invalid, 'reversed controlled block'):
            check.validate(self.root)


if __name__ == '__main__':
    unittest.main()
