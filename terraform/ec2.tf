# ec2.tf

variable "BACKEND_EC2_INSTANCE_TYPE" {
  type    = string
  default = "t3.micro"
}

variable "BACKEND_EC2_SSH_KEY_NAME" {
  type        = string
  description = "Existing EC2 keypair name for SSH into instance"
}

variable "AWS_ACCOUNT_NUMBER" {
  type = string
}

# This is also the name of the AWS ECR repository
variable "BACKEND_IMAGE_NAME" {
  type    = string
  default = "einsingen-backend"
}

variable "BACKEND_IMAGE_TAG" {
  type    = string
  default = "latest"
}

variable "DJANGO_PORT" {
  type    = string
  default = "8000"
}

variable "DEFAULT_VPC_ID" {
  type = string
}

variable "PGDATABASE" {
  type = string

}

variable "PGHOST" {
  type      = string
  sensitive = true
}

variable "PGPASSWORD" {
  type      = string
  sensitive = true
}

variable "PGPORT" {
  type    = string
  default = "5432"
}

variable "PGUSER" {
  type    = string
  default = "postgres"
}


locals {
  ECR_REPO_URL = "${replace(var.AWS_ACCOUNT_NUMBER, "-", "")}.dkr.ecr.${var.AWS_REGION}.amazonaws.com/${var.BACKEND_IMAGE_NAME}"
}
# -----------------------------------------------------------------------------
locals {
  user_data = templatefile("${path.module}/user_data.yaml", {
    AWS_REGION        = var.AWS_REGION,
    ECR_REPO_URL      = local.ECR_REPO_URL,
    BACKEND_IMAGE_TAG = var.BACKEND_IMAGE_TAG,
    DJANGO_PORT       = var.DJANGO_PORT,
    PGDATABASE        = var.PGDATABASE,
    PGHOST            = var.PGHOST,
    PGPASSWORD        = var.PGPASSWORD,
    PGPORT            = var.PGPORT,
    PGUSER            = var.PGUSER,
  })
  user_data_str = <<-EOF
#cloud-config
    
groups:
  - docker

package_update: true
package_upgrade: true

write_files:
  - path: /usr/local/bin/on-shutdown.sh
    permissions: "0755"
    content: |
      #!/bin/bash
      echo "$(date) shutting down..." >> /var/log/shutdown.log
      docker ps -q | xargs --no-run-if-empty /usr/bin/docker stop

  - path: /etc/systemd/system/on-shutdown.service
    permissions: "0644"
    content: |
      [Unit]
      Description=Run script on EC2 shutdown
      DefaultDependencies=no
      Before=shutdown.target reboot.target halt.target

      [Service]
      Type=oneshot
      ExecStart=/usr/local/bin/on-shutdown.sh

      [Install]
      WantedBy=halt.target reboot.target shutdown.target

  - path: /var/lib/cloud/scripts/per-instance/01_load_env_vars.sh
    permissions: "0644"
    content: |
      #!/bin/bash
      export AWS_REGION='${var.AWS_REGION}'
      export ECR_REPO_URL='${local.ECR_REPO_URL}'
      export IMAGE_TAG='${var.BACKEND_IMAGE_TAG}'
      export CONTAINER_PORT='${var.DJANGO_PORT}'

  - path: /var/lib/cloud/scripts/per-instance/02_setup_docker.sh
    permissions: "0755"
    content: |
      #!/bin/bash
      dnf update -y
      dnf install -y docker
      systemctl enable docker
      systemctl start docker
      # Add ec2-user to the docker group
      usermod -aG root,docker ec2-user
      newgrp docker
      systemctl daemon-reload
      systemctl enable on-shutdown.service

  - path: /var/lib/cloud/scripts/per-instance/03_run_container.sh
    permissions: "0755"
    content: |
      #!/bin/bash
      . /var/lib/cloud/scripts/per-instance/01_load_env_vars.sh
      # $${ is terraform heredoc escape for dollarsign-curlybrace
      aws ecr get-login-password --region $${AWS_REGION} | docker login --username AWS --password-stdin $${ECR_REPO_URL}
      # Pull the container on every boot to get latest updates
      docker pull $${ECR_REPO_URL}:$${IMAGE_TAG}
      /usr/bin/docker run --rm -d -p 0.0.0.0:$${CONTAINER_PORT}:$${CONTAINER_PORT} $${ECR_REPO_URL}:$${IMAGE_TAG}

  - path: /var/lib/cloud/scripts/per-instance/04_create_symlinks.sh
    permissions: "0755"
    content: |
      #!/bin/bash
      ln -s /var/lib/cloud/scripts/per-instance/03_run_container.sh /var/lib/cloud/scripts/per-boot/03_run_container.sh
      echo "Created symlink for run_container.sh in per-boot"
  EOF
}

