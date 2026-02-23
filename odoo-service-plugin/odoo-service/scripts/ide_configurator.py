#!/usr/bin/env python3
"""
ide_configurator.py — IDE Configuration Generator for Odoo

Generate run configurations for PyCharm and VSCode to develop Odoo projects
without manual setup. Supports local venv and Docker environments.

Usage:
    python ide_configurator.py --ide vscode --env local --config TAQAT17.conf
    python ide_configurator.py --ide pycharm --env docker --project myproject
    python ide_configurator.py --ide both --env docker --project myproject
    python ide_configurator.py --gitignore-only
    python ide_configurator.py --env-example-only --project myproject
"""

import argparse
import json
import os
import platform
import sys
from pathlib import Path
from typing import Optional

IS_WINDOWS = platform.system() == "Windows"


# ---------------------------------------------------------------------------
# PyCharm Configurations
# ---------------------------------------------------------------------------

def generate_pycharm_local_config(
    project_name: str,
    config_file: str,
    venv_path: str = ".venv",
    output_dir: str = ".",
) -> Path:
    """Generate PyCharm local Python run configuration XML."""
    out = Path(output_dir) / ".idea" / "runConfigurations"
    out.mkdir(parents=True, exist_ok=True)

    # Determine venv python path
    venv = Path(venv_path)
    if IS_WINDOWS:
        sdk_home = f"$PROJECT_DIR$/{venv_path}/Scripts/python.exe"
    else:
        sdk_home = f"$PROJECT_DIR$/{venv_path}/bin/python"

    conf_name = f"Odoo_{project_name}".replace(" ", "_")
    filename = out / f"{conf_name}.xml"

    content = f"""\
<component name="ProjectRunConfigurationManager">
  <configuration default="false" name="Odoo {project_name}" type="PythonConfigurationType"
                 factoryName="Python" nameIsGenerated="false">
    <module name="{project_name}" />
    <option name="INTERPRETER_OPTIONS" value="" />
    <option name="PARENT_ENVS" value="true" />
    <option name="SDK_HOME" value="{sdk_home}" />
    <option name="WORKING_DIRECTORY" value="$PROJECT_DIR$" />
    <option name="IS_MODULE_SDK" value="false" />
    <option name="ADD_CONTENT_ROOTS" value="true" />
    <option name="ADD_SOURCE_ROOTS" value="true" />
    <EXTENSION ID="PythonCoverageRunConfigurationExtension" runner="coverage.py" />
    <option name="SCRIPT_NAME" value="$PROJECT_DIR$/odoo-bin" />
    <option name="PARAMETERS" value="-c conf/{config_file}" />
    <option name="SHOW_COMMAND_LINE" value="false" />
    <option name="EMULATE_TERMINAL" value="true" />
    <option name="MODULE_MODE" value="false" />
    <option name="REDIRECT_INPUT" value="false" />
    <option name="INPUT_FILE" value="" />
    <method v="2" />
  </configuration>
</component>
"""

    filename.write_text(content, encoding="utf-8")
    print(f"[OK] PyCharm local config: {filename}")

    # Also generate dev mode config
    dev_conf_name = f"Odoo_{project_name}_dev".replace(" ", "_")
    dev_filename = out / f"{dev_conf_name}.xml"
    dev_content = content.replace(
        f'-c conf/{config_file}"',
        f'-c conf/{config_file} --dev=all"'
    ).replace(
        f"name=\"Odoo {project_name}\"",
        f"name=\"Odoo {project_name} (dev)\""
    )
    dev_filename.write_text(dev_content, encoding="utf-8")
    print(f"[OK] PyCharm dev config: {dev_filename}")

    return filename


def generate_pycharm_docker_config(
    project_name: str,
    output_dir: str = ".",
    compose_file: str = "docker-compose.yml",
) -> Path:
    """Generate PyCharm Docker Compose run configuration XML."""
    out = Path(output_dir) / ".idea" / "runConfigurations"
    out.mkdir(parents=True, exist_ok=True)

    conf_name = f"Odoo_{project_name}_Docker".replace(" ", "_")
    filename = out / f"{conf_name}.xml"

    content = f"""\
<component name="ProjectRunConfigurationManager">
  <configuration default="false" name="Odoo {project_name} (Docker)" type="docker-deploy"
                 factoryName="docker-compose.yml" server-name="Docker">
    <deployment type="docker-compose.yml">
      <settings>
        <option name="envFilePath" value="$PROJECT_DIR$/.env" />
        <option name="composeFilePaths">
          <list>
            <option value="$PROJECT_DIR$/{compose_file}" />
          </list>
        </option>
        <option name="sourceFilePath" value="{compose_file}" />
      </settings>
    </deployment>
    <method v="2" />
  </configuration>
</component>
"""

    filename.write_text(content, encoding="utf-8")
    print(f"[OK] PyCharm Docker config: {filename}")
    return filename


