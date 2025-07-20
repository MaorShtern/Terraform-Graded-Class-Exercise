# AWS IaC Tool (Python + Terraform)

A Python-based Infrastructure as Code (IaC) tool for provisioning an **EC2 instance** behind an **Application Load Balancer (ALB)** on AWS using **Terraform**, with dynamic template generation via **Jinja2**, execution via `python-terraform`, and post-deployment validation using `boto3`.

---

## 📦 Features

- 🔧 **Terraform template generation** using Jinja2
- 🚀 **Terraform execution** (`init`, `plan`, `apply`, `destroy`) using `python-terraform`
- ✅ **Post-deployment validation** of EC2 and ALB via `boto3`
- 💡 **Modular Python design** with clean error handling and function-based structure
- 🌩️ Configurable input for region, AMI, instance type, ALB name, and more

---

## 🛠️ Prerequisites

- Python 3.7+
- Terraform CLI installed and added to system PATH
- AWS credentials set via one of the following:
  - `~/.aws/credentials` file
  - Environment variables
  - IAM role (if running on EC2)

---

## 📚 Installation

Clone the repo and install required Python libraries:

```bash
git clone https://github.com/your-username/aws-iac-tool.git
cd aws-iac-tool
pip install -r requirements.txt
