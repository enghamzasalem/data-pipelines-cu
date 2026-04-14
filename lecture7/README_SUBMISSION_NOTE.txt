Lecture 7 Submission Notes

This submission uses the Docker option from the lecture 7 assignment.

Included work:
- Terraform configuration for a local web server and n8n deployment
- Explicit dependency order so the web server starts before n8n
- Output URLs for both services

Important note:
- Screenshots were not generated in this environment because Terraform and Docker are not available here.
- After running `terraform apply` on a machine with Docker, capture:
  - the web server page with the browser URL visible
  - the n8n page with the browser URL visible, or the result of `terraform output`

Suggested PR title format:
- awezdar@constructor.university / WEZDAR AHMED / lecture 7 web_server_n8n_assignment