output "user_data" {
  value     = local.user_data
  sensitive = true
}

output "backend_public_ip" {
  value = aws_instance.einsingen_backend.public_ip
}

# 1) 
# Could be replaced by a jsonencode of a valid json
data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    effect = "Allow"
  
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      # ec2 for connecting to ecr from within container
      # dlm for data lifecycle management of snapshots
      identifiers = ["ec2.amazonaws.com", "dlm.amazonaws.com"]
    }
  }
}

# 2)
resource "aws_iam_role" "ecr" {
  name               = "ec2-ecr-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json
}

# 3)
resource "aws_iam_role_policy_attachment" "ecr_read_only" {
  role       = aws_iam_role.ecr.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_role_policy_attachment" "data_lifecycle_manager" {
  role = aws_iam_role.ecr.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSDataLifecycleManagerServiceRole"  
}

# 4)
resource "aws_iam_instance_profile" "ecr_access" {
  name_prefix = "ec2-ecr-access-einsingen"
  role        = aws_iam_role.ecr.name
}

resource "aws_dlm_lifecycle_policy" "data_volume" {
  description = "Policy to create snapshots of EC2-mounted EBS"
  execution_role_arn = aws_iam_role.ecr.arn
  state = "ENABLED"
  policy_details {
    resource_types = ["VOLUME"]
    schedule {
      name = "1 week of daily snapshots"
      create_rule {
        interval      = 24
        interval_unit = "HOURS"
        times         = ["23:45"]
      }
      retain_rule {
        count = 7
      }
      tags_to_add = {
        SnapshotCreator = "DLM"
      }

      copy_tags = true
    }

    target_tags = {
      component = "database"
    }
  }
}

# 5)
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  filter {
    name   = "name"
    values = ["al2023-ami-2023*-x86_64"]
  }
  owners = ["amazon"]

}

data "aws_vpc" "default_vpc" {
  id = var.DEFAULT_VPC_ID
}

resource "aws_security_group" "einsingen" {
  name        = "einsingen"
  description = "Security group for Einsingen EC2 instances"
  vpc_id      = data.aws_vpc.default_vpc.id
  region      = var.AWS_REGION
}

resource "aws_vpc_security_group_egress_rule" "einsingen_allow_http" {
  security_group_id = aws_security_group.einsingen.id

  cidr_ipv4   = "0.0.0.0/0"
  ip_protocol = "-1"
  description = "Allow all outbound traffic"
}

resource "aws_vpc_security_group_ingress_rule" "ssh" {
  security_group_id = aws_security_group.einsingen.id

  cidr_ipv4   = "0.0.0.0/0"
  from_port   = 22
  ip_protocol = "tcp"
  to_port     = 22
  description = "Allow SSH access from anywhere"
}

resource "aws_vpc_security_group_ingress_rule" "django_http" {
  security_group_id = aws_security_group.einsingen.id

  cidr_ipv4   = "0.0.0.0/0"
  from_port   = 8000
  ip_protocol = "tcp"
  to_port     = 8000
  description = "Allow HTTP access to django"
}

resource "aws_instance" "einsingen_backend" {
  ami           = data.aws_ami.amazon_linux_2023.id
  instance_type = var.BACKEND_EC2_INSTANCE_TYPE
  key_name      = var.BACKEND_EC2_SSH_KEY_NAME

  iam_instance_profile = aws_iam_instance_profile.ecr_access.name
  security_groups      = [aws_security_group.einsingen.name]
  user_data_base64     = base64encode(local.user_data)
}

resource "aws_ebs_volume" "einsingen_data" {
  availability_zone = "eu-north-1a"
  size              = 4
  encrypted         = false
  iops              = 3000
  final_snapshot    = true
  tags = {
    app       = "einsingen",
    component = "database",
  }
  throughput = 125
  type       = "gp3"
}

resource "aws_volume_attachment" "ebs_data_attach" {
  device_name = "/dev/sdf"
  volume_id = aws_ebs_volume.einsingen_data.id
  instance_id = aws_instance.einsingen_backend.id  
}

