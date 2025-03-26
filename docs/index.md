# Pyreminder
[![Docker Pulls](https://img.shields.io/docker/pulls/haumea/pyreminder)](https://hub.docker.com/r/haumea/pyreminder/)
[![GitLab release (latest by date)](https://img.shields.io/gitlab/v/release/haondt/pyreminder)](https://gitlab.com/haondt/pyreminder/-/releases/permalink/latest)


Pyreminder is a minimal tool for checking statuses and sending notifications. Inspired by [Kibitzr](https://kibitzr.github.io/) but meant to be simpler. Pyreminder is configured with a single yaml file:

/// tab | pyreminder.yml
```yaml
checks:
  - pyreminder:
      source:
        type: docker-hub
        namespace: haumea
        repository: pyreminder
        tag: latest
      destinations:
        - type: discord
          webhookURL: ${PYREMINDER_DISCORD_WEBHOOK_URL}
          color: 1ABC9C
          template: "Hooray! A new version of `${docker_hub__image}` was just released!"
      period: 1d
```
///

# linktiles

linktiles is a tile-based read-only frontend for linkding, a minimal bookmark manager. linktiles uses an api key to fetch links from your linkding instance, and displays them in a configurable mosaic.

Feature Overview:

- Clean UI matching the style of linkding
- Display tagged bookmarks as tiles
- Create groups of bookmarks within a tile
- Various configuration options to change the look of the tiles
- SSO support via authentication proxies

Check the [installation](./installation.md) guide to get started.
