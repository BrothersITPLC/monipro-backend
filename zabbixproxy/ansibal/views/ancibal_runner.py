# ansibal/views/ansibal_runner.py
import logging
import os
import tempfile

import ansible_runner
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

ansible_logger = logging.getLogger("ansibal")
from utils import ServiceErrorHandler
from zabbixproxy.ansibal.serializers import AnsibleRequestSerializer


class AnsibleDeployView(APIView):
    def post(self, request):
        try:
            serializer = AnsibleRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            ansible_logger.info(f"Starting deployment to {data['target_host']}")

            with tempfile.NamedTemporaryFile(mode='w+', delete=True) as inv_file:
                inv_content = f"""
                [target]
                {data['target_host']}
                
                [target:vars]
                ansible_user={data['username']}
                ansible_ssh_pass={data['password']}
                ansible_become_pass={data['password']}
                ansible_python_interpreter=/usr/bin/python3
                ansible_ssh_common_args='-o StrictHostKeyChecking=no -o ConnectTimeout=30'
                """
                inv_file.write(inv_content.strip())
                inv_file.flush()

                ansible_logger.debug(f"Inventory content:\n{inv_content}")


                runner = ansible_runner.run(
                    playbook=settings.PLAYBOOK_PATH,
                    inventory=inv_file.name,
                    extravars={'nginx_host_port': data['port']},
                    quiet=False,  # Set to False to capture output
                    json_mode=False,
                    suppress_env_files=True
                )

                ansible_logger.info(f"Ansible run completed with status: {runner.status}")
                ansible_logger.debug(f"Ansible events: {runner.events}")
                ansible_logger.debug(f"Ansible stdout:\n{runner.stdout.read()}")
                return self._format_response(runner, data['target_host'])

        except Exception as e:
            ansible_logger.exception("An error occurred during deployment")
            raise Response(
                {
                    "error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _format_response(self, runner, target_host):
        success = runner.status == 'successful'
        tasks = []
        errors = []

        for event in runner.events:
            if event['event'] in ['runner_on_ok', 'runner_on_failed']:
                task = event['event_data'].get('task', 'Unknown Task')
                result = event['event_data']['res']
                
                if event['event'] == 'runner_on_ok':
                    tasks.append({
                        'task': task,
                        'status': 'success',
                        'details': result.get('msg', 'Task completed')
                    })
                else:
                    error_msg = self._sanitize_error(result.get('msg', 'Unknown error'))
                    errors.append({
                        'task': task,
                        'error': error_msg
                    })

        response = {
            'host': target_host,
            'overall_success': success,
            'executed_tasks': tasks,
            'errors': errors,
            'stats': {
                'total_tasks': len(tasks) + len(errors),
                'successful': len(tasks),
                'failed': len(errors)
            }
        }

        status_code = status.HTTP_200_OK if success else status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(response, status=status_code)

    def _sanitize_error(self, error):
        sensitive_terms = ['password', 'sudo', 'ssh']
        error = str(error)
        for term in sensitive_terms:
            if term in error.lower():
                return "Authentication or privilege error occurred"
        return error.split('\n')[0][:100] 


