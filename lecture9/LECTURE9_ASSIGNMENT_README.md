# Lecture 9: Nomad Assignment - Hello World

Run a Nomad development cluster and submit a minimal batch job that prints `Hello, world from Nomad!`.

## Objectives

1. Install the Nomad CLI (>= 1.5) and verify with `nomad -v`.
2. Start a local dev agent, or use a cluster with `NOMAD_ADDR` set.
3. Submit a hello-world jobspec with `nomad job run`.
4. Confirm the job completed and read the task output from allocation logs.
5. Clean up with `nomad job stop -purge` if needed.

## Prerequisites

- Nomad >= 1.5
- Docker running for `assignment/hello-world.nomad.hcl`
- Linux without Docker: use `assignment/hello-world-exec.nomad.hcl`
- Windows without Docker: use `assignment/hello-world-windows.nomad.hcl`

## Steps

### 1. Start the dev agent

macOS with Docker Desktop:

```bash
chmod +x nomad-dev-macos.sh
./nomad-dev-macos.sh
```

Linux:

```bash
sudo nomad agent -dev \
  -bind 0.0.0.0 \
  -network-interface='{{ GetDefaultInterfaces | attr "name" }}'
```

Windows without Docker:

```powershell
nomad agent -dev -bind 127.0.0.1 -data-dir="$PWD/.nomad-dev-data" -config=nomad-dev-windows.hcl
```

In a second terminal:

```bash
export NOMAD_ADDR=http://localhost:4646
nomad node status
```

PowerShell equivalent:

```powershell
$env:NOMAD_ADDR = "http://127.0.0.1:4646"
nomad node status
```

### 2. Run the job

Default Docker path:

```bash
cd lecture9
nomad job run assignment/hello-world.nomad.hcl
```

No-Docker alternatives:

- Linux: `nomad job run assignment/hello-world-exec.nomad.hcl`
- Windows: `nomad job run assignment/hello-world-windows.nomad.hcl`

### 3. See the output

```bash
nomad job status hello-world
nomad alloc logs <allocation-id> hello
```

You should see:

```text
Hello, world from Nomad!
```

You can also open [http://127.0.0.1:4646/ui](http://127.0.0.1:4646/ui) and inspect the `hello-world` job there.

### 4. Clean up

```bash
nomad job stop -purge hello-world
```

Stop the dev agent with `Ctrl+C` in the first terminal.

## Troubleshooting

### `Dimension "cpu" exhausted`

1. Run `nomad job status`
2. Purge any old jobs with `nomad job stop -purge <job-id>`
3. Run `nomad system gc`
4. Restart the dev agent

### `Constraint "missing drivers"` on macOS

Use `hello-world.nomad.hcl` with Docker. Do not use `hello-world-exec.nomad.hcl` on macOS.

### Windows without Docker

Use `nomad-dev-windows.hcl` to enable `raw_exec`, then run `assignment/hello-world-windows.nomad.hcl`.

## How to Submit

1. A screenshot of the Nomad UI showing the `hello-world` job completed, or a terminal screenshot showing `nomad alloc logs` with the hello line.
2. A pull request with the screenshot and your jobspec if you changed it.

### PR title example

```text
Lecture 9: Nomad hello-world - [Your Name]
```

## Optional extension

- `assignment/nginx-web.nomad.hcl`
- `assignment/simple-html-web.nomad.hcl`

## Reference

- [Nomad Quick Start](https://developer.hashicorp.com/nomad/tutorials/get-started)
