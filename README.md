# Link-dispenser

Link dispenser is a tool used on English Wikipedia that tests the availability of citations for a specific page. The main version of the tool is hosted on Toolforge by [Sohom Datta](https://github.com/sohomdatta1).

## Deploy on toolforge

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