# Flask CI/CD — Jenkins · GitLab CI · Docker · Ansible · AWS

Pipeline CI/CD complet pour une application Python Flask : qualité de code, tests, build d'image Docker, publication sur Docker Hub et déploiement automatisé sur AWS EC2 avec Ansible.

Basé sur [bennzhang/docker-demo-with-simple-python-app](https://github.com/bennzhang/docker-demo-with-simple-python-app), modernisé (Python 2.7 → 3.12, image slim, utilisateur non-root, tests, health check).

## Pipeline

```
Code → Qualité (flake8) → Tests (pytest) → Build image → Test image → Push Docker Hub → Deploy staging → Validation → Deploy production (manuel)
```

## Stack

| Outil | Rôle |
|---|---|
| Flask + Gunicorn | Application web |
| Docker | Conteneurisation |
| Jenkins | Orchestration CI/CD |
| Docker Hub | Registre d'images |
| Ansible | Déploiement sur les serveurs |
| AWS EC2 | Environnements staging et production |

## Structure

```
.
├── main.py              # Application Flask (/ et /health)
├── gunicorn.conf.py
├── requirements.txt
├── requirements-dev.txt # pytest, flake8
├── tests/test_main.py
├── Dockerfile
├── Jenkinsfile
├── .gitlab-ci.yml
└── ansible/
    ├── inventory.ini    # IP des serveurs staging / production
    └── deploy.yml       # Installe Docker, pull l'image, lance le conteneur
```

## Lancer en local

```bash
docker build -t flask-app .
docker run -d -p 8080:8080 flask-app
curl http://localhost:8080          # Hello World
curl http://localhost:8080/health   # {"status":"ok"}
```

## Configuration Jenkins

Plugins : Pipeline, Docker Pipeline, SSH Agent, Credentials Binding. Ansible et Docker doivent être installés sur l'agent Jenkins.

Credentials à créer :
- `dockerhub-creds` : Username/password Docker Hub (utiliser un access token)
- `aws-ssh-key` : clé privée SSH (.pem) des instances EC2

À remplacer : `DOCKERHUB_USER` et `STAGING_IP` dans le Jenkinsfile, les IP dans `ansible/inventory.ini`.

## Configuration GitLab CI (gitlab.com)

Variables à créer dans *Settings → CI/CD → Variables* :
- `DOCKERHUB_USER`
- `DOCKERHUB_TOKEN` (masquée)
- `STAGING_IP`, `PROD_IP`
- `SSH_PRIVATE_KEY` (type **File**, contenu de la clé .pem)

Le déploiement en production se déclenche manuellement depuis l'interface GitLab.

## Jenkins vs GitLab CI

| | Jenkins | GitLab CI |
|---|---|---|
| Hébergement | À installer et maintenir | Runners partagés sur gitlab.com |
| Configuration | Jenkinsfile (Groovy) | .gitlab-ci.yml (YAML) |
| Secrets | Credentials Jenkins | Variables CI/CD |
| Docker | Docker de l'agent | Docker-in-Docker |
| Validation prod | `input` | `when: manual` |

## Infrastructure AWS

- 2 instances EC2 Ubuntu (free tier) : staging et production
- Security group : port 22 (limité à mon IP) et port 80

## Améliorations possibles

- Provisionner les instances avec Terraform
- Scan de sécurité de l'image (Trivy)
- Notifications Slack
