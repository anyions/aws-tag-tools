import json
import logging
from typing import Optional

import rich_click as click

from awstt import executor
from awstt.config import init_config
from awstt.output import init_logger

logger = logging.getLogger()

click.rich_click.USE_RICH_MARKUP = False

click.rich_click.COMMAND_GROUPS = {
    "awstt": [{"name": "Commands", "commands": ["set", "unset", "list", "exec", "info"]}]
}

_common_option_groups = [
    {
        "name": "Credential Options",
        "options": ["--access_key", "--secret_key", "--profile"],
    },
    {
        "name": "Log Options",
        "options": ["--save-log", "--log-level"],
    },
    {
        "name": "Help",
        "options": ["--help"],
    },
]

click.rich_click.OPTION_GROUPS = {
    "awstt": [
        {
            "name": "Help",
            "options": ["--help"],
        },
    ],
    "awstt info": [
        {
            "name": "Help",
            "options": ["--help"],
        },
    ],
    "awstt set": [
        {
            "name": "Tagging Options",
            "options": ["--tag", "--resource", "--region", "--partition", "--force", "--filter"],
        },
    ],
    "awstt unset": [
        {
            "name": "UnTagging Options",
            "options": ["--tag", "--resource", "--region", "--partition", "--filter"],
        },
    ],
    "awstt list": [
        {
            "name": "List Options",
            "options": ["--resource", "--region", "--partition", "--force", "--filter"],
        },
    ],
    "awstt exec": [
        {
            "name": "Execute Options",
            "options": ["--config", "--filter"],
        },
    ],
}
click.rich_click.OPTION_GROUPS["awstt list"] += _common_option_groups
click.rich_click.OPTION_GROUPS["awstt set"] += _common_option_groups
click.rich_click.OPTION_GROUPS["awstt unset"] += _common_option_groups
click.rich_click.OPTION_GROUPS["awstt exec"] += _common_option_groups


@click.group()
def info():
    """Show helpful information about AWS-Tag-Tools"""
    pass


@info.command("resources", short_help="List all supported resources", add_help_option=False)
def info_resources():
    from awstt.output import console
    from awstt.worker.scanner import Scanner

    console = console()
    table = console.new_table(title="", show_header=False, show_edge=False)
    table.add_column("")
    for resource in Scanner.list_available():
        table.add_row(resource)

    console.print(
        console.new_panel(
            table,
            padding=(1, 1),
            title="[b red]Supported resources",
            border_style="bright_blue",
        ),
    )


_cli_option_partition_choices = click.Choice(["aws", "aws-cn", "aws-us-gov"])

_cli_common_options = [
    click.option("--access_key", help="Access key of AWS AK/SK"),
    click.option("--secret_key", help="Secret key of AWS AK/SK"),
    click.option("--profile", help="Profile name of AWS CLI Credential"),
    click.option("--save-log", "save_log", is_flag=True, default=False, help="Save log to file"),
    click.option(
        "--log-level",
        "log_level",
        help="Set log level",
        type=click.Choice(["debug", "info", "warning", "error", "critical"], case_sensitive=False),
        default="error",
        show_default=True,
    ),
]


def cmd_common_options(func):
    for option in reversed(_cli_common_options):
        func = option(func)
    return func


@click.group()
def cmd():
    """AWS-Tag-Tools: The missing tag manager for AWS resources"""
    pass


@cmd.command("set", help="Set tag(s) to resources")
@cmd_common_options
@click.option("--tag", required=True, help="Tag to set", metavar="KEY=VALUE[,KEY=VALUE,...]")
@click.option("--region", help="Region of AWS", metavar="REGION1[,REGION2,...]")
@click.option("--partition", help="Partition of AWS", type=_cli_option_partition_choices, default="aws")
@click.option("--resource", help="Resource type or ARN pattern", metavar="RESOURCE1[,RESOURCE2,...]")
@click.option("--filter", "filters", help="JMESPath expression to filter resources")
@click.option("--force", is_flag=True, default=False, help="Force overwrite if tag exists")
def cmd_set(
        tag: str,
        resource: Optional[str],
        region: Optional[str],
        partition: Optional[str],
        filters: Optional[str],
        force: Optional[bool],
        access_key: Optional[str],
        secret_key: Optional[str],
        profile: Optional[str],
        save_log: Optional[bool],
        log_level: Optional[str],
):
    if len(tag) < 1:
        click.echo("Error: must set at least one tag, see the usage of SET command.")
        click.echo(click.get_current_context().get_help())
        return

    init_logger(log_level, save_log)

    opt_tags = tag.split(",")
    tags = []
    for t in opt_tags:
        if "=" in t:
            kv = t.split("=", 1)
            tags.append({"key": kv[0], "value": kv[1]})
        else:
            click.echo(f"Error: invalid tag option")
            return

    inputs = {
        "action": "set",
        "partition": partition,
        "regions": region.split(",") if region else [],
        "filter": filters,
        "tags": tags,
        "resources": resource.split(",") if resource else [],
        "force": force,
        "credential": {
            "access_key": access_key,
            "secret_key": secret_key,
            "profile": profile,
        },
    }

    config = init_config(inputs)
    executor.run(config)


