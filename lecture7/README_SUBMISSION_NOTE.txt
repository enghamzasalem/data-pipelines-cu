Lecture 7 Submission Notes

This submission can use the AWS option from the lecture 7 assignment.

Included work:
- Terraform configuration for an AWS EC2 web server and n8n deployment
- Sequential startup in `user_data` so the web server starts before n8n
- Output URLs for both services

Important note:
- After running `terraform apply` with AWS credentials, capture:
  - the web server page with the browser URL visible
  - the n8n page with the browser URL visible, or the result of `terraform output`

Suggested PR title format:
- awezdar@constructor.university / WEZDAR AHMED / lecture 7 web_server_n8n_assignment
