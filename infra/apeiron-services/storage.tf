resource "random_id" "mlflow_artifacts" {
  byte_length = 4
  prefix      = "${var.project}-${var.name}-mlflow-artifacts-"
}

resource "aws_s3_bucket" "mlflow_artifacts" {
  bucket = random_id.mlflow_artifacts.hex
}
