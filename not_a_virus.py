#!/usr/bin/env python3

import os
import subprocess
import sys

def ensure_applications_symlink():
    """
    Ensure that ~/Applications points to /Applications.
    If ~/Applications already exists as a directory (not a symlink),
    it will be renamed to ~/Applications.bak.<pid>.
    """
    home = os.path.expanduser("~")
    user_apps = os.path.join(home, "Applications")
    system_apps = "/Applications"

    print(f"[INFO] Checking ~/Applications at {user_apps}")

    if os.path.islink(user_apps):
        # Already a symlink
        target = os.readlink(user_apps)
        if target == system_apps:
            print("[OK] ~/Applications already points to /Applications")
            return
        else:
            print(f"[WARN] ~/Applications points somewhere else: {target}")
            os.remove(user_apps)
            print("[INFO] Removed bad symlink.")

    elif os.path.isdir(user_apps):
        # Real directory, not a link
        backup = user_apps + f".bak.{os.getpid()}"
        os.rename(user_apps, backup)
        print(f"[WARN] Moved existing ~/Applications to {backup}")

    elif os.path.exists(user_apps):
        # Some weird file
        backup = user_apps + f".bak.{os.getpid()}"
        os.rename(user_apps, backup)
        print(f"[WARN] Moved existing file ~/Applications to {backup}")

    # Now create the symlink
    os.symlink(system_apps, user_apps)
    print(f"[OK] Created symlink: {user_apps} -> {system_apps}")


def launch_app(app_name):
    """
    Launch the app by name inside ~/Applications using `open`.
    Returns the process PID once found.
    """
    app_path = os.path.expanduser(f"~/Applications/{app_name}<extension>")
    if not os.path.exists(app_path):
        print(f"[ERROR] Could not find {app_path}")
        sys.exit(1)

    print(f"[INFO] Launching {app_path}")
    subprocess.run(["open", app_path])

    # Poll for PID
    pid = None
    for _ in range(20):
        try:
            pid_list = subprocess.check_output(
                ["pgrep", "-fl", app_name],
                text=True
            ).strip().splitlines()
            for line in pid_list:
                if app_name in line:
                    pid = int(line.split()[0])
                    break
            if pid:
                break
        except subprocess.CalledProcessError:
            pass
        import time; time.sleep(1)

    if pid:
        print(f"[OK] Found PID for {app_name}: {pid}")
        return pid
    else:
        print("[ERROR] Could not find PID after launch attempts.")
        sys.exit(1)


if __name__ == "__main__":
    ensure_applications_symlink()
    pid = launch_app("<application>")
    print(f"[INFO] Ready to attach monitoring tools to PID {pid}")
