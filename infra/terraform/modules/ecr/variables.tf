variable "project" {
  type        = string
  description = "Project name, used as a prefix for the repository name."
}

variable "name" {
  type        = string
  description = "Short name for what this repo holds, e.g. \"api\"."
}

variable "keep_last_n_images" {
  type        = number
  default     = 10
  description = "Number of most-recent images to retain before lifecycle expiry."
}