def generate_pycharm_misc_xml(output_dir: str = ".") -> Path:
    """Generate .idea/misc.xml with Odoo-appropriate settings."""
    out = Path(output_dir) / ".idea"
    out.mkdir(parents=True, exist_ok=True)

    filename = out / "misc.xml"
    if filename.exists():
        print(f"[INFO] .idea/misc.xml already exists, skipping.")
        return filename

    content = """\
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="JavaScriptSettings">
    <option name="languageLevel" value="ES6" />
  </component>
  <component name="ProjectRootManager" version="2" project-jdk-name="Python 3.11" project-jdk-type="Python SDK" />
</project>
"""
    filename.write_text(content, encoding="utf-8")
    print(f"[OK] .idea/misc.xml created: {filename}")
    return filename


# ---------------------------------------------------------------------------
# VSCode Configurations
# ---------------------------------------------------------------------------

def generate_vscode_tasks(
    project_name: str,
    env_type: str = "local",
    compose_file: Optional[str] = None,
    config_file: Optional[str] = None,
    output_dir: str = ".",
) -> Path:
    """Generate .vscode/tasks.json for Odoo development."""
    out = Path(output_dir) / ".vscode"
    out.mkdir(parents=True, exist_ok=True)

    filename = out / "tasks.json"

    default_config = config_file or "odoo.conf"
    cf = f'"{compose_file}"' if compose_file else '"docker-compose.yml"'

    tasks = {
        "version": "2.0.0",
        "tasks": [
            {
                "label": f"Odoo: Start ({project_name}, dev mode)",
                "type": "shell",
                "command": f"python -m odoo -c conf/${{input:configFile}} --dev=all",
                "group": {"kind": "build", "isDefault": True},
                "presentation": {"reveal": "always", "panel": "new", "showReuseMessage": False},
                "problemMatcher": []
            },
            {
                "label": f"Odoo: Start ({project_name}, production mode)",
                "type": "shell",
                "command": f"python -m odoo -c conf/${{input:configFile}} --workers=4",
                "group": "build",
                "presentation": {"reveal": "always", "panel": "new"},
                "problemMatcher": []
            },
            {
                "label": "Odoo: Stop (kill port 8069)",
                "type": "shell",
                "windows": {
                    "command": "FOR /F \"tokens=5\" %P IN ('netstat -ano ^| findstr :8069') DO taskkill /PID %P /F"
                },
                "linux": {"command": "lsof -ti:8069 | xargs kill -9"},
                "osx": {"command": "lsof -ti:8069 | xargs kill -9"},
                "command": "FOR /F \"tokens=5\" %P IN ('netstat -ano ^| findstr :8069') DO taskkill /PID %P /F",
                "presentation": {"reveal": "always"},
                "problemMatcher": []
            },
            {
                "label": "Odoo: Update Module",
                "type": "shell",
                "command": "python -m odoo -c conf/${input:configFile} -d ${input:database} -u ${input:moduleName} --stop-after-init",
                "presentation": {"reveal": "always", "panel": "shared"},
                "problemMatcher": []
            },
            {
                "label": "Odoo: Install Module",
                "type": "shell",
                "command": "python -m odoo -c conf/${input:configFile} -d ${input:database} -i ${input:moduleName} --stop-after-init",
                "presentation": {"reveal": "always"},
                "problemMatcher": []
            },
            {
                "label": "Odoo: Refresh Module List",
                "type": "shell",
                "command": "python -m odoo -c conf/${input:configFile} -d ${input:database} --update-list",
                "presentation": {"reveal": "always"},
                "problemMatcher": []
            },
            {
                "label": "Docker: Start",
                "type": "shell",
                "command": "docker-compose up -d",
                "group": "build",
                "presentation": {"reveal": "always"},
                "problemMatcher": []
            },
            {
                "label": "Docker: Stop",
                "type": "shell",
                "command": "docker-compose down",
                "presentation": {"reveal": "always"},
                "problemMatcher": []
            },
            {
                "label": "Docker: Rebuild",
                "type": "shell",
                "command": "docker-compose up -d --build",
                "presentation": {"reveal": "always", "panel": "new"},
                "problemMatcher": []
            },
            {
                "label": "Docker: Logs",
                "type": "shell",
                "command": "docker-compose logs -f odoo",
                "presentation": {"reveal": "always", "panel": "shared"},
                "problemMatcher": []
            },
            {
                "label": "Docker: Shell",
                "type": "shell",
                "command": "docker-compose exec odoo bash",
                "presentation": {"reveal": "always", "panel": "new"},
                "problemMatcher": []
            },
            {
                "label": "Docker: Update Module",
                "type": "shell",
                "command": "docker-compose exec odoo python -m odoo -c /etc/odoo/odoo.conf -d ${input:database} -u ${input:moduleName} --stop-after-init",
                "presentation": {"reveal": "always"},
                "problemMatcher": []
            },
            {
                "label": "DB: Backup",
                "type": "shell",
                "command": "python odoo-service/scripts/db_manager.py backup --db ${input:database} --output backups/",
                "presentation": {"reveal": "always"},
                "problemMatcher": []
            }
        ],
        "inputs": [
            {
                "id": "configFile",
                "type": "promptString",
                "description": "Config file name (e.g. TAQAT17.conf)",
                "default": default_config
            },
            {
                "id": "database",
                "type": "promptString",
                "description": "Database name",
                "default": project_name
            },
            {
                "id": "moduleName",
                "type": "promptString",
                "description": "Module name(s) to install/update (comma-separated)",
                "default": "my_module"
            }
        ]
    }

    filename.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
    print(f"[OK] VSCode tasks.json: {filename}")
    return filename


