from datetime import datetime
import kfp
import kfp.dsl as dsl

from config import Config

if __name__ == "__main__":
    cfg = Config

    exp_name = pipeline_name = "hyperparamets_tuning_test"
    docker_image = "submit-katib:latest"
 
    @dsl.pipeline(
        name=pipeline_name
    )
    def pipeline_func():        
        op_hypertune = dsl.ContainerOp(
            name=exp_name,
            image=docker_image,
            arguments=["--yaml", "/mnt/katib_yaml/katib-example.yaml"],
            pvolumes={'/mnt': cfg.PVC, "/dev/shm": cfg.SHM_VOLUME},
            file_outputs={'output': '/tmp/output'}
            )
        op_hypertune.container.set_image_pull_policy("Never")

    client = kfp.Client(host=cfg.ENDPOINT, namespace=cfg.NAMESPACE, cookies=cfg.COOKIES)

    client.create_run_from_pipeline_func(
        pipeline_func,
        run_name=datetime.now().strftime('%y.%m.%d-%H:%M:%S'),
        experiment_name=exp_name,
        arguments={},
        namespace=cfg.NAMESPACE
    )