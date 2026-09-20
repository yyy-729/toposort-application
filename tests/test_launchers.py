from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path


class LauncherTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "Windows 批处理测试只在 Windows 运行")
    def test_chinese_launcher_starts_application_without_error(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        if not (project_root / ".venv" / "Scripts" / "python.exe").exists():
            self.skipTest("需要先运行 install_dependencies.bat 创建独立环境")
        environment = os.environ.copy()
        environment["QT_QPA_PLATFORM"] = "offscreen"
        environment["TOPOSORT_AUTO_CLOSE_MS"] = "350"

        completed = subprocess.run(
            ["cmd.exe", "/d", "/c", "启动应用.bat"],
            cwd=project_root,
            env=environment,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=45,
            check=False,
        )

        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout={completed.stdout}\nstderr={completed.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
