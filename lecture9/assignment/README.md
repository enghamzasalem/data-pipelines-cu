# Lecture 9 assignment files

| File | Description |
|------|-------------|
| `hello-world.nomad.hcl` | Default Docker hello-world job using `busybox`. |
| `hello-world-exec.nomad.hcl` | Linux-only no-Docker hello-world job using `exec`. |
| `hello-world-windows.nomad.hcl` | Windows no-Docker hello-world job using `raw_exec` and PowerShell. |
| `nginx-web.nomad.hcl` | Optional nginx web service job. |
| `simple-html-web.nomad.hcl` | Optional static HTML service without Docker. |

Basic commands:

```bash
export NOMAD_ADDR=http://localhost:4646
nomad job run assignment/hello-world.nomad.hcl
nomad job status hello-world
nomad alloc logs <alloc-id> hello
```

See `../LECTURE9_ASSIGNMENT_README.md` for the full assignment workflow.
