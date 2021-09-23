import kfp.components as comp

def download_dataset(
    path: str
):
    import os
    import zipfile
    import wget

    if not os.path.exists(path):
        os.makedirs(path)
    wget.download(url="http://cs231n.stanford.edu/coco_captioning.zip", out=path)
    file_path = os.path.join(path, "coco_captioning.zip")

    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(path)

    if os.path.isfile(file_path):
        os.remove(file_path)

def DownloadDataset():
    return comp.func_to_container_op(
        func=download_dataset, 
        base_image='python:3.8.2-slim-buster',
        packages_to_install=['wget']
    )

if __name__ == "__main__":
    from datetime import datetime
    import kfp
    import kfp.dsl as dsl
    
    from config import Config

    cfg = Config

    exp_name = pipeline_name = "download_dataset_test"
    download_path = "/mnt/data"
 
    @dsl.pipeline(
        name=pipeline_name
    )
    def pipeline_func():        
        op_dataset_download = DownloadDataset()(download_path)
        op_dataset_download.add_pvolumes({'/mnt': cfg.PVC, "/dev/shm": cfg.SHM_VOLUME})

    client = kfp.Client(host=cfg.ENDPOINT, namespace=cfg.NAMESPACE, cookies=cfg.COOKIES)

    client.create_run_from_pipeline_func(
        pipeline_func,
        run_name=datetime.now().strftime('%y.%m.%d-%H:%M:%S'),
        experiment_name=exp_name,
        arguments={},
        namespace=cfg.NAMESPACE
    )