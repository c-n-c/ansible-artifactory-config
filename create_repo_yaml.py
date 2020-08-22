import re
import sys
import xml.etree.ElementTree as ET

test_filename_input = sys.argv[1] + '/capture_config/files/config.xml'
test_filename_output_base = sys.argv[1] + '/deploy_config/files/'

ALL_TAGS = [('proxies', 'proxy'),
            ('propertySets', 'propertySet'),
            ('localRepositories', 'localRepository'),
            ('remoteRepositories', 'remoteRepository'),
            ('virtualRepositories', 'virtualRepository')]

cleanup_template = re.compile("{.*}")

remove_yaml_node = ["localRepoChecksumPolicyType",
                    "repoLayoutRef",
                    "value",
                    "externalDependencies"
                    ]

make_child_to_array = ['repositoryRef', 'propertySetRef']

replace_with_tags = {"proxyRef": "proxy", "defaultProxy": "platformDefault"}

replace_with_child_text = {"predefinedValue": "value"}


def fetch_child_text(node, child):
    children = list(node)
    for each in children:
        if re.sub(cleanup_template, "", each.tag) == child:
            return each.text.strip()


def xml2yml(node, output_fp, parse_tags, yml_tree_depth=0, xml_tree_depth=0):
    cleaned_tag = re.sub(cleanup_template, "", node.tag)
    children = list(node)

    if cleaned_tag != parse_tags[0] and yml_tree_depth is 0 and xml_tree_depth < 2:
        xml_tree_depth += 1
        if xml_tree_depth > 1:
            return
        else:
            for child in children:
                xml2yml(child, output_fp, parse_tags, yml_tree_depth, xml_tree_depth)

    elif cleaned_tag in remove_yaml_node:
        return

    else:
        if cleaned_tag == parse_tags[1]:
            file_name_text = ""
            list_item = ["%s-%s" % (x.text, cleaned_tag.lower()) for x in children if re.match("^.*key$", x.tag)] or \
                        ["%s-propertyset" % x.text for x in children if re.match("^.*name$", x.tag)]
            if list_item:
                file_name_text = list_item[0]
            if not file_name_text:
                return
            entity_tag = file_name_text.replace("-propertyset", "").replace("-%s" % cleaned_tag.lower(), "", 1)
            output_fp = open("%s%s.yml" % (test_filename_output_base, file_name_text), "w")
            output_fp.write('{tag}:\n'.format(tag=parse_tags[0]))
            output_fp.write('  {tag}:\n'.format(tag=entity_tag))
        node_attrs = node.attrib
        content = node.text.strip() if node.text else ''

        if content and cleaned_tag not in ["key", "name"]:
            if not (node_attrs or children):
                if cleaned_tag in ["includesPattern"]:
                    output_fp.write(
                        '{indent}{tag}: "{text}"\n'.format(
                            indent=yml_tree_depth * '  ', tag=cleaned_tag, text=content or ''))
                elif cleaned_tag in make_child_to_array:
                    output_fp.write(
                        '{indent}- {text}\n'.format(
                            indent=yml_tree_depth * '  ', text=content or ''))
                elif cleaned_tag in replace_with_tags.keys():
                    output_fp.write(
                        '{indent}{tag}: {text}\n'.format(
                            indent=yml_tree_depth * '  ', tag=replace_with_tags[cleaned_tag], text=content or ''))
                else:
                    output_fp.write(
                        '{indent}{tag}: {text}\n'.format(
                            indent=yml_tree_depth * '  ', tag=cleaned_tag, text=content or ''))
                return

        if yml_tree_depth > 0 and cleaned_tag not in [parse_tags[1], "key", "name", "predefinedValue"]:
            output_fp.write('{indent}{tag}:\n'.format(
                indent=yml_tree_depth * '  ', tag=cleaned_tag))

        if cleaned_tag in replace_with_child_text.keys():
            output_fp.write(
                '{indent}{tag}: {text}\n'.format(
                    indent=yml_tree_depth * '  ', tag=fetch_child_text(
                        node, replace_with_child_text[cleaned_tag]),
                    text=content or ''))

        yml_tree_depth += 1
        xml_tree_depth += 1
        for child in children:
            xml2yml(child, output_fp, parse_tags, yml_tree_depth, xml_tree_depth)


with open(test_filename_input) as input_fp:
    tree = ET.parse(input_fp)
    for tags in ALL_TAGS:
        xml2yml(tree.getroot(), None, tags)
