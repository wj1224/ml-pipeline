from datetime import datetime
import kfp
import kfp.dsl as dsl
import kfp.gcp as gcp
    
from config import Config
from download_dataset import DownloadDataset
from train_with_best_params import TrainWithBestParams

if __name__ == "__main__":
    cfg = Config

    exp_name = pipeline_name = "ml-pipeline_test"
    download_path = "/mnt/data"
    base_dir = download_path + "/coco_captioning"

    @dsl.pipeline(
        name=pipeline_name
        )
    def pipeline_func():        
        op_dataset_download = DownloadDataset()(download_path)
            
        op_hypertune = dsl.ContainerOp(
            name="Hyperparams tuning",
            image="submit-katib:latest",
            arguments=["--yaml", "/mnt/katib_yaml/katib-example.yaml"],
            file_outputs={'output': '/tmp/output'}
            )
            
        op_train = TrainWithBestParams()(op_hypertune.output, cfg.NAMESPACE, base_dir)

        op_hypertune.after(op_dataset_download)
        op_train.after(op_hypertune)

        for op in [op_dataset_download, op_hypertune, op_train]:
            op.add_pvolumes({'/mnt': cfg.PVC, "/dev/shm": cfg.SHM_VOLUME})
            op.container.set_image_pull_policy("Never")
            op.apply(gcp.use_gcp_secret("gs-key", secret_file_path_in_volume="/gs_key.json"))

            op.execution_options.caching_strategy.max_cache_staleness = "P0D"
            
    client = kfp.Client(host=cfg.ENDPOINT, namespace=cfg.NAMESPACE, cookies=cfg.COOKIES)

    client.create_run_from_pipeline_func(
        pipeline_func,
        run_name=datetime.now().strftime('%y.%m.%d-%H:%M:%S'),
        experiment_name=exp_name,
        arguments={},
        namespace=cfg.NAMESPACE
        )