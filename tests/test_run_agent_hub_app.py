from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "skills/run-agent-hub-app/scripts/run_agent_hub_app.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("run_agent_hub_app_tests", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["run_agent_hub_app_tests"] = module
    spec.loader.exec_module(module)
    return module


runner = load_runner()


class RunAgentHubAppTests(unittest.TestCase):
    def test_background_server_prefers_live_dashboard_serve_command(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = root / "repo"
            viewer_dir = root / "viewer"
            run_dir = root / "runtime"
            agent_hub_script = root / "skills/manage-agent-hub-issues/scripts/agent_hub.py"
            repo.mkdir()
            viewer_dir.mkdir()
            run_dir.mkdir()
            agent_hub_script.parent.mkdir(parents=True)
            agent_hub_script.write_text("# cli\n", encoding="utf-8")

            with mock.patch.object(runner.subprocess, "Popen") as popen:
                popen.return_value.pid = 123
                process = runner.start_background_server(
                    "127.0.0.1",
                    8765,
                    viewer_dir,
                    run_dir,
                    repo,
                    "live-change",
                    agent_hub_script,
                )

        self.assertIs(process, popen.return_value)
        command = popen.call_args.args[0]
        self.assertEqual(command[:5], [sys.executable, str(agent_hub_script), "--repo", str(repo), "dashboard"])
        self.assertIn("serve", command)
        self.assertIn("--change", command)
        self.assertIn("live-change", command)
        self.assertNotIn("http.server", command)

    def test_reused_live_server_is_detected_by_state_api(self):
        state = {
            "version": "3",
            "columns": [],
            "summary": {},
            "revision": {"id": "rev-1"},
        }
        body = runner.json.dumps(state).encode("utf-8")

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return body

        with mock.patch.object(runner.urllib.request, "urlopen", return_value=Response()) as urlopen:
            self.assertTrue(runner.serves_hub_snapshot("127.0.0.1", 8765))

        self.assertEqual(urlopen.call_args.args[0], "http://127.0.0.1:8765/api/state")


if __name__ == "__main__":
    unittest.main()
