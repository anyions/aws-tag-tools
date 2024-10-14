import logging
from typing import Dict, List, Tuple

from awstt import output
from awstt.config import Config, ConfigError, Tag, check_config
from awstt.worker.thread import Scanner, ScanningThread, Tagger, TaggingThread
from awstt.worker.types import AWSResource, AWSResourceTag, RegionalTaggingTarget, ResourceFilter, TaggingResponse
from awstt.worker.utils import filter_tags, is_arn, is_arn_wild_match, parse_arn


logger = logging.getLogger(__name__)


def _run_list_cmd(config: Config, console: output.Console) -> List[AWSResource]:
    for name in Scanner.list_available():
        scanner = Scanner.by_name(name)(config.partition, config.regions, config.credential)

        if len(config.resources) == 0:
            ScanningThread.add(
                scanner,
                ([ResourceFilter(pattern=scanner.arn_pattern, conditions=[config.filter])] if config.filter else []),
            )
        else:
            filters = []
            need_to_scan = False

            for res in config.resources:
                if isinstance(res, str):
                    target = res
                else:
                    target = res.target

                if (is_arn(target) and scanner.is_supported_arn(target)) or (name.lower() == target.lower()):
                    need_to_scan = True

                    if not isinstance(res, str):
                        conditions = [s for s in [config.filter, res.filter] if s is not None]

                        filters.append(
                            ResourceFilter(
                                pattern=target if is_arn(target) else scanner.arn_pattern,
                                conditions=conditions,
                            )
                        )
                    else:
                        filters.append(
                            ResourceFilter(
                                pattern=target,
                                conditions=[config.filter] if config.filter else [],
                            )
                        )

            if need_to_scan:
                ScanningThread.add(scanner, filters)

    return ScanningThread.execute(console)


def _group_tag_resources(resources: List[AWSResource], tags: List[Tag], force: bool) -> List[RegionalTaggingTarget]:
    class TaggingGroup:
        # noinspection SpellCheckingInspection
        def __init__(self, rs: List[AWSResource], ts: List[Tag]):
            self.resources = rs
            self.tags = ts

    # group resources by region

    regional_resources: Dict[str, List[AWSResource]] = {}
    for resource in resources:
        region = parse_arn(resource.arn).region
        if region not in regional_resources:
            regional_resources[region] = []

        regional_resources[region].append(resource)

    if force:
        return [
            RegionalTaggingTarget(region, resources, [AWSResourceTag(key=t.key, value=t.value) for t in tags])
            for region, resources in regional_resources.items()
        ]

    # group resources by tags

    resp = []
    for region, resources in regional_resources.items():
        resources_with_tags: Dict[str, TaggingGroup] = {}

        for resource in resources:
            filtered_tags: List[Tag] = []
            for tag in tags:
                if not any(t.key == tag.key for t in resource.tags):
                    filtered_tags.append(tag)

            if len(filtered_tags) == 0:
                continue

            key = " | ".join(map(lambda t: "%s=%s" % (t.key, t.value), filtered_tags))
            if key not in resources_with_tags:
                resources_with_tags[key] = TaggingGroup([], filtered_tags)
            resources_with_tags[key].resources.append(resource)

        resp.extend(
            [
                RegionalTaggingTarget(
                    region, group.resources, [AWSResourceTag(key=t.key, value=t.value) for t in group.tags]
                )
                for _, group in resources_with_tags.items()
            ]
        )

    return resp


