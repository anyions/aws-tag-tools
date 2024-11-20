#  Copyright (c) 2024 AnyIons, All rights reserved.
#  This file is part of aws-tag-tools, released under the MIT license.
#  See the LICENSE file in the project root for full license details.

import logging
from typing import Dict, List, Tuple

from awstt import output
from awstt.config import Config, ConfigError, Resource, Tag, check_config
from awstt.evals import eval_expression
from awstt.worker.thread import Scanner, ScanningThread, Tagger, TaggingThread
from awstt.worker.types import AWSResource, AWSResourceTag, RegionalTaggingTarget, TaggingResponse
from awstt.worker.utils import filter_tags, is_arn, parse_arn


logger = logging.getLogger(__name__)


def _concat_filter(g_filter: str, r_filter: str) -> str:
    return f"{g_filter} && {r_filter}" if all((g_filter, r_filter)) else g_filter or r_filter


def _concat_tags(g_tags: List[Tag], r_tags: List[Tag]) -> List[Tag]:
    if any(isinstance(t, Tag) for t in g_tags + r_tags):
        tags = {t.key: t.value for t in g_tags} | {t.key: t.value for t in r_tags}
        return [Tag(key=k, value=v) for k, v in tags.items()]
    else:
        return g_tags + r_tags


def _run_list_cmd(config: Config, console: output.Console) -> List[Tuple[Resource, List[AWSResource]]]:
    for name in Scanner.list_available():
        scanner = Scanner.by_name(name)(config.partition, config.regions, config.credential)

        if len(config.resources) == 0:
            ScanningThread.add(
                scanner,
                Resource(target=name, filter=config.filter, tags=config.tags, force=config.force),
            )
        else:
            for res in config.resources:
                if isinstance(res, str):
                    target = res
                else:
                    target = res.target

                if (is_arn(target) and scanner.is_supported_arn(target)) or (name.lower() == target.lower()):
                    if not isinstance(res, str):
                        ScanningThread.add(
                            scanner,
                            Resource(
                                target=target,
                                filter=_concat_filter(config.filter, res.filter),
                                tags=_concat_tags(config.tags, res.tags),
                                force=config.force if res.force is None else res.force,
                            ),
                        )
                    else:
                        ScanningThread.add(
                            scanner,
                            Resource(
                                target=target,
                                filter=config.filter,
                                tags=config.tags,
                                force=config.force,
                            ),
                        )

    return ScanningThread.execute(console, config.env)


def _group_tagging_resources(
    env: dict, resources: List[AWSResource], tags: List[Tag], force: bool
) -> List[RegionalTaggingTarget]:
    class TaggingGroup:
        def __init__(self, rs: List[AWSResource], ts: List[Tag]):
            self.resources = rs
            self.tags = ts

    # group resources by region first then by eval tags

    groups: Dict[str, Dict[str, TaggingGroup]] = {}

    for resource in resources:
        region = parse_arn(resource.arn).region
        if region not in groups:
            groups[region] = {}

        region_group = groups[region]

        real_tags = []
        for tag in tags:
            tag_key = eval_expression(tag.key, env, resource.spec)
            tag_val = eval_expression(tag.value, env, resource.spec)
            if force:
                real_tags.append(Tag(key=tag_key, value=tag_val))
            elif not any(t.key == tag_key for t in resource.tags):
                real_tags.append(tag)

        if len(real_tags) == 0:
            continue

        group_key = " | ".join(map(lambda t: "<~~%s=%s~~>" % (t.key, t.value), real_tags))
        if group_key not in region_group:
            region_group[group_key] = TaggingGroup([], real_tags)

        region_group[group_key].resources.append(resource)

    targets = []
    for region, region_group in groups.items():
        for group in region_group.values():
            if len(group.tags) == 0:
                continue

            targets.append(
                RegionalTaggingTarget(
                    region, group.resources, [AWSResourceTag(key=t.key, value=t.value) for t in group.tags]
                )
            )

    return targets


