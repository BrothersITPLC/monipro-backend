
```
monipro-backend
├─ agents
│  ├─ admin.py
│  ├─ agent
│  │  ├─ insight_agent.py
│  │  └─ __init__.py
│  ├─ apps.py
│  ├─ migrations
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ tests.py
│  ├─ tools
│  │  ├─ format_alert_tool.py
│  │  └─ __init__.py
│  ├─ urls.py
│  ├─ views
│  │  ├─ alert_insight.py
│  │  └─ __init__.py
│  └─ __init__.py
├─ customers
│  ├─ admin.py
│  ├─ apps.py
│  ├─ migrations
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ serializers
│  │  ├─ organization_info.py
│  │  ├─ payment_update.py
│  │  └─ __init__.py
│  ├─ tests.py
│  ├─ urls.py
│  ├─ views
│  │  ├─ organization_info.py
│  │  ├─ payment_update.py
│  │  └─ __init__.py
│  └─ __init__.py
├─ customers.json
├─ docker-compose.yml
├─ Dockerfile
├─ entrypoint.sh
├─ item_types
│  ├─ admin.py
│  ├─ apps.py
│  ├─ migrations
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ serializers
│  │  ├─ agent_based_items_type.py
│  │  ├─ monitoring_category.py
│  │  ├─ simple_check_item_types.py
│  │  └─ __init__.py
│  ├─ tests.py
│  ├─ urls.py
│  ├─ views
│  │  ├─ agent_based_items_type.py
│  │  ├─ monitoring_category.py
│  │  ├─ simple_check_item_types.py
│  │  └─ __init__.py
│  └─ __init__.py
├─ jobs
│  ├─ admin.py
│  ├─ apps.py
│  ├─ functions
│  │  ├─ delete_old_zabbix_token.py
│  │  └─ __init__.py
│  ├─ migrations
│  │  └─ __init__.py
│  └─ __init__.py
├─ logs
│  └─ filebeat-20250528.ndjson
├─ manage.py
├─ middleware
│  ├─ authmiddleware.py
│  ├─ user_add_limit.py
│  └─ __init__.py
├─ monipro
│  ├─ asgi.py
│  ├─ celery.py
│  ├─ settings.py
│  ├─ urls.py
│  ├─ wsgi.py
│  └─ __init__.py
├─ payment
│  ├─ admin.py
│  ├─ apps.py
│  ├─ functions
│  │  ├─ chapa_initialization.py
│  │  ├─ chapa_verification.py
│  │  └─ __init__.py
│  ├─ migrations
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ serializers
│  │  ├─ chapa_initialization.py
│  │  └─ __init__.py
│  ├─ tests.py
│  ├─ urls.py
│  ├─ views
│  │  ├─ chapa_initialization.py
│  │  ├─ chapa_verification.py
│  │  └─ __init__.py
│  └─ __init__.py
├─ requirements.txt
├─ users
│  ├─ admin.py
│  ├─ apps.py
│  ├─ migrations
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ serializers
│  │  ├─ activate_deactivate.py
│  │  ├─ add_user.py
│  │  ├─ change_password.py
│  │  ├─ forgot_password.py
│  │  ├─ get_team_users.py
│  │  ├─ initial_registration.py
│  │  ├─ login.py
│  │  ├─ profile_picture_update.py
│  │  ├─ reset_password.py
│  │  ├─ team_user_by_organization.py
│  │  ├─ update_profile.py
│  │  ├─ user_profile.py
│  │  ├─ verify_registration_otp.py
│  │  └─ __init__.py
│  ├─ serializers.py
│  ├─ tests.py
│  ├─ urls.py
│  ├─ views
│  │  ├─ activate_deactivate.py
│  │  ├─ add_user.py
│  │  ├─ change_password.py
│  │  ├─ forgot_password.py
│  │  ├─ get_team_users.py
│  │  ├─ google_exchange.py
│  │  ├─ initial_registration.py
│  │  ├─ login.py
│  │  ├─ logout.py
│  │  ├─ profile_picture_update.py
│  │  ├─ reset_password.py
│  │  ├─ team_user.py
│  │  ├─ team_user_by_organization.py
│  │  ├─ update_profile.py
│  │  ├─ user_profile.py
│  │  ├─ verify_registration_otp.py
│  │  └─ __init__.py
│  └─ __init__.py
├─ utils
│  ├─ bulk_sms.py
│  ├─ error_handler.py
│  ├─ otp_send_email.py
│  ├─ password_reset_email.py
│  ├─ random_password.py
│  ├─ single_sms.py
│  ├─ team_user_email.py
│  └─ __init__.py
└─ zabbixproxy
   ├─ admin.py
   ├─ alert_functions
   │  ├─ get_alert.py
   │  ├─ get_single_alert.py
   │  └─ __init__.py
   ├─ apps.py
   ├─ automation_functions
   │  ├─ ansibal_playbooks
   │  │  ├─ zabbix-playbook.yml
   │  │  └─ __init__.py
   │  ├─ ansibal_runner.py
   │  └─ __init__.py
   ├─ check_reachability_functions
   │  ├─ check_reachability.py
   │  └─ __init__.py
   ├─ credentials_functions
   │  ├─ create_host_group.py
   │  ├─ create_user.py
   │  ├─ create_user_group.py
   │  ├─ zabbiz_login.py
   │  └─ __init__.py
   ├─ host_functions
   │  ├─ host_creat.py
   │  ├─ simple_check_host_creat.py
   │  └─ __init__.py
   ├─ host_items_functions
   │  ├─ item_content_function.py
   │  ├─ item_list_function.py
   │  └─ __init__.py
   ├─ item_functions
   │  ├─ item_creat_functions.py
   │  ├─ simple_check_item_params.py
   │  └─ __init__.py
   ├─ item_template_functions
   │  ├─ items_simple_check.py
   │  └─ __init__.py
   ├─ migrations
   │  └─ __init__.py
   ├─ models.py
   ├─ serializers
   │  ├─ ansibal_runner.py
   │  ├─ host_create.py
   │  ├─ host_list.py
   │  ├─ zabbix_user.py
   │  └─ __init__.py
   ├─ tasks
   │  ├─ agent_deployment.py
   │  ├─ host_creation.py
   │  ├─ host_interfaceid.py
   │  ├─ host_record.py
   │  ├─ simple_check_workflow.py
   │  ├─ workflow.py
   │  └─ __init__.py
   ├─ tasks.py
   ├─ template_functions
   │  ├─ simple_check_template.py
   │  └─ __init__.py
   ├─ tests.py
   ├─ urls.py
   ├─ views
   │  ├─ ancibal_runner.py
   │  ├─ check_reachability.py
   │  ├─ create_host.py
   │  ├─ create_host_v1.py
   │  ├─ create_simple_check_zabbix_host.py
   │  ├─ create_template.py
   │  ├─ create_user.py
   │  ├─ create_user_and_host_group.py
   │  ├─ get_hosts.py
   │  └─ __init__.py
   └─ __init__.py

```