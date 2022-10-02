# IT Cap Script

How to install dependencies?

```shell
> poetry install
```

Set environment variables

```shell
export JIRA_TOKEN=MYTOKEN
export JIRA_EMAIL=myemail@hellofresh.com
```

How to run script?

```shell
# poetry run it-cap --project {PROJECT KEY} --period {month}/{year} --output {screen|csv}
# example
> poetry run it-cap --project MCPRO --period 09/2022 --output screen

# Story Points?
> poetry run it-cap --project GAI --period 09/2022 --story-points
```
