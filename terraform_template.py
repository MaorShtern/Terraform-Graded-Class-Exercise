import jinja2

# Extract user inputs from the context dictionary
ami_options = {
    "ubuntu": "ami-0abcdef1234567890",
    "amazon linux": "ami-0fedcba9876543210"
}

instance_types = {
    "t3.small": "t3.small",
    "t3.medium": "t3.medium"
}

terraform_template = """

    provider "aws" {
    region = "{{ region }}"
    }

    resource "aws_instance" "web_server" {
     ami = "{{ ami }}"
     instance_type = "{{ instance_type }}"
     subnet_id         = aws_subnet.public[0].id
     availability_zone = "{{ availability_zone }}"
     vpc_security_group_ids = [aws_security_group.lb_sg.id]

     tags = {
       Name = "WebServer"
     }
    }

    resource "aws_lb" "application_lb" {
     name = "{{ load_balancer_name }}"
     internal = false
     load_balancer_type = "application"
     security_groups = [aws_security_group.lb_sg.id]
     subnets = aws_subnet.public[*].id
    }

    resource "aws_security_group" "lb_sg" {
     name        = "lb_security_group"
     description = "Allow HTTP inbound traffic"
     vpc_id      = aws_vpc.main.id

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

    resource "aws_lb_listener" "http_listener" {
     load_balancer_arn = aws_lb.application_lb.arn
     port              = 80
     protocol          = "HTTP"

     default_action {
       type             = "forward"
       target_group_arn = aws_lb_target_group.web_target_group.arn
     }
    }

    resource "aws_lb_target_group" "web_target_group" {
     name     = "web-target-group"
     port     = 80
     protocol = "HTTP"
     vpc_id   = aws_vpc.main.id

     health_check {
        healthy_threshold   = 2
        unhealthy_threshold = 2
        timeout             = 5
        interval            = 30
        path                = "/"
        protocol            = "HTTP"
     }
    }

    resource "aws_lb_target_group_attachment" "web_instance_attachment" {
     target_group_arn = aws_lb_target_group.web_target_group.arn
     target_id        = aws_instance.web_server.id
     port             = 80
    }

    resource "aws_subnet" "public" {
     count = 2
     vpc_id = aws_vpc.main.id
     cidr_block = "10.0.${count.index}.0/24"
     availability_zone = element(["us-east-1a", "us-east-1b"], count.index)
    }


    resource "aws_vpc" "main" {
     cidr_block = "10.0.0.0/16"
    }
    
    output "instance_id" {
      value = aws_instance.web_server.id
    }
    
    output "lb_dns_name" {
      value = aws_lb.application_lb.dns_name
    }

"""


def render_template(context):
    ami = ami_options.get(context["ami"].lower(), "ami-?????")
    instance_type = instance_types.get(context["instance_type"].lower(), "t3.small")

    template_context = {
        "ami": ami,
        "instance_type": instance_type,
        "region": context["region"],
        "availability_zone": context.get("availability_zone", "us-east-1a"),
        "load_balancer_name": context["alb_name"]
    }

    # # Either inline the template or load from file
    # with open("templates/main.tf.j2") as f:
    #     terraform_template = f.read()

    # template = jinja2.Template(terraform_template)
    # return template.render(template_context)