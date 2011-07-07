import os

from django.conf import settings
from django.test import simple

def run_tests(test_labels, verbosity=1, interactive=True, extra_tests=[]):

    try:
        import settings_test
    except:
        pass
    else:
        for setting in dir(settings_test):
            if setting == setting.upper():
                setattr(settings, setting, getattr(settings_test, setting))

    return simple.run_tests(test_labels, verbosity, interactive, extra_tests)