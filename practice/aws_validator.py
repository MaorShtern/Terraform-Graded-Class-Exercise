import boto3
import json
from python_terraform import Terraform
import sys



def get_terraform_outputs(terraform_dir):
    tf = Terraform(working_dir=terraform_dir)
    return_code, outputs, stderr = tf.output()
    if return_code != 0:
        print("❌ Failed to get Terraform outputs.")
        print(stderr)
        sys.exit(1)
    return outputs

def validate_resources(terraform_dir):
    outputs = get_terraform_outputs(terraform_dir)

    # Extract outputs
    instance_id = outputs.get("instance_id", {}).get("value")
    alb_dns_name = outputs.get("lb_dns_name", {}).get("value")

    if not instance_id:
        sys.exit("❌ instance_id not found in Terraform output.")

    ec2 = boto3.client("ec2")
    elbv2 = boto3.client("elbv2")

    # Get EC2 instance details
    print(f"🔍 Validating EC2 instance: {instance_id}")
    ec2_resp = ec2.describe_instances(InstanceIds=[instance_id])
    reservations = ec2_resp.get("Reservations", [])
    instance_info = reservations[0]["Instances"][0] if reservations else None

    if not instance_info:
        sys.exit("❌ EC2 instance not found.")

    instance_state = instance_info["State"]["Name"]
    public_ip = instance_info.get("PublicIpAddress", "N/A")

    # Get ALB details by DNS name
    print(f"🔍 Validating ALB DNS: {alb_dns_name}")
    alb_resp = elbv2.describe_load_balancers()
    load_balancers = alb_resp.get("LoadBalancers", [])

    alb_found = next((lb for lb in load_balancers if lb["DNSName"] == alb_dns_name), None)

    if not alb_found:
        sys.exit("❌ Load Balancer not found.")

    # Prepare output
    result = {
        "instance_id": instance_id,
        "instance_state": instance_state,
        "public_ip": public_ip,
        "load_balancer_dns": alb_dns_name
    }

    # Save to file
    with open("aws_validation.json", "w") as f:
        json.dump(result, f, indent=4)

    print("\n✅ AWS validation complete. Results saved to aws_validation.json.")
    print(json.dumps(result, indent=4))


