#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from tick_project import settings

ran = False


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tick_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    if not ran:
        ran = True
        print("Do you want to allow a host?(Yes/No)")
        ans = input()
        if ans == "Yes":
            settings.ALLOWED_HOSTS.append(input())
    main()
