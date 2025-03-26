linktiles is configured with a collection of environment variables. 

## Authentication

### `LT_SECRET_KEY`

- default: `<hardcoded secret key>`

When using the built-in authentication, this is the secret key used for session management. There is a default key built into the application that will work, but it is recommended that you replace this with your own. You can generate one with openssl:

```sh
openssl rand -hex 32
```

### `LT_ENABLE_AUTH_PROXY`

- options: `True`,`False`, `true`, `false`, `1`, `0`
- default: `false`

If set to `true` (or another truthy value), linktiles will assume it is behind an authorization proxy (like [Authelia](https://www.authelia.com/)) and will authenticate requests based on the `Remote-User` header. This will also disable the built-in authentication flow.

### `LT_AUTH_PROXY_USERNAME_HEADER`

- default: `HTTP_REMOTE_USER`

Which header linktiles should look at for the username when configured to use an auth proxy. Note that all the request headers are converted to uppercase, prefixed with `HTTP_` and replace `-` with `_` before making this comparison. So Authelia's `Remote-User` header, for example, would be registered as `HTTP_REMOTE_USER`.

### `LT_AUTH_PROXY_LOGOUT_URL`

- default: `/login`

Which url to redirect to when logging out while using an auth proxy. You may want to change this to the logout page of your authentication proxy. The default redirect is to the linktiles login page, which would just display an error when configured to use an auth proxy.

## Storage Configuration

### `LT_DB_ENGINE`

- options: `memory`, `redis`
- default: `memory`

Configures which backend to use for storage. `memory` will be discarded when the container restarts.

### `LT_DB_HOST`

- default: `localhost`

The host to use for the database connection, if applicable.

### `LT_DB_USER`

- default: `linktiles`

The user to use for the database connection, if applicable.

### `LT_DB_PASSWORD`

- default: `None`

The password to use for the database connection, if applicable.

### `LT_DB_PORT`

- default (when db engine is `redis`): `6379`

The port to use for the database connection, if applicable.

## Server behavior

### `LT_ENVIRONMENT`

- options: `prod`, `production`, `dev`, `development`
- default: `prod`

If set to `dev` or `development`, it will run the Flask server in [debug mode](https://flask.palletsprojects.com/en/stable/quickstart/#debug-mode).

### `LT_CONTEXT_PATH`

- default: `None`

If set, linktiles will use this path as a prefix for all its routes. Useful if you need to serve linktiles under a subpath.

### `LT_SERVER_PORT`

- default: `5001`

Which port linktiles should serve itself on.

### `GUNICORN_WORKERS`

- default: `2`

When running linktiles via the docker image, this value can be used to configure how many worker processes Gunicorn should use.
