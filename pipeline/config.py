import kfp.dsl as dsl

class Config:
    ENDPOINT = 'http://{HOST_IP}:{PORT}/pipeline'
    NAMESPACE = {NAMESPACE}
    COOKIES = 'authservice_session={COOKIES}'

    PVC = dsl.PipelineVolume('pipeline-volume')
    SHM_VOLUME = dsl.PipelineVolume(name='shm-vol', empty_dir={'medium': 'Memory'})