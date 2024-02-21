
# Build layer with Python dependencies
data "archive_file" "python_layer" {
  type        = "zip"
  output_path = "/tmp/python_layer_zip_dir.zip"
  source_dir  = "../python_layer"
}

resource "aws_lambda_layer_version" "python_layer" {
  layer_name          = "python_dependencies"
  filename            = data.archive_file.python_layer.output_path
  source_code_hash    = data.archive_file.python_layer.output_base64sha256
  compatible_runtimes = ["python3.8"]
}