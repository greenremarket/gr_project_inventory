# Odoo CI Workflow

This directory contains CI workflows for testing the Odoo module.

## odoo-ci.yml

This workflow sets up a proper Odoo environment in GitHub Actions to run your tests:

1. It creates a PostgreSQL database for Odoo
2. Installs system dependencies needed for Odoo
3. Downloads and installs Odoo 17.0
4. Sets up Python paths and Odoo configuration
5. Runs your tests with pytest

## Setup Instructions

1. Replace the existing `.github/workflows/ci.yml` with this new workflow:
   ```bash
   mv .github/workflows-new/odoo-ci.yml .github/workflows/odoo-ci.yml
   rm .github/workflows/ci.yml  # Or rename if you want to keep it
   ```

2. Push the changes to trigger the new workflow.

## Including Enterprise Modules (Optional)

If your module depends on Odoo Enterprise, you need to follow these additional steps:

1. Create a GitHub secret named `ENTERPRISE_TOKEN` with a personal access token that has access to the Enterprise repository.
2. Modify the workflow to include these additional steps for accessing Enterprise:

```yaml
- name: Clone Enterprise repository
  if: ${{ github.event_name != 'pull_request' || github.event.pull_request.head.repo.full_name == github.repository }}
  run: |
    git clone https://x-access-token:${{ secrets.ENTERPRISE_TOKEN }}@github.com/odoo/enterprise.git --depth 1 --branch 17.0 enterprise

- name: Create mock enterprise for public PRs
  if: ${{ github.event_name == 'pull_request' && github.event.pull_request.head.repo.full_name != github.repository }}
  run: |
    mkdir -p enterprise/setup
    touch enterprise/setup/__init__.py
```

3. Update the addons_path in the workflow to include the enterprise modules:
   ```
   echo "addons_path = $(pwd),$(pwd)/enterprise,$(pwd)/../odoo-17.0/addons" >> ~/.odoo/odoo.conf
   ```
