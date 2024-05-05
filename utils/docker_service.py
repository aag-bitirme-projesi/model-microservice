import docker
import socket

import docker.errors

class DockerService:
    
    def __init__(self):
        self.client = docker.from_env()
    
    def run_docker_container(self, image_name):
        port = self.find_port()
        if not port:
            raise ValueError("No available ports right now, please try again later")
        port_mapping = {"5000/tcp": port}
        
        try:
            container = self.client.containers.run(image_name, ports=port_mapping, detach=True)
            return container.id, port
        except docker.errors.APIError as e:
            raise ValueError("Error occurred while running container.")
    
    def stop_docker_container(self, container_id):
        try:
            container = self.client.containers.get(container_id)
            container.stop()
        except docker.errors.NotFound:
            raise ValueError("Container not found.")
        except docker.errors.APIError as e:
            raise ValueError("Error occurred while stopping container.")
        
    def remove_docker_container(self, container_id):
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=True)
        except docker.errors.NotFound:
            raise ValueError("Container not found.")
        except docker.errors.APIError:
            raise ValueError("Error occured while removing container.")
    
    def find_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
        # for port in range(5001, 5501):
        #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #         try:
        #             # s.bind(('localhost', port))
        #             return port
        #         except OSError:
        #             continue
        # return None
