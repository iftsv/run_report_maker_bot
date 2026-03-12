### Intro feat_02.md
This document outlines the plan for **Feature Update 2**: Deployment Automation for the **Run Report Maker Bot**.

### Phase 5: CI/CD Pipeline & Automated Deployment
**Prompt for Antigravity:**
> **Mission: Automate deployment to an Ubuntu server using GitHub Actions.**
> 
> **Objective:** Create a seamless deployment process where code changes pushed to the repository are automatically pulled to the server and the service is restarted.
> 
> **Requirements:**
> 1. **Deployment Script:**
>    - Create `deploy_run_report_maker_bot.sh` in the repository root.
>    - The script should go to the project directory `/home/user/running_bot`.
>    - Perform a `git pull` to fetch the latest changes.
>    - Install new requirements using the virtual environment.
>    - Restart the `running_bot.service` using `systemctl`.
> 
> 2. **GitHub Actions Workflow:**
>    - Create a YAML file in `.github/workflows/deploy.yml`.
>    - The workflow triggers on a push to the `main` branch.
>    - It uses an SSH action (like `appleboy/ssh-action`) to securely connect to the Ubuntu server.
>    - It executes the `deploy_run_report_maker_bot.sh` script on the server.
> 
> 3. **Secret Management:**
>    - The GitHub repo must hold secrets for `HOST` (server IP), `USERNAME` (server user), and `SSH_KEY` (private key for SSH).

### Details for implementation
The deployment script must be made executable (`chmod +x deploy_run_report_maker_bot.sh`). Using absolute paths in the script is recommended to prevent working directory issues during remote execution.