@cmd.command("unset", help="Unset tag(s) from resources")
@cmd_common_options
@click.option("--tag", required=True, help="tag to unset", metavar="KEY1[,KEY2,...]")
@click.option("--region", help="Region of AWS", metavar="REGION1[,REGION2,...]")
@click.option("--partition", help="Partition of AWS", type=_cli_option_partition_choices, default="aws")
@click.option("--resource", help="Resource type or ARN pattern", metavar="RESOURCE1[,RESOURCE2,...]")
@click.option("--filter", "filters", help="JMESPath expression to filter resources")
def cmd_unset(
        tag: str,
        resource: Optional[str],
        region: Optional[str],
        partition: Optional[str],
        filters: Optional[str],
        access_key: Optional[str],
        secret_key: Optional[str],
        profile: Optional[str],
        save_log: Optional[bool],
        log_level: Optional[str],
):
    if len(tag) < 1:
        click.echo("Error: must set at least one tag, see the usage of UNSET command.")
        click.echo(click.get_current_context().get_help())
        return

    init_logger(log_level, save_log)

    inputs = {
        "action": "unset",
        "partition": partition,
        "regions": region.split(",") if region else [],
        "filter": filters,
        "tags": tag.split(","),
        "resources": resource.split(",") if resource else [],
        "credential": {
            "access_key": access_key,
            "secret_key": secret_key,
            "profile": profile,
        },
    }

    config = init_config(inputs)
    executor.run(config)


@cmd.command("list", help="List resources by tag(s) or spec condition(s)")
@cmd_common_options
@click.option("--region", help="Region of AWS", metavar="REGION1[,REGION2,...]")
@click.option("--partition", help="Partition of AWS", type=_cli_option_partition_choices, default="aws")
@click.option("--resource", help="Resource type or ARN pattern", metavar="RESOURCE1[,RESOURCE2,...]")
@click.option("--filter", "filters", help="JMESPath expression to filter resources")
def cmd_list(
        resource: Optional[str],
        region: Optional[str],
        partition: Optional[str],
        filters: Optional[str],
        access_key: Optional[str],
        secret_key: Optional[str],
        profile: Optional[str],
        save_log: Optional[bool],
        log_level: Optional[str],
):
    init_logger(log_level, save_log)

    inputs = {
        "action": "list",
        "partition": partition,
        "regions": region.split(",") if region else [],
        "filter": filters,
        "tags": [],
        "resources": resource.split(",") if resource else [],
        "force": False,
        "credential": {
            "access_key": access_key,
            "secret_key": secret_key,
            "profile": profile,
        },
    }

    config = init_config(inputs)
    executor.run(config)


@cmd.command("exec", help="Execute action with config file")
@cmd_common_options
@click.option("--config", "cfg", help="Config file", type=click.Path(exists=True))
def cmd_exec(
        cfg: str,
        access_key: Optional[str],
        secret_key: Optional[str],
        profile: Optional[str],
        save_log: Optional[bool],
        log_level: Optional[str],
):
    init_logger(log_level, save_log)

    with open(cfg, "r") as f:
        inputs = json.loads(f.read())

        if not inputs.get("credential"):
            inputs["credential"] = {}

        if access_key:
            inputs["credential"]["access_key"] = access_key
        if secret_key:
            inputs["credential"]["secret_key"] = secret_key
        if profile:
            inputs["credential"]["profile"] = profile

        config = init_config(inputs)
        executor.run(config)


def run():
    cmd.add_command(info)
    cmd(prog_name="awstt", auto_envvar_prefix="AWSTT")
