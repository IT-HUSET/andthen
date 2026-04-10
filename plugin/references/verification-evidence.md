# Verification Evidence

Use this reference whenever a skill asks for verification evidence in its completion summary.

## Rules
- Report only evidence you actually ran or observed.
- Include status/counts when available, not vague claims.
- Mention only the evidence categories relevant to the current workflow.

## Evidence Types
- **Build**: Exit code or success/failure status.
- **Tests**: Pass/fail counts such as `42/42 pass`.
- **Linting/types**: Error and warning counts.
- **Visual validation**: Screenshot-based confirmation that UI output matches requirements.
- **Runtime**: Confirmation that the app or flow started and worked in the exercised path.

## Default Subsets
- **Plan orchestration** (`exec-plan`, `exec-plan-team`): Build, Tests, Linting/types.
- **Story execution** (`exec-spec`): Build, Tests, Linting/types. Add Visual validation and Runtime when the story includes UI work or app-start/runtime behavior.
- **Quick implementation** (`quick-implement`): Build, Tests, Linting/types. Add Visual validation when UI changed. Add Runtime when you started the app or exercised the flow directly.