def generate_vscode_launch(
    config_file: Optional[str] = None,
    venv_path: str = ".venv",
    output_dir: str = ".",
) -> Path:
    """Generate .vscode/launch.json for Odoo debugging."""
    out = Path(output_dir) / ".vscode"
    out.mkdir(parents=True, exist_ok=True)

    filename = out / "launch.json"

    if IS_WINDOWS:
        python_path = f"${{workspaceFolder}}/{venv_path}/Scripts/python.exe"
    else:
        python_path = f"${{workspaceFolder}}/{venv_path}/bin/python"

    default_config = config_file or "odoo.conf"

    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Odoo: Debug (Local)",
                "type": "debugpy",
                "request": "launch",
                "module": "odoo",
                "args": ["-c", f"conf/${{input:configFile}}", "--dev=all"],
                "cwd": "${workspaceFolder}",
                "python": python_path,
                "justMyCode": False,
                "console": "integratedTerminal",
                "env": {"PYTHONDONTWRITEBYTECODE": "1"}
            },
            {
                "name": "Odoo: Debug (Local, specific DB)",
                "type": "debugpy",
                "request": "launch",
                "module": "odoo",
                "args": [
                    "-c", f"conf/${{input:configFile}}",
                    "-d", "${input:database}",
                    "--dev=all"
                ],
                "cwd": "${workspaceFolder}",
                "python": python_path,
                "justMyCode": False,
                "console": "integratedTerminal"
            },
            {
                "name": "Odoo: Debug (Docker attach)",
                "type": "debugpy",
                "request": "attach",
                "connect": {"host": "localhost", "port": 5678},
                "pathMappings": [
                    {
                        "localRoot": "${workspaceFolder}",
                        "remoteRoot": "/opt/odoo/source"
                    }
                ]
            },
            {
                "name": "Odoo: Update Module",
                "type": "debugpy",
                "request": "launch",
                "module": "odoo",
                "args": [
                    "-c", f"conf/${{input:configFile}}",
                    "-d", "${input:database}",
                    "-u", "${input:moduleName}",
                    "--stop-after-init"
                ],
                "cwd": "${workspaceFolder}",
                "python": python_path,
                "justMyCode": True,
                "console": "integratedTerminal"
            }
        ],
        "inputs": [
            {
                "id": "configFile",
                "type": "promptString",
                "description": "Config file name",
                "default": default_config
            },
            {
                "id": "database",
                "type": "promptString",
                "description": "Database name",
                "default": "myproject17"
            },
            {
                "id": "moduleName",
                "type": "promptString",
                "description": "Module name to update",
                "default": "my_module"
            }
        ]
    }

    filename.write_text(json.dumps(launch_config, indent=2), encoding="utf-8")
    print(f"[OK] VSCode launch.json: {filename}")
    return filename


