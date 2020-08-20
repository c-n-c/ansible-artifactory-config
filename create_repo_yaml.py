import re
import sys
import xml.etree.ElementTree as ET

test_filename_input = sys.argv[1] + '/capture_config/files/config.xml'
test_filename_output_base = sys.argv[1] + '/deploy_config/files/'

ALL_TAGS = [('localRepositories', 'localRepository'),
            ('remoteRepositories', 'remoteRepository'),
            ('virtualRepositories', 'virtualRepository')]

cleanup_template = re.compile("{.*}")

cleanup_yaml_node = ["localRepoChecksumPolicyType", "repoLayoutRef"]

make_child_to_array = ['repositoryRef']


def xml2yml(node, output_fp, parse_tags, yml_tree_depth=0):
    cleaned_tag = re.sub(cleanup_template, "", node.tag)
    children = list(node)

    if cleaned_tag != parse_tags[0] and yml_tree_depth is 0:
        for child in children:
            xml2yml(child, output_fp, parse_tags, yml_tree_depth)

    elif cleaned_tag in cleanup_yaml_node:
        return

    else:
        if cleaned_tag == parse_tags[1]:
            file_name_text = [x.text for x in children if re.sub(cleanup_template, "", x.tag) == "key"][0]
            if not file_name_text:
                return

            output_fp = open("%s%s.yml" % (test_filename_output_base, file_name_text), "w")
            output_fp.write('{tag}:\n'.format(tag=parse_tags[0]))
            output_fp.write('  {tag}:\n'.format(tag=file_name_text))

        nodeattrs = node.attrib
        content = node.text.strip() if node.text else ''

        if content and cleaned_tag != "key":
            if not (nodeattrs or children):
                if cleaned_tag == "includesPattern":
                    output_fp.write(
                        '{indent}{tag}: "{text}"\n'.format(
                            indent=yml_tree_depth * '  ', tag=cleaned_tag, text=content or ''))
                elif cleaned_tag in make_child_to_array:
                    output_fp.write(
                        '{indent}- {text}\n'.format(
                            indent=yml_tree_depth * '  ', text=content or ''))
                else:
                    output_fp.write(
                        '{indent}{tag}: {text}\n'.format(
                            indent=yml_tree_depth * '  ', tag=cleaned_tag, text=content or ''))
                return

        if yml_tree_depth > 0 and cleaned_tag not in [parse_tags[1], "key"]:
            output_fp.write('{indent}{tag}:\n'.format(
                indent=yml_tree_depth * '  ', tag=cleaned_tag))

        yml_tree_depth += 1
        for child in children:
            xml2yml(child, output_fp, parse_tags, yml_tree_depth)


with open(test_filename_input) as input_fp:
    tree = ET.parse(input_fp)
    for tags in ALL_TAGS:
        xml2yml(tree.getroot(), None, tags)
