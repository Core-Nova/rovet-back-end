import argparse
import os
import shutil
import subprocess
import sys
import venv
import getpass
from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent


# ───────────────────────────────────────────────────────────────
#  OS / Dependency helpers
# ───────────────────────────────────────────────────────────────

def is_debian_or_ubuntu():
    """Detect Debian/Ubuntu-based systems."""
    if os.path.exists("/etc/os-release"):
        with open("/etc/os-release") as f:
            content = f.read().lower()
            return ("debian" in content) or ("ubuntu" in content)
    return False


def running_in_ci():
    """Detect if running inside a CI system like GitHub Actions."""
    return os.environ.get("CI", "").lower() == "true"

def ensure_system_dependencies():
    """
    Ensure python3-venv and python3-pip are installed on Debian/Ubuntu.
    Behaves differently in CI environments (non-interactive).
    """
    if not is_debian_or_ubuntu():
        return

    print("Detected Debian/Ubuntu system. Checking system dependencies...")

    missing = []

    # Check python3-venv
    if subprocess.call(
        ["dpkg", "-s", "python3-venv"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ) != 0:
        missing.append("python3-venv")

    # Check python3-pip
    if subprocess.call(
        ["dpkg", "-s", "python3-pip"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ) != 0:
        missing.append("python3-pip")

    if not missing:
        return

    # ─────────────────────────────────────────
    # CI MODE: Fast fail — no interaction allowed
    # ─────────────────────────────────────────
    if running_in_ci():
        print(
            "\n❌ Missing required system packages in CI environment:\n"
            f"    {' '.join(missing)}\n\n"
            "CI mode does not support sudo installation. "
            "Please install these packages in your CI workflow BEFORE running this script.\n"
        )
        sys.exit(1)

    # ─────────────────────────────────────────
    # LOCAL MODE: Try root/non-sudo first
    # ─────────────────────────────────────────
    print(f"Missing packages: {', '.join(missing)}")

    try:
        print("Attempting installation without sudo (root/CI containers)...")
        subprocess.check_call(["apt-get", "update"])
        subprocess.check_call(["apt-get", "install", "-y"] + missing)
        print("System packages installed without sudo.")
        return
    except Exception:
        print("Non-sudo installation failed or permission denied.")

    # ─────────────────────────────────────────
    # LOCAL MODE: sudo with password prompt
    # ─────────────────────────────────────────

    print("Sudo password required to install system packages.")
    password = getpass.getpass("Enter sudo password: ")

    def sudo_run(cmd):
        proc = subprocess.run(
            ["sudo", "-S"] + cmd,
            input=(password + "\n").encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if proc.returncode != 0:
            print(f"❌ sudo command failed: {' '.join(cmd)}")
            print(proc.stderr.decode())
            sys.exit(1)

    print("Installing packages with sudo...")

    sudo_run(["apt-get", "update"])
    sudo_run(["apt-get", "install", "-y"] + missing)

    print("System dependencies installed successfully.")



# ───────────────────────────────────────────────────────────────
#  Virtual Environment & Requirements
# ───────────────────────────────────────────────────────────────

def create_venv(venv_dir):
    if os.path.exists(venv_dir):
        print(f"Virtual environment '{venv_dir}' already exists. Skipping creation.")
        return

    # Ensure OS-level Python deps exist (Debian/Ubuntu)
    ensure_system_dependencies()

    print("Creating virtual environment...")
    venv.create(venv_dir, with_pip=True)


def install_requirements(venv_dir):
    py = _venv_python(venv_dir)

    print("Upgrading pip...")
    subprocess.check_call([py, "-m", "pip", "install", "--upgrade", "pip"])

    script_dir = os.path.dirname(os.path.abspath(__file__))
    req_path = os.path.join(script_dir, "requirements", "requirements.txt")

    print(f"Installing requirements from: {req_path}")
    subprocess.check_call([py, "-m", "pip", "install", "-r", req_path])


def _venv_python(venv_dir):
    """Returns full path to the Python executable inside the venv."""
    if os.name == "nt":
        return os.path.join(venv_dir, "Scripts", "python.exe")
    return os.path.join(venv_dir, "bin", "python")


# ───────────────────────────────────────────────────────────────
#  Main
# ───────────────────────────────────────────────────────────────

def main():
    in_ci = running_in_ci()

    if in_ci:
        print("Running in CI mode (CI=true). Interactive sudo prompts disabled.")

    parser = argparse.ArgumentParser(description="Setup project virtual environment")
    parser.add_argument("--clean", action="store_true", help="Delete existing venv and rebuild")
    args = parser.parse_args()

    venv_name = "venv"
    venv_dir = f"{PROJECT_ROOT}/{venv_name}"

    if args.clean and os.path.exists(venv_dir):
        print("--clean specified: removing existing virtual environment...")
        shutil.rmtree(venv_dir)
        print("Existing virtual environment removed.")

    create_venv(venv_dir)
    install_requirements(venv_dir)

    print("\n✔ Virtual environment set up successfully.")


if __name__ == "__main__":
    main()
