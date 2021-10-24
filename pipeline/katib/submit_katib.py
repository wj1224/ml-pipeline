import argparse
import time
import yaml
from kubernetes import client, config, watch

class SubmitKatib:
    def __init__(self, yaml_path):
        self.yaml_path = yaml_path
        
        config.load_incluster_config()
        self.api = client.CustomObjectsApi()

        self.group = "kubeflow.org"
        self.version = "v1beta1"
        self.namespace = {NAMESPACE}
        self.plural = "experiments"

    def submit(self):
        with open(self.yaml_path) as f:
            dep = yaml.safe_load(f)
            self.name = dep['metadata']['name'] + '-' + str(int(time.time())) 
            dep['metadata']['name'] = self.name
            with open("/tmp/output", "w") as f:
                f.write(self.name)

            api_response = self.api.create_namespaced_custom_object(group=self.group, plural=self.plural, version=self.version, namespace=self.namespace, body=dep)
            print(api_response)

    def condition(self):
        return self.api.get_namespaced_custom_object_status(group=self.group, version=self.version, plural=self.plural, namespace=self.namespace, name=self.name)['status']['conditions'][-1]['type']

    def watch(self):
        w = watch.Watch()

        for event in w.stream(self.api.list_namespaced_custom_object, group=self.group, version=self.version, plural=self.plural, namespace=self.namespace):
            if not isinstance(event['object']['metadata']['name'], type(None)):
                exp_name = event['object']['metadata']['name']
                if 'status' in event['object'].keys():
                    exp_response = event['object']['status']['conditions'][-1]['type']
                else:
                    continue
                if exp_name == self.name:
                    print(exp_name, exp_response)
                    if exp_response == 'Succeeded':
                        w.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--yaml", type=str, required=True, default=None, help="katib job yaml file path")
    args = parser.parse_args()

    target = args.yaml

    katib = SubmitKatib(target)
    katib.submit()
    katib.watch()
