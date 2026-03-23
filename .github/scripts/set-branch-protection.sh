#!/usr/bin/env bash
# Apply branch protection rules to main and develop via the GitHub API.
#
# Prerequisites:
#   gh auth login    (GitHub CLI, authenticated with repo admin scope)
#
# Usage:
#   bash .github/scripts/set-branch-protection.sh
#
# What it enforces:
#   - CI / Pytest must pass before merging
#   - Branches must be up to date with the base branch
#   - At least 1 approving review required
#   - Applies to both main and develop

set -euo pipefail

REPO="Coding-Temple-Tech-Residency/TR42-VistaOne-GBTF"
CI_CHECK="CI / Pytest"

apply_protection() {
  local branch="$1"
  echo "Applying branch protection to: ${branch}"
  gh api "repos/${REPO}/branches/${branch}/protection" \
    --method PUT \
    --header "Accept: application/vnd.github+json" \
    --field "required_status_checks[strict]=true" \
    --field "required_status_checks[contexts][]=${CI_CHECK}" \
    --field "enforce_admins=false" \
    --field "required_pull_request_reviews[required_approving_review_count]=1" \
    --field "required_pull_request_reviews[dismiss_stale_reviews]=true" \
    --field "restrictions=null"
  echo "  Done."
}

apply_protection "main"
apply_protection "develop"

echo ""
echo "Branch protection applied. Verify at:"
echo "  https://github.com/${REPO}/settings/branches"
