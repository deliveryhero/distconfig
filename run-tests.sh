#!/bin/bash -e

set_up() {
  abort_if_no_docker
  create_docker_containers
  export_services_endpoint
}

abort_if_no_docker() {
  (hash docker 2> /dev/null) || (echo "Docker is needed to run tests ... quitting"; exit 1)
}

create_docker_containers() {
  echo "Starting consul container ..."
  CONSUL_CONTAINER_ID=$(docker run -d -p 8400:8400 -p 8500:8500 -p 8600:53/udp -h node1 progrium/consul -server -bootstrap)

  echo "Starting etcd container ..."
  ETCD_CONTAINER_ID=$(docker run -d -p 4001:4001 quay.io/coreos/etcd:v0.4.6)

  echo "Starting zookeeper container ..."
  ZOOKEEPER_CONTAINER_ID=$(docker run -d -p 2181:2181 jplock/zookeeper:3.4.6)

}

export_services_endpoint() {
  if hash boot2docker 2>/dev/null; then
    local ip=$(boot2docker ip)

    export CONSUL_ENDPOINT_IP=$ip
    export ETCD_ENDPOINT_IP=$ip
    export ZOOKEEPER_ENDPOINT_IP=$ip
  fi
}

run_tests() {
  echo "Running tests ..."
  set +e
  export DISTCONFIG_RUN_INTEGRATION_TEST=true
  tox "$@"
  set -e
}

tear_down() {
  echo "Destroying containers ..."
  docker stop $ETCD_CONTAINER_ID $ZOOKEEPER_CONTAINER_ID $CONSUL_CONTAINER_ID
}

set_up
run_tests "$@"
tear_down
