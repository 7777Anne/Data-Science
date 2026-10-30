# Standalone GitHub migration plan

**Purpose:** promote five runnable subprojects to their own public GitHub repositories while preserving history. Hotel Booking already exists as a standalone repository.

## Why this migration requires a local authenticated step

The connected GitHub integration can edit existing repositories, but does not provide a repository-creation action. The checked-in script uses GitHub CLI (`gh`) on the owner's laptop to create repositories. It does not require giving credentials to ChatGPT.

## Prerequisites (Mac)

```bash
brew install gh
gh auth login
git clone https://github.com/7777Anne/Data-Science.git
cd Data-Science
bash scripts/migrate_to_standalone_repos.sh --dry-run
```

Read the script before running it. If the dry-run lists the correct destinations, execute:

```bash
bash scripts/migrate_to_standalone_repos.sh --execute
```

This creates **five** standalone repositories from subtrees of `Data-Science`, using `git subtree split` to preserve project-specific history. It adds CI, project-root command paths and output ignore rules, then creates the `7777Anne/7777Anne` GitHub profile repository from a template. It does not delete the original monorepo or hotel repository.

**Safety:** If a destination already exists, the script stops rather than overwriting it. If a network operation fails partway through, inspect what was created before rerunning; the script intentionally avoids overwriting any partial destinations.

## Post-migration verification

1. Open each new repository, verify README and `.github/workflows/ci.yml`.
2. Check Actions for a passing CI run and inspect generated metrics locally.
3. Compare `git log --oneline` with the original project's subtree history.
4. Pin up to six strong repositories from GitHub Profile > Customize your pins.
5. Confirm `https://github.com/7777Anne` displays the profile README.
6. Only after validation, update the original monorepo README to describe it as the archive/index.

## Not promoted yet

Automotive Copilot, EV Sustainability and Precision Medicine are research/historical scaffolds without complete working implementations. They should not become headline repositories until rebuilt and validated.
