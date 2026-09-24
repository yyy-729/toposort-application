from __future__ import annotations

import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path


class LauncherTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "Windows 批处理测试只在 Windows 运行")
    def test_chinese_launcher_starts_application_without_error(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        if not (project_root / ".venv" / "Scripts" / "pythonw.exe").exists():
            self.skipTest("需要先运行 install_dependencies.bat 创建独立环境")
        environment = os.environ.copy()
        environment["QT_QPA_PLATFORM"] = "offscreen"
        environment["TOPOSORT_AUTO_CLOSE_MS"] = "350"
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "app_ready.txt"
            environment["TOPOSORT_STARTUP_READY_FILE"] = str(marker)
            started = time.monotonic()
            completed = subprocess.run(
                ["cmd.exe", "/d", "/c", "启动应用.bat"],
                cwd=project_root,
                env=environment,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=12,
                check=False,
            )
            self.assertEqual(
                completed.returncode,
                0,
                msg=f"stdout={completed.stdout}\nstderr={completed.stderr}",
            )
            self.assertLess(time.monotonic() - started, 12)
            deadline = time.monotonic() + 30
            while not marker.exists() and time.monotonic() < deadline:
                time.sleep(0.1)
            self.assertTrue(marker.exists(), "启动器退出后，应用主窗口没有打开")

    @unittest.skipUnless(os.name == "nt", "Windows 启动测试只在 Windows 运行")
    def test_windowless_launcher_opens_main_window(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        if not (project_root / ".venv" / "Scripts" / "pythonw.exe").exists():
            self.skipTest("需要先运行 install_dependencies.bat 创建独立环境")
        environment = os.environ.copy()
        environment["QT_QPA_PLATFORM"] = "offscreen"
        environment["TOPOSORT_AUTO_CLOSE_MS"] = "350"
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "app_ready.txt"
            environment["TOPOSORT_STARTUP_READY_FILE"] = str(marker)
            completed = subprocess.run(
                ["wscript.exe", str(project_root / "launcher.vbs")],
                cwd=project_root,
                env=environment,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=12,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, msg=completed.stderr)
            deadline = time.monotonic() + 30
            while not marker.exists() and time.monotonic() < deadline:
                time.sleep(0.1)
            self.assertTrue(marker.exists(), "无终端启动后，应用主窗口没有打开")


if __name__ == "__main__":
    unittest.main()
