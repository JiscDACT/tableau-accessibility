from lxml.etree import XMLParser, parse
import argparse
import os
import csv
from yaml import load, loader

# We need to use the 'huge' parser as these docs are really big
p = XMLParser(huge_tree=True)


def get_item(tree, dashboard_name, item):
    zone = get_view(tree, dashboard_name, item)
    if zone is None:
        zone = get_button(tree, dashboard_name, item)
    if zone is None:
        zone = get_parameter(tree, dashboard_name, item)
    if zone is None:
        zone = get_filter(tree, dashboard_name, item)
    if zone is None:
        zone = get_text(tree, dashboard_name, item)
    if zone is None:
        zone = get_image(tree, dashboard_name, item)
    if zone is None:
        zone = get_highlighter_by_filter(tree, dashboard_name, item)
    return zone


def get_parent_tag(item, tag):
    while item is not None:
        if item.tag == tag:
            return item
        item = item.getparent()


def get_parent_worksheet(item):
    return get_parent_tag(item, 'worksheet')


def get_parent_dashboard(item):
    return get_parent_tag(item, 'dashboard')


def get_parent_dashboard_name(item):
    return get_parent_dashboard(item).get("name")


def get_parent_zone(item):
    return get_parent_tag(item, 'zone')


def get_image(tree, dashboard_name, path):
    match = "substring(@param, string-length(@param) - string-length('"+path+"') + 1) = '"+path+"'"
    query = ".//dashboard[@name='" + dashboard_name + "']//zone[(@_.fcp.SetMembershipControl.false...type='bitmap' or @type='bitmap') and "+match+"]"
    image = tree.xpath(query)
    if image is not None and image.__len__() > 0:
        zone = image[0]
        return zone
    return None


def get_text(tree, dashboard_name, text):
    view = tree.xpath("//dashboard[@name='" + dashboard_name + "']//run[text()='" + text + "']")
    if view is not None and view.__len__() > 0:
        zone = get_parent_zone(view[0])
        return zone
    return None


def get_view(tree, dashboard_name, viewname):
    view = tree.xpath("//dashboard[@name='" + dashboard_name + "']//zone[@name='" + viewname + "' and not(@param)]")
    if view is not None and view.__len__() > 0:
        zone = view[0]
        return zone
    return None


def get_button(tree, dashboard_name, caption):
    button = tree.xpath("//dashboard[@name='" + dashboard_name + "']//zone//button//caption[text()='" + caption + "']")
    if button is not None and button.__len__() > 0:
        zone = get_parent_zone(button[0])
        return zone
    return None


def get_highlighter_by_filter(tree, dashboard_name, filter):
    if filter.startswith("Highlight "):
        filter = filter.split("Highlight ")[1]
        highlighters = tree.xpath(".//dashboard[@name='"+dashboard_name+"']//zone[@type='highlighter' and contains(@param, ':" + filter + ":')]")
        if highlighters is not None and highlighters.__len__() > 0:
            return highlighters[0]
        highlighters = tree.xpath(".//dashboard[@name='"+dashboard_name+"']//zone[@_.fcp.SetMembershipControl.true...type-v2='highlighter' and contains(@param, ':" + filter + ":')]")
        if highlighters is not None and highlighters.__len__() > 0:
            return highlighters[0]
    return None


def get_parameter_by_alias(tree, alias):
    # column caption='The First Parameter' datatype='string' name='[Parameter 1]'
    reference = tree.xpath("//column[@caption='" + alias + "' and starts-with(@name, '[Parameter ')]")
    if reference is not None and reference.__len__() > 0:
        return reference[0].get("name")
    return None


# TODO ensure this works with 2019.4
def get_parameter(tree, dashboard_name, parameter):
    param = '[Parameters].['+parameter+']'
    parameters = tree.xpath(".//dashboard[@name='"+dashboard_name+"']//zone[@param='" + param + "']")
    if parameters is not None and parameters.__len__() > 0:
        zone = parameters[0]
        return zone

    # Parameter with a custom title
    parameters = tree.xpath(".//dashboard[@name='"+dashboard_name+"']//zone[@type='paramctrl']/formatted-text/run[text()='"+parameter+"']")
    if parameters is not None and parameters.__len__() > 0:
        zone = get_parent_zone(parameters[0])
        return zone

    # Parameter with a custom title for later versions
    parameters = tree.xpath(".//dashboard[@name='"+dashboard_name+"']//zone[@_.fcp.SetMembershipControl.true...type-v2='paramctrl'='paramctrl']/formatted-text/run[text()='"+parameter+"']")
    if parameters is not None and parameters.__len__() > 0:
        zone = get_parent_zone(parameters[0])
        return zone

    # Parameters with aliases
    reference = get_parameter_by_alias(tree, parameter)
    if reference is not None:
        param = '[Parameters].' + reference
        parameters = tree.xpath(".//dashboard[@name='" + dashboard_name + "']//zone[@param='" + param + "']")
        if parameters is not None and parameters.__len__() > 0:
            zone = parameters[0]
            return zone

    return None


