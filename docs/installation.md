# Installation

The easiest way to get up and running is with [Docker Compose](https://docs.docker.com/compose). The default option for data storage is in memory. If you would like to persist data beyond container restarts you must set up a [Redis](https://redis.io/) instance.

## Example configuration

Below is a sample `docker-compose.yml` that will spin up linktiles and a redis container for persistence.

```yaml title='docker-compose.yml'
services:
  linktiles:
    image: haumea/linktiles:latest
    container_name: linktiles
    networks:
      - linktiles
    port:
      - 5001:5001
    environment:
      LT_DB_ENGINE: redis
      LT_DB_PORT: 6378
      LT_DB_HOST: linktiles-redis
  linktiles-redis:
    image: redis:latest
    container_name: linktiles-redis
    networks:
      - linktiles

network:
  linktiles:
```

Run `docker compose up -d` and you should be able to visit the UI at [http://localhost:5001/](http://localhost:5001/).
