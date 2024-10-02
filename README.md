# Kotaemon Docker Compose OIDC
## Persistent deployment configuration for Kotaemon that utilizes OIDC for authentication

# 👋🏻 Introduction
Utilizes FastAPI to create an OIDC wrapper around Kotaemon ( https://github.com/Cinnamon/kotaemon )
Can be deployed using docker compose after setting a few variables in the docker-compose.yml.

# 👨🏻‍💻 Run from your local machine
1. Clone the repo, then cd into the kotaemon-docker-compose-oidc directory.
2. Edit the docker-compose.yml to update the OIDC related environment variables
3. Run "docker compose up -d" to launch the container
4. Browse to http://localhost:8000/

# 🔑 Environment variables (set in docker-compose.yml)
| Setting                          | Value              | Note                                                                                                                                   |
| -------------------------------- | ------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| SECRET_KEY                       |                    | Random value to secure session                                                                                                         |
| OPENID_CLIENT_ID                 |                    | Client ID provided by your IdP                                                                                                         |
| OPENID_CLIENT_SECRET             |                    | Secret provided by your IdP                                                                                                            |
| OPENID_CONFIG_URL                |                    | URL to the open ID metadata configuration resource                                                                                     |

