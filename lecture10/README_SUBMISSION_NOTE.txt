Lecture 10 submission checklist

1. Start the Nomad dev agent.
2. Run the Ollama Nomad job.
3. Wait for the poststart pull task to finish.
4. Confirm `api/tags` shows the pulled model.
5. Take two screenshots:
   - Nomad UI with `ollama` running
   - terminal output from `api/tags`
6. Submit the PR.
7. Add one short note that connects this work to:
   - Lecture 9 for Nomad basics, or
   - Lecture 8 for infrastructure sizing / capacity planning

Windows path prepared in this folder:
- `nomad-dev-windows.hcl`
- `assignment/ollama-windows.nomad.hcl`

Current successful local result:
- job: `ollama`
- tags output includes: `tinyllama:latest`
