input_file = "google.list"
output_file = "google.yaml"

with open(input_file, "r", encoding="utf-8") as fin, open(
    output_file, "w", encoding="utf-8"
) as fout:
    fout.write("payload:\n")
    for line in fin:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("DOMAIN,"):
            domain = line.split(",", 1)[1].strip()
            fout.write(f"- '{domain}'\n")
        elif line.startswith("DOMAIN-SUFFIX,"):
            domain = line.split(",", 1)[1].strip()
            fout.write(f"- '+.{domain}'\n")
