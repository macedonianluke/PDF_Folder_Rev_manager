import sys
import os

sys.path.insert(0, 'scripts')

from update_transmittal_matrix_refactored import create_transmittal_template
import config

output_path = config.DEFAULT_TEMPLATE_NAME

print(f"Creating new template: {config.DEFAULT_TEMPLATE_NAME}")
doc = create_transmittal_template()

doc.save(output_path)

print(f"Successfully created template file at: {output_path}")
