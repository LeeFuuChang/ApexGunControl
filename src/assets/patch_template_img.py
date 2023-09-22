patch_template_img_byte = b'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'
