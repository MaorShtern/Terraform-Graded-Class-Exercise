import sys
import jinja2
from modules.terraform_renderer import TerraformRenderer
from python_terraform import Terraform, IsFlagged


ami_options = {
    "ubuntu": "ami-0c995fbcf99222492",
    "amazon linux": "ami-0915e09cc7ceee3ab"
}



def Get_User_Variables():
    # --- AMI selection ---
    ami_choice = input("Choose between Ubuntu or Amazon Linux: ").strip().lower()
    if ami_choice == "ubuntu":
        ami_choice = ami_options[ "ubuntu"]
    elif ami_choice in ["amazon linux", "linux"]:
        ami_choice = ami_options["amazon linux"]
    else:
        print("❌ You must choose either 'Ubuntu' or 'Amazon Linux'!")
        sys.exit(1)

    # --- Instance type selection ---
    instance_type_choice = input("Choose instance type (t3.small / t3.medium): ").strip()
    if instance_type_choice == "t3.small":
        instance_type_choice = "t3.small"
    elif instance_type_choice == "t3.medium":
        instance_type_choice = "t3.medium"
    else:
        print("❌ You must choose either 't3.small' or 't3.medium'!")
        sys.exit(1)

    # --- Region selection ---
    region = input("Select region (only 'us-east-1' is allowed, others will be defaulted): ").strip()
    if region != "us-east-1":
        print(f"⚠️ Region '{region}' is not allowed. Defaulting to 'us-east-1'.")
        region = "us-east-1"


    # --- Load Balancer name ---
    alb_name = input("Enter a name for your Load Balancer (ALB): ").strip()
    print("\n✅ Summary of your configuration:")
    print(f"  AMI:            {ami_choice}")
    print(f"  Instance Type:  {instance_type_choice}")
    print(f"  Region:         {region}")
    print(f"  ALB Name:       {alb_name}")

    # --- Store all values in a dictionary ---
    context = {
        "ami": ami_choice,
        "instance_type": instance_type_choice,
        "region": region,
        "availability_zone": "us-east-1a",  # used by EC2 instance
        "availability_zones": ["us-east-1a", "us-east-1b"],  # used by subnets
        "load_balancer_name": alb_name
    }

    print("\n✅ Configuration collected successfully!")
    print("Context to pass into Jinja2 template:")
    print(context)

    # --- Jinja2 template usage ---
    template_str = """
          resource "aws_instance" "example" {
            ami         = "{{ ami }}"
            instance_type = "{{ instance_type }}"
            region        = "{{ region }}"
          }

          resource "aws_lb" "example" {
            name               = "{{ alb_name }}"
            internal           = false
            load_balancer_type = "application"
            subnets            = ["subnet-xyz"]  # Replace with real subnet IDs
          }
          """

    # Render the template
    try:
        template = jinja2.Template(template_str)
        rendered_output = template.render(context)

        print("\n📄 Rendered Terraform Configuration:")
        print(rendered_output)
        return context

    except jinja2.exceptions.TemplateError as e:
        print("\n❌ Jinja2 template rendering failed!")
        print(f"Error: {e}")


def write_to_file(content, path):
    with open(path, "w") as f:
        f.write(content)



def run_terraform():
    tf = Terraform(working_dir='terraform')

    print("\n=== Running terraform init ===")
    rc, out, err = tf.init(capture_output=False)
    if err and err.strip() != "":
        print(f" Init failed:\n{err}")
        sys.exit(1)

    print("\n=== Running terraform plan ===")
    rc, out, err = tf.plan(capture_output=False)
    if err and err.strip() != "":
        print(f" Plan failed:\n{err}")
        sys.exit(1)

    print("\n=== Running terraform apply ===")
    rc, out, err = tf.apply(
        skip_plan=True,
        capture_output=False,
        auto_approve=True,
        no_color=IsFlagged,
        lock=False 
    )
    if err and err.strip() != "":
        print(f" Apply failed:\n{err}")
        sys.exit(1)

    print("\n Terraform apply completed successfully.")



   
def get_outputs():
    try:
        tf = Terraform(working_dir='terraform')
        outputs = tf.output()
        parsed_outputs = {}

        print("\n=== Terraform Outputs ===")
        for key, val in outputs.items():
            value = val.get("value", "N/A")
            parsed_outputs[key] = value
            print(f"{key}: {value}")

        return parsed_outputs

    except Exception as e:
        print(f"\n Failed to fetch outputs: {str(e)}")




if __name__ == '__main__':

    try:
        print("Build a Python-based AWS Infrastructure as Code (IaC) tool!")
        print("Please enter the following details to create your infrastructure.\n")

        context = Get_User_Variables()

        renderer = TerraformRenderer()
        renderer.render(context)

        run_terraform()
        get_outputs()


    except Exception as e:
        print(f"\n Unexpected error: {str(e)}")
        sys.exit(1)






