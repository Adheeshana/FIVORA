"""
Simple runner to launch `DashboardScreen` for local testing.
"""
import sys
import os
import importlib.util
from PyQt5.QtWidgets import QApplication


def import_dashboard_screen():
    proj_root = os.path.dirname(__file__)
    module_path = os.path.join(proj_root, "screens", "dashboard_screen.py")
    spec = importlib.util.spec_from_file_location("dashboard_screen", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.DashboardScreen


def main():
    DashboardScreen = import_dashboard_screen()
    app = QApplication(sys.argv)
    dummy_user = {"full_name": "Test User"}
    window = DashboardScreen(dummy_user)
    window.setWindowTitle("Dashboard - FIVORA (Test)")
    window.resize(1000, 700)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