def generate_vscode_settings(output_dir: str = ".") -> Path:
    """Generate .vscode/settings.json with Odoo-appropriate settings."""
    out = Path(output_dir) / ".vscode"
    out.mkdir(parents=True, exist_ok=True)

    filename = out / "settings.json"

    if IS_WINDOWS:
        python_path = ".venv/Scripts/python.exe"
    else:
        python_path = ".venv/bin/python"

    settings = {
        "python.analysis.extraPaths": [
            "./odoo",
            "./odoo/addons",
            "./projects"
        ],
        "python.languageServer": "Pylance",
        "python.defaultInterpreterPath": python_path,
        "python.analysis.typeCheckingMode": "basic",
        "python.analysis.autoImportCompletions": True,
        "python.analysis.diagnosticMode": "workspace",
        "files.exclude": {
            "**/__pycache__": True,
            "**/*.pyc": True,
            "**/*.pyo": True,
            "odoo.egg-info": True,
            "**/.git": False
        },
        "search.exclude": {
            "odoo.egg-info": True,
            "**/__pycache__": True,
            ".venv": True,
            "**/*.pyc": True,
            "data": True
        },
        "editor.rulers": [79, 120],
        "editor.formatOnSave": False,
        "editor.tabSize": 4,
        "editor.insertSpaces": True,
        "files.associations": {
            "*.xml": "xml",
            "*.conf": "ini",
            "*.po": "po",
            "*.pot": "po"
        },
        "xml.validation.enabled": False,
        "[python]": {
            "editor.tabSize": 4,
            "editor.insertSpaces": True
        },
        "[xml]": {
            "editor.tabSize": 4
        },
        "[javascript]": {
            "editor.tabSize": 4
        },
        "files.trimTrailingWhitespace": True,
        "files.insertFinalNewline": True,
        "terminal.integrated.defaultProfile.windows": "Command Prompt"
    }

    filename.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    print(f"[OK] VSCode settings.json: {filename}")
    return filename


def generate_vscode_extensions(output_dir: str = ".") -> Path:
    """Generate .vscode/extensions.json with recommended Odoo extensions."""
    out = Path(output_dir) / ".vscode"
    out.mkdir(parents=True, exist_ok=True)

    filename = out / "extensions.json"

    extensions = {
        "recommendations": [
            "ms-python.python",
            "ms-python.vscode-pylance",
            "ms-python.debugpy",
            "redhat.vscode-xml",
            "ms-azuretools.vscode-docker",
            "odoo-ide.odoo-vscode-extension",
            "mechatroner.rainbow-csv",
            "gruntfuggly.todo-tree",
            "eamodio.gitlens"
        ]
    }

    filename.write_text(json.dumps(extensions, indent=2), encoding="utf-8")
    print(f"[OK] VSCode extensions.json: {filename}")
    return filename


# ---------------------------------------------------------------------------
# .gitignore
# ---------------------------------------------------------------------------

GITIGNORE_CONTENT = """\
# =============================================================
# Odoo Project .gitignore
# =============================================================

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environments
.venv/
venv/
ENV/
env/
.env/
env.bak/
venv.bak/
.python-version

# Odoo-specific
data/
logs/
*.log
*.log.*
backups/
*.dump
*.sql.gz

# IDE
.idea/
*.iml
*.iws
*.ipr
.vscode/
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
desktop.ini

# Environment files
.env
.env.local
.env.production
.env.staging
!.env.example

# Node
node_modules/
npm-debug.log*
yarn-debug.log*

# Coverage
.coverage
.coverage.*
htmlcov/
.tox/
.pytest_cache/

# Distribution / packaging
*.manifest
*.spec

# PostgreSQL
*.dump
*.sql
!backups/.gitkeep

# Temporary files
*.tmp
*.bak
*.swp
*~
"""


def generate_gitignore(output_dir: str = ".") -> Path:
    """Generate an Odoo-appropriate .gitignore file."""
    out = Path(output_dir) / ".gitignore"

    if out.exists():
        print(f"[INFO] .gitignore already exists at {out}. Skipping.")
        return out

    out.write_text(GITIGNORE_CONTENT, encoding="utf-8")
    print(f"[OK] .gitignore created: {out}")
    return out


# ---------------------------------------------------------------------------
# .env.example
# ---------------------------------------------------------------------------

