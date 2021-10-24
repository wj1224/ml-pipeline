import kfp.components as comp

def train_with_best_params(
    exp_name: str,
    namespace: str,
    base_dir: str
):
    import subprocess
    import kubeflow.katib as katib
    

    kclient = katib.KatibClient()
    api_response = kclient.get_optimal_hyperparameters(name=exp_name, namespace=namespace)['currentOptimalTrial']
    best_params = ' '.join(f'--{params["name"]} {params["value"]}' for params in api_response['parameterAssignments'])

    subprocess.run(['sh', '-c', f"""python train.py --tracking --max-train 5000 --epochs 200 --base-dir {base_dir} {best_params}"""])

def TrainWithBestParams():
    return comp.func_to_container_op(
        func=train_with_best_params, 
        base_image='image_captioning:latest',
        packages_to_install=['kubeflow-katib']
    )

if __name__ == "__main__":
    from datetime import datetime
    import kfp
    import kfp.dsl as dsl
    import kfp.gcp as gcp
    
    from config import Config

    cfg = Config

    exp_name = pipeline_name = "train_with_best_params_test"
 
    @dsl.pipeline(
        name=pipeline_name
    )
    def pipeline_func():        
        op_train = TrainWithBestParams()("katib-example-1632038258", cfg.NAMESPACE, "/mnt/data/coco_captioning")
        op_train.add_pvolumes({'/mnt': cfg.PVC, "/dev/shm": cfg.SHM_VOLUME})
        op_train.container.set_image_pull_policy("Never")
        op_train.apply(gcp.use_gcp_secret("gs-key", secret_file_path_in_volume="/gs_key.json"))

    client = kfp.Client(host=cfg.ENDPOINT, namespace=cfg.NAMESPACE, cookies=cfg.COOKIES)

    client.create_run_from_pipeline_func(
        pipeline_func,
        run_name=datetime.now().strftime('%y.%m.%d-%H:%M:%S'),
        experiment_name=exp_name,
        arguments={},
        namespace=cfg.NAMESPACE
    )