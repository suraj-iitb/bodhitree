# Folder Structure

Django App Name | Purpose
------------ | -------------
registration | All user related functionalities like login, signup, profile, plans etc.
course | All course related functionalities like creation, people management, chapter, section, schedule, settings, notifications etc
video | All video related functionalities
quiz |  All quiz related functionalities
document |  All document functionalities
discussion_forum | All discussion forum realted functionalities
email_notices | All email realted functionalities
cribs | All cribs realted functionalities
leaderboard | All marks related functionalities
stats | All statistics related to a course
programming_assignments | All programming assignments related functionalities
subjective_assignments | All subjective assignments related functionalities

Folder/File | Purpose
------------ | -------------
main | Django project folder
utils | Utility functions & classes
.github | CI/CD workflows, issue templates for github
.vscode | Vscode settings & configurations like debugger setup inside docker container
.images | Utility images  for markdown files
.dockerignore | Dockerignore file
.gitignore | Gitignore file
.flake8 | Flake configurations (Style Guide Enforcement)
.pre-commit-config.yaml | Configuration file for pre-commit hooks
pyproject.toml | Configuration file for black & isort
.env | Environment variable file
Dockefile | Dockerfile to build backend image
docker-compose.yml | Base docker compose file which contains common docker services configurations
docker-compose.debug.yml | Debug/Development docker compose file which contains debug/development docker services configurations
docker-compose.test.yml | Test docker compose file which contains test docker services configurations
docker-compose.prod.yml | Production docker compose file which contains production docker services configurations
manage.py | Django's command-line utility for administrative tasks
requirements.txt | Dependencies required by the project
requirements.dev.txt | Extra development dependencies required by the project
README.md | Project readme file
CODE_STRUCTURE.md | Code Structure readme file
