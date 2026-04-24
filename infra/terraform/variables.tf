variable "aws_region" {
  type        = string
  default     = "eu-north-1"
  description = "AWS region"
}

variable "hosted_zone_id" {
  type        = string
  description = "Route53 Hosted Zone ID"
}

variable "acm_certificate_arn" {
  type        = string
  description = "ACM certificate ARN for HTTPS"
}

variable "image_url" {
  type        = string
  default     = "509399624827.dkr.ecr.eu-north-1.amazonaws.com/scraper-repo:latest"
  description = "Full image URL in ECR, static value"
}

variable "domain_prefix" {
  type        = string
  default     = "scraper-news"
  description = "Subdomain prefix for Route53 record (e.g. scraper-news.example.com)"
}

variable "ecs_cluster_name" {
  type        = string
  default     = "scraper-news-cluster"
  description = "ECS cluster name"
}

variable "ecs_service_name" {
  type        = string
  default     = "scraper-news-service"
  description = "ECS service name"
}

variable "container_name" {
  type        = string
  default     = "scraper-news-container"
  description = "Container name in the task definition"
}

variable "container_port" {
  type        = number
  default     = 80
  description = "Container port exposed by the application"
}

variable "cpu" {
  type        = string
  default     = "2048"
  description = "Fargate task CPU units"
}

variable "memory" {
  type        = string
  default     = "8192"
  description = "Fargate task memory (MiB)"
}

variable "desired_count" {
  type        = number
  default     = 1
  description = "Number of desired ECS tasks"
}

variable "hf_token" {
  type        = string
  description = "HuggingFace access token"
}
