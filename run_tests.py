#!/usr/bin/env python
import os
import subprocess
import sys


def install_dependencies():
    print("\nInstalling test dependencies...\n")

    try:
        subprocess.check_output("pip install -r test_requirements.txt", shell=True,
                                stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        print("ERROR: Test dependency installation failed.\n{}\n".format(exc.output.decode()))
        return False
    else:
        print("Test dependency installation successful.\n")

    return True


def run_django_tests():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_test_app.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv + ['test'])


if __name__ == '__main__':
    if install_dependencies():
        run_django_tests()
