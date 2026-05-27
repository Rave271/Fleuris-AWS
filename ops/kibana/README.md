# Kibana Starter Dashboards

Create the following visualizations after Filebeat is ingesting logs:

## Dashboards

- Request volume over time (event_type=http_request)
- Login trends (event_type=LOGIN_SUCCESS, LOGIN_FAILED, MFA_FAILED)
- Endpoint popularity (terms on endpoint)
- HTTP status distribution (terms on status_code)
- Response time trends (avg response_time_ms)
- Transfer activity (event_type=TRANSFER_CREATED)

## Recommended Filters

- event_type: http_request
- status_code >= 400
- endpoint: /transfer, /login, /dashboard

Save each visualization and combine into a single "Fleuris Vault Ops" dashboard.
