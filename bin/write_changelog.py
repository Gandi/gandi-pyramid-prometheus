#!/usr/bin/env python3
import datetime

import gandi_pyramid_prometheus

header = (
    f"{gandi_pyramid_prometheus.__version__} - "
    f"Released on {datetime.datetime.now().date().isoformat()}"
)
with open("CHANGES.rst.new", "w") as changelog:
    changelog.write(header)
    changelog.write("\n")
    changelog.write("-" * len(header))
    changelog.write("\n")
    changelog.write("* please write here \n\n")
