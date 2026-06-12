with open("render/__init__.py", "r") as f:
    text = f.read()

text = text.replace("finding.get(\"adapter_error_cause\", [])", "finding.adapter_error_cause")
text = text.replace("finding.get('title', '')", "finding.title")
text = text.replace('    return finding.confidence == "high" or finding.mode == "deterministic"', '    if finding.status == "unknown":\n        return False\n    return finding.confidence == "high" or finding.mode == "deterministic"')

with open("render/__init__.py", "w") as f:
    f.write(text)