def generate_env_example(
    project_name: str,
    output_dir: str = ".",
    http_port: int = 8069,
) -> Path:
    """Generate a .env.example template."""
    out = Path(output_dir) / ".env.example"
    lp_port = http_port + 3

    content = f"""\
# =============================================================
# Odoo Environment Variables — .env.example
# Copy this to .env and customize for your environment
# =============================================================

# ---- PostgreSQL ----
POSTGRES_USER=odoo
POSTGRES_PASSWORD=change_me_in_production
POSTGRES_DB=postgres
PGHOST=localhost
PGPORT=5432

# ---- Odoo Ports ----
ODOO_HTTP_PORT={http_port}
ODOO_LONGPOLLING_PORT={lp_port}

# ---- Development ----
# Set to 'all' for dev mode, leave empty for production
DEV_MODE=all

# ---- Project ----
PROJECT_NAME={project_name}
ODOO_CONFIG=conf/{project_name}.conf

# ---- Email (optional) ----
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=your@email.com
# SMTP_PASSWORD=your_app_password
# SMTP_SSL=True

# ---- AWS S3 (optional, for attachment storage) ----
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
# AWS_S3_BUCKET=your_bucket
# AWS_REGION=us-east-1
"""

    out.write_text(content, encoding="utf-8")
    print(f"[OK] .env.example created: {out}")
    return out


# ---------------------------------------------------------------------------
# Full Generation
# ---------------------------------------------------------------------------

def generate_all_vscode(
    project_name: str,
    config_file: Optional[str] = None,
    venv_path: str = ".venv",
    output_dir: str = ".",
) -> None:
    """Generate all VSCode configuration files."""
    print(f"\n[INFO] Generating VSCode configuration for: {project_name}")
    generate_vscode_tasks(project_name, "local", config_file=config_file, output_dir=output_dir)
    generate_vscode_launch(config_file, venv_path, output_dir)
    generate_vscode_settings(output_dir)
    generate_vscode_extensions(output_dir)
    print(f"[OK] VSCode configuration complete in {Path(output_dir) / '.vscode'}")


def generate_all_pycharm(
    project_name: str,
    env_type: str = "local",
    config_file: Optional[str] = None,
    venv_path: str = ".venv",
    output_dir: str = ".",
) -> None:
    """Generate all PyCharm configuration files."""
    print(f"\n[INFO] Generating PyCharm configuration for: {project_name}")

    if env_type == "docker":
        generate_pycharm_docker_config(project_name, output_dir)
    else:
        generate_pycharm_local_config(
            project_name,
            config_file or "odoo.conf",
            venv_path,
            output_dir,
        )

    generate_pycharm_misc_xml(output_dir)
    print(f"[OK] PyCharm configuration complete in {Path(output_dir) / '.idea'}")


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="IDE Configuration Generator for Odoo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ide_configurator.py --ide vscode --env local --config TAQAT17.conf
  python ide_configurator.py --ide pycharm --env docker --project myproject
  python ide_configurator.py --ide both --env local --project myproject --config TAQAT17.conf
  python ide_configurator.py --gitignore-only
  python ide_configurator.py --env-example-only --project myproject
        """
    )

    parser.add_argument(
        "--ide",
        choices=["vscode", "pycharm", "both"],
        default="both",
        help="IDE to generate config for"
    )
    parser.add_argument(
        "--env",
        choices=["local", "docker"],
        default="local",
        help="Environment type"
    )
    parser.add_argument("--project", "-p", help="Project name")
    parser.add_argument("--config", "-c", help="Odoo config filename (e.g. TAQAT17.conf)")
    parser.add_argument("--venv", default=".venv", help="Virtual environment path")
    parser.add_argument("--output", "-o", default=".", help="Output directory")
    parser.add_argument("--gitignore-only", action="store_true", help="Only generate .gitignore")
    parser.add_argument("--env-example-only", action="store_true", help="Only generate .env.example")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    project = args.project or "myproject"

    if args.gitignore_only:
        generate_gitignore(args.output)
        return

    if args.env_example_only:
        generate_env_example(project, args.output)
        return

    # Generate .gitignore and .env.example always
    generate_gitignore(args.output)
    generate_env_example(project, args.output)

    if args.ide in ("vscode", "both"):
        generate_all_vscode(
            project_name=project,
            config_file=args.config,
            venv_path=args.venv,
            output_dir=args.output,
        )

    if args.ide in ("pycharm", "both"):
        generate_all_pycharm(
            project_name=project,
            env_type=args.env,
            config_file=args.config,
            venv_path=args.venv,
            output_dir=args.output,
        )

    print(f"\n[DONE] IDE configuration generated in: {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