def _run_set_cmd(
    config: Config, inputs: List[Tuple[Resource, List[AWSResource]]], console: output.Console
) -> List[TaggingResponse]:
    tagger = Tagger(config.partition, config.credential)

    for expect, resources in inputs:
        if len(resources) == 0:
            continue

        g_resources = _group_tagging_resources(config.env, resources, expect.tags, expect.force)
        TaggingThread.add(g_resources)

    return TaggingThread.execute(tagger, console)


def _group_untagging_resources(env: dict, resources: List[AWSResource], tags: List[str]) -> List[RegionalTaggingTarget]:
    resources_with_filtered_tags = filter_tags(resources, tags, env)

    regional_resources: Dict[str, Dict] = {}

    for item in resources_with_filtered_tags:
        resource, tags = item[0], item[1]

        region = parse_arn(resource.arn).region
        if region not in regional_resources:
            regional_resources[region] = {}

        tags_key = ",".join(tags)
        if tags_key not in regional_resources[region]:
            regional_resources[region][tags_key] = {"tags": tags, "resources": []}

        regional_resources[region][tags_key]["resources"].append(resource)

    resp = []
    for region, item in regional_resources.items():
        for tags_key, target in item.items():
            resp.append(RegionalTaggingTarget(region, target["resources"], target["tags"]))

    return resp


def _run_unset_cmd(
    config: Config, inputs: List[Tuple[Resource, List[AWSResource]]], console: output.Console
) -> List[TaggingResponse]:
    tagger = Tagger(config.partition, config.credential, action="unset")
    for expect, resources in inputs:
        if len(resources) == 0:
            continue

        g_resources = _group_untagging_resources(config.env, resources, expect.tags)
        TaggingThread.add(g_resources)

    return TaggingThread.execute(tagger, console)


def run(config: Config):
    echo_config = config.dict()
    console = output.console()

    if config.credential and config.credential.access_key is not None:
        echo_config["credential"]["access_key"] = "******"
    if config.credential and config.credential.secret_key is not None:
        echo_config["credential"]["secret_key"] = "******"

    console.print(
        console.new_panel(
            console.new_pretty(echo_config),
            padding=(1, 1),
            title="[b red]Running with config",
            border_style="bright_blue",
        ),
    )

    logger.info(f"Running with config: \n{echo_config}")

    try:
        check_config(config)
    except ConfigError as e:
        logger.fatal(f"Bad config: {e}")

    resources_list_response = _run_list_cmd(config, console)

    if config.action.lower() == "list":
        categories = {}

        logger.info(f"Tags list executed summary:")

        table = console.new_table(title="Tags List Summary")
        table.add_column("ARN")
        table.add_column("Tags", width=40)
        for _, resources in resources_list_response:
            for res in resources:
                if not categories.get(res.category):
                    categories[res.category] = True
                    logger.info(f"=== {res.category} ===")

                    table.add_section()
                    table.add_row(res.category, "", end_section=True)

                tags = "\n".join(["%s = %s" % (t.key, t.value) for t in res.tags]) if len(res.tags) > 0 else "<No Tags>"
                table.add_row(res.arn, tags)
                logger.info("%-80s\n%s" % (res.arn, tags))

        console.print(table)

    if config.action.lower() in ["set", "unset"]:
        categories = {}

        logger.info(f"Tags {config.action.lower()} executed summary:")

        if config.action.lower() == "set":
            summaries = _run_set_cmd(config, resources_list_response, console)
        else:
            summaries = _run_unset_cmd(config, resources_list_response, console)

        table = console.new_table(title="Tags Set Summary")
        table.add_column("ARN", width=80)
        table.add_column("Status", width=10)
        table.add_column("Hint", width=40)

        for summary in summaries:
            if not categories.get(summary.category):
                categories[summary.category] = True
                logger.info(f"=== {summary.category} ===")

                table.add_section()
                table.add_row(summary.category, "", end_section=True)

            table.add_row(summary.arn, summary.status, summary.hint if summary.hint else "")
            logger.info("%-80s  %-10s  %s" % (summary.arn, summary.status, summary.hint if summary.hint else ""))

        console.print(table)