def get_filter_by_alias(tree, alias):
    reference = tree.xpath("//column[@caption='" + alias + "']")
    if reference is not None and reference.__len__() > 0:
        name = reference[0].get("name")
        if name.startswith('[') and name.endswith(']'):
            name = name[1:-1]
        return name
    return None


def get_filter(tree, dashboard_name, filter):
    filter_search = ':'+filter+':'
    parameter = tree.xpath(".//dashboard[@name='"+dashboard_name+"']//zone[contains(@param, '" + filter_search + "')]")
    if parameter is not None and parameter.__len__() > 0:
        zone = parameter[0]
        return zone

    reference = get_filter_by_alias(tree, filter)
    if reference is not None:
        filter_search = ':'+reference+':'
        filters = tree.xpath(".//dashboard[@name='"+dashboard_name+"']//zone[contains(@param, '" + filter_search + "')]")
        if filters is not None and filters.__len__() > 0:
            zone = filters[0]
            return zone

    return None


def check_accessibility(input_filename):
    with open(input_filename, 'r', encoding='utf-8') as f:  # open in readonly mode
        tree = parse(f, parser=p)
        warnings = []
        warnings = warnings + check_alt_text(tree)
        warnings = warnings + check_titles_and_captions(tree)
        warnings = warnings + check_vertical_text(tree)
        warnings = warnings + check_mark_labels(tree)
        return warnings


def check_mark_labels(tree):
    formats = tree.xpath("//worksheet[not(.//format[@attr='mark-labels-show'])]")
    warnings = []
    for format in formats:
        sheet = get_parent_tag(format, 'worksheet').get("name")
        zones = tree.xpath("//zone[@name='"+sheet+"']")
        for zone in zones:
            if zone.get('_.fcp.SetMembershipControl.false...type') is None and zone.get("type") is None:
                dashboard_name = get_parent_dashboard_name(zone)
                warnings.append(
                    {
                        "code": "B3",
                        "dashboard": dashboard_name,
                        "item": sheet,
                        "message": "B3 no mark labels for view '"+sheet+"' in dashboard '"+dashboard_name+"'"
                    })
    return warnings


def check_vertical_text(tree):
    formats = tree.xpath("//format[@attr='text-orientation' and (@value='-90' or @value='90')]")
    warnings = []
    for format in formats:
        sheet = get_parent_tag(format, 'worksheet').get("name")
        zones = tree.xpath("//zone[@name='"+sheet+"']")
        for zone in zones:
            if zone.get('_.fcp.SetMembershipControl.false...type') is None and zone.get("type") is None:
                dashboard_name = get_parent_dashboard_name(zone)
                warnings.append(
                    {
                        "code": "B1",
                        "dashboard": dashboard_name,
                        "item": sheet,
                        "message": "B3 text is rotated for view '"+sheet+"' in dashboard '"+dashboard_name+"'"
                    })
    return warnings


# TODO ensure this works with 2019.4
def check_alt_text(tree):
    warnings = []
    images = tree.xpath("//zone[@_.fcp.SetMembershipControl.false...type='bitmap' or @type='bitmap']")
    for image in images:
        if not image.get("alt-text") or image.get("alt-text") == '':
            dashboard_name = get_parent_dashboard_name(image)
            short_name = image.get("param").split("/")[-1]
            warnings.append(
                {
                    "code": "A4",
                    "dashboard": dashboard_name,
                    "item": image.get("param"),
                    "message": "A4 image '"+short_name+"' with missing alternative text in dashboard '" + dashboard_name + "'"
                })
    return warnings


