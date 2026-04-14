# Lecture 9: HashiCorp Nomad

Theme: workload orchestration for containers and batch jobs in the context of the data pipeline course.

## Official tutorials

- [Nomad introduction](https://developer.hashicorp.com/nomad/tutorials/get-started/introduction)
- [Install Nomad](https://developer.hashicorp.com/nomad/tutorials/get-started/install)
- [Create a cluster](https://developer.hashicorp.com/nomad/tutorials/get-started/cluster)
- [Deploy and update a job](https://developer.hashicorp.com/nomad/tutorials/get-started/jobs)
- [Stop the cluster](https://developer.hashicorp.com/nomad/tutorials/get-started/cleanup)

## Assignment

Minimal `hello-world` batch job options:

- `assignment/hello-world.nomad.hcl` for Docker
- `assignment/hello-world-exec.nomad.hcl` for Linux without Docker
- `assignment/hello-world-windows.nomad.hcl` for Windows without Docker

See `LECTURE9_ASSIGNMENT_README.md` for the exact submission steps.

## Prerequisites

- Nomad >= 1.5
- Docker for the Docker-based jobspecs
- On Windows without Docker, use `nomad-dev-windows.hcl` with `assignment/hello-world-windows.nomad.hcl`

## Reference

- Lecture 6 and Lecture 7: Docker web services
- Lecture 8: Terraform baseline infrastructure
- [Nomad documentation](https://developer.hashicorp.com/nomad/docs)
