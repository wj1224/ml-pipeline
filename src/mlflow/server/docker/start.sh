#!/bin/sh

if [ $# -eq 0 ] || [ $# -ge 2 ] ; then
    echo "Only one argument is possible"
    exit 0
fi

cond=${1}

if [ "${cond}" == "--remote" ] ; then
    export BACKEND_STORE=mysql+mysqldb://$MYSQL_USERNAME:$MYSQL_PASSWORD@mysqldb-svc.mysqldb.svc.cluster.local:3306/mlflow
    export ARTIFACT_STORE=gs://ml-pipeline-example-mlflow/artifacts/
elif [ "${cond}" == "--local" ] ; then
    MOUNT_PATH=/mnt/mlflow
    export BACKEND_STORE=file://$MOUNT_PATH/mlruns
    export ARTIFACT_STORE=$MOUNT_PATH/mlruns
    cd $MOUNT_PATH
else
    echo "ERROR: Choose [--remote, --local] between the two"
    exit 0
fi

mlflow server \
    --backend-store-uri $BACKEND_STORE \
    --default-artifact-root $ARTIFACT_STORE \
    --host $SERVER_HOST \
    --port $SERVER_PORT \
    > $MLFLOW_HOME/backend_server.log 2>&1 &

mlflow ui
