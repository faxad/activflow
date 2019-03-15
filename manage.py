#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    SETTINGS = "activflow.settings.development"

    if os.environ.get("ENV", None) == "staging":
        SETTINGS = "activflow.settings.staging"
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
