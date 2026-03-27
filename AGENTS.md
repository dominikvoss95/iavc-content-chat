# AGENTS.md

## Project Structure
- Always use modular, maintainable app project structure for the respective language and web framework
- Always check if a feature works before moving on to the next feature
  - ie do incremental development
- Add README.md file to the root of the project
- Docs via mkdocs

### Coding style
- Use snake_case for variable and function names
- Use CamelCase for class names
- Use PEP 8 style guide for code formatting
- Use descriptive variable names that are self-explanatory
- Use descriptive function names that are self-explanatory
- Use descriptive class names that are self-explanatory
- Use descriptive docstrings for functions and classes
- Use descriptive comments for code that is not self-explanatory
- Use descriptive variable names that are self-explanatory

### Tools you can use
Based on the language you are using, you can use the following tools:

For All:
- **Commit:** `git commit -am "<message>"` (commits changes, must pass before commits)
  - use conventional commits (eg feat: add new feature, fix: fix bug)
- **Push:** `git push` (pushes changes to remote repository, must pass before commits)

- **CMD or Bash Terminal:** (for running commands)

For TypeScript/JavaScript
- **Build:** `npm run build` (compiles TypeScript, outputs to dist/)
- **Test:** `npm test` (runs Jest, must pass before commits)
- **Lint:** `npm run lint --fix` (auto-fixes ESLint errors)

For Python
- **Build or run:** `python app.py` (runs the app, must pass before commits)
- **Test:** `pytest` (runs pytest, must pass before commits)
- **Lint:** `pylint` (runs pylint, must pass before commits)

For Rust
- **Build or run:** `cargo run` (runs cargo run, must pass before commits)
- **Test:** `cargo test` (runs cargo test, must pass before commits)
- **Lint:** `cargo fmt` (runs cargo fmt, must pass before commits)

For Go
- **Build or run:** `go run main.go` (runs go run, must pass before commits)
- **Test:** `go test` (runs go test, must pass before commits)
- **Lint:** `golangci-lint run` (runs golangci-lint, must pass before commits)

For Julia
- **Build or run:** `julia -e "using Pkg; Pkg.instantiate()"` (runs Julia build or run, must pass before commits)
- **Test:** `julia -e "using Pkg; Pkg.test()"` (runs Julia test, must pass before commits)
- **Lint:** `julia -e "using Pkg; Pkg.instantiate()"` (runs Julia lint, must pass before commits)

For C
- **Build or run:** `gcc main.c -o main` (runs gcc, must pass before commits)
- **Test:** `make test` (runs make test, must pass before commits)
- **Lint:** `make lint` (runs make lint, must pass before commits)

For C++
- **Build or run:** `g++ main.cpp -o main` (runs g++, must pass before commits)
- **Test:** `make test` (runs make test, must pass before commits)
- **Lint:** `make lint` (runs make lint, must pass before commits)

### Boundaries
- **Always:** Write to `src/` or similar and `tests/`, run tests before commits, follow naming conventions
- **Ask first:** Database schema changes, adding dependencies, modifying CI/CD config
- **Never:** Commit secrets or API keys

### Security
- **Always:** Use secure coding practices, follow OWASP Top 10, use secure authentication and authorization, use secure data storage, use secure data transmission, use secure data encryption, use secure data access, use secure data backup, use secure data recovery, use secure data disposal