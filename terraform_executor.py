

import os
from python_terraform import Terraform
import sys



def execute_terraform(tf_content, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        f.write(tf_content)
    print(f"✅ Terraform config written to {output_path}")

    tf = Terraform(working_dir=os.path.dirname(output_path))

    print("\n🔧 terraform init")
    code, _, err = tf.init(capture_output=False)
    if code != 0:
        sys.exit(f"❌ Init failed:\n{err}")

    print("\n📝 terraform plan")
    code, out, err = tf.plan(capture_output=True)
    print(out)
    if code != 0:
        sys.exit(f"❌ Plan failed:\n{err}")

    print("\n🚀 terraform apply")
    code, out, err = tf.apply(skip_plan=True, capture_output=True)
    print(out)
    if code != 0:
        sys.exit(f"❌ Apply failed:\n{err}")

    print("\n📦 terraform output")
    code, output, err = tf.output()
    if code == 0:
        for k, v in output.items():
            print(f"{k}: {v['value']}")
    else:
        print("⚠️ Failed to fetch output:", err)

