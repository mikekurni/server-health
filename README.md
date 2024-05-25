# Staging Server Health Status Checkers

A proof of concept (PoC) tool for monitoring server health status of staging/sandbox web app server. Using Python Streamlit, DETA BASE for the NoSQL like database, and DISCORD Webhook to notifies the DevOps team.

This tool will check and save the log records data of staging/sanbox server in 5 minutes interval. When the staging server returning responses other than status code of 200 and/or 204 it will triggred a function to send notifications through Discord webhook.