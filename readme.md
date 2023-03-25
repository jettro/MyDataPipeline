# Docker issues with Opensearch

Create the following file:
/Users/jettrocoenradie/Library/Application Support/rancher-desktop/lima/_config/override.yaml

```yaml
provision:
- mode: system
  script: |
    #!/bin/sh
    set -o xtrace
    sysctl -w vm.max_map_count=262144
    cat <<'EOF' > /etc/security/limits.d/rancher-desktop.conf
    * soft     nofile         82920
    * hard     nofile         82920
    EOF
```

You can test using curl, for now we do not check the certificate:
```bash
curl https://localhost:9200 -ku admin:admin
```

# References
Just some articles I used

## Setting up Docker/Opensearch
https://opster.com/guides/opensearch/opensearch-basics/spin-up-opensearch-cluster-with-docker/
