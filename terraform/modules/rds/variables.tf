variable "project_name" {
  description = "Project name used for naming and tagging."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}

variable "private_db_subnet_ids" {
  description = "Private database subnet IDs."
  type        = list(string)
}

variable "security_group_id" {
  description = "Security group assigned to PostgreSQL."
  type        = string
}

variable "instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t4g.micro"
}

variable "allocated_storage" {
  description = "Initial database storage in GiB."
  type        = number
  default     = 20
}

variable "max_allocated_storage" {
  description = "Maximum autoscaled database storage in GiB."
  type        = number
  default     = 50
}

variable "database_name" {
  description = "Initial PostgreSQL database name."
  type        = string
  default     = "platform_launchpad"
}

variable "master_username" {
  description = "PostgreSQL master username."
  type        = string
  default     = "platform_admin"
}

variable "backup_retention_period" {
  description = "Number of days automated backups are retained."
  type        = number
  default     = 1
}

variable "deletion_protection" {
  description = "Protect the database from accidental deletion."
  type        = bool
  default     = false
}

variable "engine_version" {
  description = "PostgreSQL major engine version."
  type        = string
  default     = "18"
}