def _run_set_cmd(config: Config, resources: List[AWSResource], console: output.Console) -> List[TaggingResponse]:
    tagger = Tagger(config.partition, config.credential)

    if len(config.resources) == 0:
        g_resources = _group_tag_resources(resources, config.tags, config.force)

        TaggingThread.add(g_resources)
    else:
        g_tags = config.tags
        for c_resource in config.resources:
            if isinstance(c_resource, str):
                targets: List[AWSResource] = []

                for resource in resources:
                    if resource.category.lower() == c_resource.lower() and not is_arn(c_resource):
                        targets.append(resource)
                    elif is_arn(c_resource) and is_arn_wild_match(resource.arn, c_resource):
                        targets.append(resource)

                if len(targets) > 0:
                    g_resources = _group_tag_resources(targets, g_tags, config.force)
                    if len(g_resources) > 0:
                        TaggingThread.add(g_resources)
            else:
                force = c_resource.force or config.force
                tags: List[Tag] = []

                for tag in g_tags:
                    c_tag = next(filter(lambda x: x.key == tag.key, c_resource.tags), None)
                    if c_tag:
                        tags.append(Tag(key=c_tag.key, value=c_tag.value))
                    else:
                        tags.append(Tag(key=tag.key, value=tag.value))

                targets: List[AWSResource] = []

                for resource in resources:
                    if is_arn(c_resource.target) and is_arn_wild_match(resource.arn, c_resource.target):
                        targets.append(resource)
                    elif resource.category.lower() == c_resource.target.lower() and not is_arn(c_resource.target):
                        targets.append(resource)

                if len(targets) > 0:
                    g_resources = _group_tag_resources(targets, tags, force)
                    if len(g_resources) > 0:
                        TaggingThread.add(g_resources)

    return TaggingThread.execute(tagger, console)


def _group_untag_resources(
    resources_with_filtered_tags: List[Tuple[AWSResource, List[str]]]
) -> List[RegionalTaggingTarget]:
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


def _run_unset_cmd(config: Config, resources: List[AWSResource], console: output.Console) -> List[TaggingResponse]:
    tagger = Tagger(config.partition, config.credential, action="unset")

    if len(config.resources) == 0:
        resources_with_filtered_tags = filter_tags(resources, config.tags)
        if len(resources_with_filtered_tags) == 0:
            return []

        g_resources = _group_untag_resources(resources_with_filtered_tags)

        TaggingThread.add(g_resources)
    else:
        g_tags = config.tags

        for c_resource in config.resources:
            if isinstance(c_resource, str):
                targets = []

                for resource in resources:
                    if resource.category == c_resource and not is_arn(c_resource):
                        targets.append(resource)
                    elif is_arn(c_resource) and is_arn_wild_match(resource.arn, c_resource):
                        targets.append(resource)

                if len(targets) > 0:
                    resources_with_filtered_tags = filter_tags(resources, g_tags)

                    if len(resources_with_filtered_tags) > 0:
                        g_resources = _group_untag_resources(resources_with_filtered_tags)
                        TaggingThread.add(g_resources)
            else:
                targets = []

                for resource in resources:
                    if is_arn(c_resource.target) and is_arn_wild_match(resource.arn, c_resource.target):
                        targets.append(resource)
                    elif resource.category == c_resource.target and not is_arn(c_resource.target):
                        targets.append(resource)

                if len(targets) > 0:
                    tags = g_tags + c_resource.tags

                    resources_with_filtered_tags = filter_tags(resources, tags)

                    if len(resources_with_filtered_tags) > 0:
                        g_resources = _group_untag_resources(resources_with_filtered_tags)
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

    resource = _run_list_cmd(config, console)

    if config.action.lower() == "list":
        categories = {}

        logger.info(f"Tags list executed summary:")

        table = console.new_table(title="Tags List Summary")
        table.add_column("ARN", width=80)
        table.add_column("Tags")
        for res in resource:
            if not categories.get(res.category):
                categories[res.category] = True
                logger.info(f"=== {res.category} ===")

                table.add_section()
                table.add_row(res.category, "", end_section=True)

            tags = " | ".join(["%s=%s" % (t.key, t.value) for t in res.tags]) if len(res.tags) > 0 else "<No Tags>"
            table.add_row(res.arn, tags)
            logger.info("%-80s\n%s" % (res.arn, tags))

        console.print(table)

    if config.action.lower() in ["set", "unset"]:
        categories = {}

        logger.info(f"Tags {config.action.lower()} executed summary:")

        if config.action.lower() == "set":
            summaries = _run_set_cmd(config, resource, console)
        else:
            summaries = _run_unset_cmd(config, resource, console)

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
