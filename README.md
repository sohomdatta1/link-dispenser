# Link-dispenser

Link dispenser is a tool used on English Wikipedia that tests the availability of citations for a specific page. The main version of the tool is hosted on Toolforge by [Sohom Datta](https://github.com/sohomdatta1).

## Deploy on toolforge

### Wikimedia OAuth 2 setup

1. Register a consumer at `https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration/propose`.
2. Choose OAuth 2 and request the minimal grants you need (e.g. "basic" for identity).
3. Set the callback URL to `https://<your-domain>/auth/callback` (must match exactly).
4. Set these environment variables before starting the service:

```
SECRET_KEY=... # random string
WIKIMEDIA_OAUTH_CLIENT_ID=...
WIKIMEDIA_OAUTH_CLIENT_SECRET=...
WIKIMEDIA_OAUTH_REDIRECT_URI=https://<your-domain>/auth/callback
```

Optional overrides if you use a different wiki than meta:

```
WIKIMEDIA_OAUTH_AUTHORIZE_URL=https://<wiki>/w/rest.php/oauth2/authorize
WIKIMEDIA_OAUTH_TOKEN_URL=https://<wiki>/w/rest.php/oauth2/access_token
WIKIMEDIA_OAUTH_PROFILE_URL=https://<wiki>/w/rest.php/oauth2/resource/profile
WIKIMEDIA_OAUTH_SCOPE=basic
```

```sh
toolforge build start https://gitlab.wikimedia.org/toolforge-repos/link-dispenser.git
git clone https://gitlab.wikimedia.org/toolforge-repos/link-dispenser.git
cd link-dispenser
webservice start
toolforge jobs load jobs.yaml
```

## Conrtibutions

Are encouraged.

## Reporting bugs

Please report bugs to [Phabricator](https://phabricator.wikimedia.org/maniphest/task/edit/form/43/?projects=Tool-link-dispenser&subscribers=Soda)