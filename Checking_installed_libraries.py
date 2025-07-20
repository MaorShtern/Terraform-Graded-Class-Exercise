from python_terraform import Terraform
import jinja2



if __name__ == "__main__":
    tf = Terraform()
    print(tf)
    template = jinja2.Template("Hello, {{ name }}!")
    output = template.render(name="Maor")

    print(output)

    # You must give Boto3 access to your AWS account.
    # boto3 --> aws configure
    # AWS Access Key ID
    # AWS Secret Access Key
    # Default region (like us-east-1)
    # Output format (optional, like json)