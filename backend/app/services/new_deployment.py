from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from app.config import settings

MCP_DEPLOYMENT_NAMESPACE = settings.mcp_deployment_namespace

# gerar os arquivos de implantacao
def check_k8s_namespace_exists(namespace: str) -> bool:
    try:
        import subprocess

        process = subprocess.Popen(
            f"kubectl get namespace {namespace}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        pid = process.pid
        stdout, stderr = process.communicate()
        if "NotFound" in stderr:
            return False
        return True
    except Exception as erro:
        return False

def check_k8s_deployment_exists(deployment_name: str, namespace: str = MCP_DEPLOYMENT_NAMESPACE) -> bool:
    try:
        import subprocess

        process = subprocess.Popen(
            f"kubectl get deployment {deployment_name} -n {namespace}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate()
        if "NotFound" in stderr:
            return False
        return True
    except Exception as erro:
        return False

def create_k8s_default_mcp_namespace() -> bool:
    try:
        import subprocess

        process = subprocess.Popen(
            f"kubectl create namespace {MCP_DEPLOYMENT_NAMESPACE}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        pid = process.pid
        stdout, stderr = process.communicate()
        if "AlreadyExists" in stderr:
            return False
        return True
    except Exception as erro:
        return False

def generate_k8s_deployment_file(
    deployment_name: str,
    image: str,
    replicas: int = 1,
    container_port: int = 80,
    namespace: str = MCP_DEPLOYMENT_NAMESPACE,
) -> bool:
    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": deployment_name, "namespace": namespace},
        "spec": {
            "replicas": replicas,
            "selector": {"matchLabels": {"app": deployment_name}},
            "template": {
                "metadata": {"labels": {"app": deployment_name}},
                "spec": {
                    "containers": [
                        {
                            "name": deployment_name,
                            "image": image,
                            "ports": [{"containerPort": container_port}],
                        }
                    ]
                },
            },
        },
    }
    yaml.dump(deployment, sort_keys=False)
    default_deployment_path = Path(settings.deployments_files_dir) / f"{deployment_name}_deployment.yaml"
    try:
        with open(default_deployment_path, "w") as file:
            file.write(yaml.dump(deployment))
        return True, default_deployment_path
    except Exception as erro:
        return False, None

def generate_k8s_service_file(
    service_name: str,
    service_port: int = 80,
    target_port: int = 80,
    namespace: str = MCP_DEPLOYMENT_NAMESPACE
) -> bool:
    service = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": service_name, "namespace": namespace},
        "spec": {
            "selector": {"app": service_name},
            "ports": [{"protocol": "TCP", "port": service_port, "targetPort": target_port}],
            "type": "LoadBalancer",
        },
    }
    default_deployment_path = Path(settings.deployments_files_dir) / f"{service_name}_service.yaml"
    try:
        with open(default_deployment_path, "w") as file:
            file.write(yaml.dump(service))
        return True, default_deployment_path
    except Exception as erro:
        return False, None

def generate_k8s_ingress_file(
    ingress_name: str,
    host: str,
    service_name: str,
    service_port: int = 80,
    namespace: str = MCP_DEPLOYMENT_NAMESPACE
) -> bool:
    ingress = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {"name": ingress_name, "namespace": namespace},
        "spec": {
            "rules": [
                {
                    "host": host,
                    "http": {
                        "paths": [
                            {
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {"name": service_name, "port": {"number": service_port}}
                                },
                            }
                        ]
                    },
                }
            ]
        },
    }
    try:
        default_deployment_path = Path(settings.deployments_files_dir) / f"{ingress_name}_ingress.yaml"
        with open(default_deployment_path, "w") as file:
            file.write(yaml.dump(ingress))
        return True, default_deployment_path
    except Exception as erro:
        return False, None
    
def generate_k8s_configmap_file(
    configmap_name: str,
    data: dict,
    namespace: str = MCP_DEPLOYMENT_NAMESPACE
) -> bool:
    configmap = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {"name": configmap_name, "namespace": namespace},
        "data": data,
    }
    try:
        default_deployment_path = Path(settings.deployments_files_dir) / f"{configmap_name}_configmap.yaml"
        with open(default_deployment_path, "w") as file:
            file.write(yaml.dump(configmap))
        return True, default_deployment_path
    except Exception as erro:
        return False, None

def generate_k8s_secret_file(
    secret_name: str,
    data: dict,
    namespace: str = MCP_DEPLOYMENT_NAMESPACE
) -> bool:
    secret = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {"name": secret_name, "namespace": namespace},
        "data": data,
    }
    try:
        default_deployment_path = Path(settings.deployments_files_dir) / f"{secret_name}_secret.yaml"
        with open(default_deployment_path, "w") as file:
            file.write(yaml.dump(secret))
        return True, default_deployment_path
    except Exception as erro:
        return False, None

def apply_k8s_file(k8s_config_file_path: str) -> bool:
    try:
        import subprocess

        process = subprocess.Popen(
            f"kubectl apply -f {k8s_config_file_path}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        pid = process.pid
        stdout, stderr = process.communicate()
        # TODO: apurar falha no kubectl
        
        return True
    except Exception as erro:
        return False

def perform_k8s_deployment(
    deployment_name: str,
    image: str,
    replicas: int = 1,
    container_port: int = 80,
    service_port: int = 80,
    ingress_host: str | None = None,
    envorinment_variables: dict | None = None,
    secret_variables: dict | None = None,
) -> bool:
    if not check_k8s_namespace_exists(MCP_DEPLOYMENT_NAMESPACE):
        create_k8s_default_mcp_namespace()

    generate_files = []
    try:
        generated, path = generate_k8s_deployment_file(deployment_name, image, replicas, container_port)
        if generated:
            apply_k8s_file(path)
            generate_files.append(path)
        generated, path = generate_k8s_service_file(deployment_name, service_port, container_port)
        if generated:
            apply_k8s_file(path)
            generate_files.append(path)
        if ingress_host:
            generated, path = generate_k8s_ingress_file(deployment_name, ingress_host, deployment_name, service_port)
            if generated:
                apply_k8s_file(path)
                generate_files.append(path)
        if envorinment_variables:
            generated, path = generate_k8s_configmap_file(f"{deployment_name}-config", envorinment_variables)
            if generated:
                apply_k8s_file(path)
                generate_files.append(path)
        if secret_variables:
            generated, path = generate_k8s_secret_file(f"{deployment_name}-secret", secret_variables)
            if generated:
                apply_k8s_file(path)
                generate_files.append(path)
        # TODO: informar sucesso da implantacao
        
    except Exception as erro:
        for generate_file_path in generate_files:
            import os
            os.remove(generate_file_path)
        # TODO: informar falha da implantacao

# aplicar arquivos de implantacao