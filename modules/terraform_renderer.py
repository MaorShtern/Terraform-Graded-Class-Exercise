from jinja2 import Template
import os

class TerraformRenderer:
    def __init__(self):
        self.template_str = self._load_template()

    def _load_template(self):
        return """
provider "aws" {
  region = "{{ region }}"
}

# Create a VPC
resource "aws_vpc" "main_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "main_vpc"
  }
}

# Create two subnets
resource "aws_subnet" "subnet_a" {
  vpc_id                  = aws_vpc.main_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "{{ availability_zone }}"
  map_public_ip_on_launch = true

  tags = {
    Name = "subnet_a"
  }
}

resource "aws_subnet" "subnet_b" {
  vpc_id                  = aws_vpc.main_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "{{ availability_zone }}"
  map_public_ip_on_launch = true

  tags = {
    Name = "subnet_b"
  }
}

# Security Group
resource "aws_security_group" "lb_sg" {
  name        = "lb_security_group_{{ load_balancer_name }}"
  description = "Allow HTTP inbound traffic"
  vpc_id      = aws_vpc.main_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance
resource "aws_instance" "web_server" {
  ami                    = "{{ ami_id }}"
  instance_type          = "{{ instance_type }}"
  availability_zone      = "{{ availability_zone }}"
  subnet_id              = aws_subnet.subnet_a.id
  vpc_security_group_ids = [aws_security_group.lb_sg.id]

  tags = {
    Name = "WebServer"
  }
}

# Load Balancer
resource "aws_lb" "application_lb" {
  name               = "{{ load_balancer_name }}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb_sg.id]
  subnets            = [aws_subnet.subnet_a.id, aws_subnet.subnet_b.id]
}

resource "aws_lb_target_group" "web_target_group" {
  name     = "web-target-group-{{ load_balancer_name }}"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main_vpc.id
}

resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_lb.application_lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web_target_group.arn
  }
}

resource "aws_lb_target_group_attachment" "web_instance_attachment" {
  target_group_arn = aws_lb_target_group.web_target_group.arn
  target_id        = aws_instance.web_server.id
}

output "instance_id" {
  value = aws_instance.web_server.id
}

output "load_balancer_dns" {
  value = aws_lb.application_lb.dns_name
}
"""

    def render(self, context: dict, output_path="terraform/generated.tf"):
        try:
            template = Template(self.template_str)
            rendered = template.render(**context)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as f:
                f.write(rendered)

            print(f"Terraform config written to {output_path}")
        except Exception as e:
            print(f"Error rendering Terraform config: {str(e)}")

            