def check_titles_and_captions(tree):
    warnings = []
    zones = tree.xpath("//zone[@name]")
    for zone in zones:
        if zone.get('_.fcp.SetMembershipControl.false...type') is None and zone.get("type") is None:
            dashboard_name = get_parent_dashboard_name(zone)
            item = zone.get('name')
            if zone.get('show-title') and zone.get('show-title') == 'false':
                warnings.append(
                    {
                        "code": "A5",
                        "dashboard": dashboard_name,
                        "item": item,
                        "message": "A5 Object '" + item + "' in dashboard '" + dashboard_name + "' has no title"
                    })
            if not zone.get('show-caption') or zone.get('show-caption') == 'false':
                warnings.append(
                    {
                        "code": "A6",
                        "dashboard": dashboard_name,
                        "item": item,
                        "message": "A6 Object '" + item + "' in dashboard '" + dashboard_name + "' has no caption"
                    })
    return warnings


def load_manifest(manifest_path):
    with open(manifest_path, 'r') as file:
        configuration = load(file, Loader=loader.SafeLoader)
    return configuration


def fix_tabs(input_filename, output_filename, configuration):
    with open(input_filename, 'r', encoding='utf-8') as f:  # open in readonly mode
        tree = parse(f, parser=p)
        tree = fix_tabs_in_tree(tree, configuration)
        tree.write(output_filename, encoding='utf-8')


def fix_tabs_in_tree(tree, configuration):
    zone_id = 0
    for dashboard_name in configuration:
        tab_order = configuration[dashboard_name]
        zone_id += 100

        # Start providing IDs for the named items
        for item in tab_order:
            zone = get_item(tree, dashboard_name, item)
            if zone is not None:
                zone.set("id", zone_id.__str__())
                zone.set("is-modified", '1')
                zone_id += 1
            else:
                print("ERROR in manifest: object '"+item+"' does not exist in dashboard '"+dashboard_name+"'")

        # Add IDs to everything else in document order
        zones = tree.xpath('//dashboard[@name="' + dashboard_name + '"]//zone')
        for zone in zones:
            if not zone.get("is-modified"):
                zone.set("id", zone_id.__str__())
                zone_id += 1

        dashboard = tree.find("//dashboard[@name='"+dashboard_name+"']")

        # TODO handle device layouts properly
        # Duplicate IDs in device layouts cause problems so get rid of them...
        layouts = dashboard.find("devicelayouts")
        if layouts is not None:
            dashboard.remove(layouts)
    return tree


if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description='Accessibility testing and tab focus order fixer for Tableau.')
    argparser.add_argument('input_path', metavar='<input>', type=str, nargs=1, default='testing.twb',
                        help='The name of the Tableau file to process')
    argparser.add_argument('output_path', metavar='<output>', type=str, nargs='?', default='output.twb',
                        help='The output file name')
    argparser.add_argument('manifest_path', metavar='<manifest>', type=str, nargs='?', default='manifest.txt',
                        help='The manifest file')
    argparser.add_argument('-t', action='store_true',
                        help='Just check for issues without modifying focus order')
    argparser.add_argument('-c', action='store_true',
                        help='Output results in CSV format')

    args = argparser.parse_args()

    # Defaults
    input_path = vars(args)['input_path'][0]
    output_path = vars(args)['output_path']
    manifest_path = vars(args)['manifest_path']
    check_only = vars(args)['t']
    csv_output = vars(args)['c']

    if not os.path.exists(input_path):
        print('Input workbook does not exist')
        exit()
    else:
        print("Input workbook: "+input_path)

    if check_only:
        print("Only checking for issues, will not create output")
    else:
        print("Modifying tab order and checking issues")
        print("Output workbook: " + output_path)

        if not os.path.exists(manifest_path) and not check_only:
            print('Manifest does not exist')
            exit()
        else:
            print("Manifest: " + manifest_path)

            # Load the configuration/manifest
            configuration = load_manifest(manifest_path)
            fix_tabs(input_path, output_path, configuration)

    warnings = check_accessibility(input_path)
    for warning in warnings:
        print(warning.get("message"))

    print("Note that this tool cannot check for a number of common accessibility issues (codes A1, A2, A3, A7, B2, "
          "B4, B5, B6) and you should check these using other methods.")

    if csv_output:
        print("Saving a report of issues found in accessibility_report.csv")
        field_names = warnings[0].keys()
        with open('accessibility_report.csv', 'w', newline='') as csvFile:
            writer = csv.DictWriter(csvFile, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(warnings)