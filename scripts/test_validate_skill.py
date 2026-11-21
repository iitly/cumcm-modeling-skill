"""Regression tests for the skill validator, using disposable copied fixtures.
Run with: python -B scripts/test_validate_skill.py
These test mechanical checks, not model or scientific correctness.
"""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ACTIVE = Path(__file__).resolve().parents[1]
SCRATCH = Path(os.environ.get('HERMES_HOME', str(Path.home()/'.hermes')))/'cache'/'scratch'

class ValidatorRegression(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='mathmodel-validator-', dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'skill'
        shutil.copytree(ACTIVE, self.root, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))

    def run_checker(self):
        run = subprocess.run([sys.executable, '-B', str(self.root/'scripts/validate_skill.py')],
                             capture_output=True, text=True, encoding='utf-8')
        self.assertTrue(run.stdout.strip().startswith('{'), run.stderr)
        return run, json.loads(run.stdout)

    def append(self, rel, text):
        path = self.root/rel
        path.write_text(path.read_text(encoding='utf-8')+text, encoding='utf-8')

    def assert_rejected(self, diagnostic):
        run, data = self.run_checker()
        self.assertNotEqual(run.returncode, 0, run.stdout)
        self.assertFalse(data['ok'])
        self.assertIn(diagnostic, '\n'.join(data['problems']))

    def test_healthy_copy_passes(self):
        run, data = self.run_checker()
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertTrue(data['ok'])

    def test_missing_link_in_reference_is_rejected(self):
        self.append('references/model-validation.md', '\n`references/does_not_exist.md`\n')
        self.assert_rejected('broken link: references/does_not_exist.md')

    def test_active_bad_rule_in_meta_file_is_rejected(self):
        self.append('references/maintenance-decisions.md', '\n## 执行要求\n国一 ≥10 张图。\n')
        self.assert_rejected('forbidden phrase')

    def test_unclosed_code_fence_is_rejected(self):
        self.append('references/model-validation.md', '\n```python\nprint(1)\n')
        self.assert_rejected('unclosed code fence')

    def test_invalid_python_is_rejected(self):
        (self.root/'scripts/broken_demo.py').write_text('def broken(:\n    pass\n', encoding='utf-8')
        self.append('SKILL.md', '\n`scripts/broken_demo.py`\n')
        self.assert_rejected('invalid Python: scripts/broken_demo.py')

    def test_internal_path_escape_is_rejected(self):
        (self.root.parent/'outside.md').write_text('outside fixture', encoding='utf-8')
        self.append('SKILL.md', '\n`references/../../outside.md`\n')
        self.assert_rejected('internal link escapes skill root')

    def test_unbalanced_example_marker_is_rejected(self):
        self.append('references/maintenance-decisions.md', '\n<!-- examples:start -->\n')
        self.assert_rejected('unbalanced example region')

if __name__ == '__main__':
    unittest.main(verbosity=2)
