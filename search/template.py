import logging

from search.opensearch import OpenSearchClient
from util import load_json_body_from_file

INDEX_TEMPLATE_NAME = "jc_products"
COMPONENT_NAME_SETTINGS = "jc_settings"
COMPONENT_NAME_DYN_MAPPINGS = "jc_dynamic_template"

tpl_logging = logging.getLogger("template")


class OpenSearchTemplate:

    def __init__(self, client: OpenSearchClient):
        self.client = client

    def create_update_template(self):
        """ Check the version of the current template and update if necessary """
        tpl_logging.info("Initialize or update the product template in OpenSearch.")

        self.__update_settings_component()
        self.__update_dynamic_mapping_component()
        self.__update_index_template()

    def __update_settings_component(self):
        body = load_json_body_from_file(file_name="./config_files/component_settings.json")
        required_version = body['version']
        settings_needs_update = self.__component_needs_update(component_name=COMPONENT_NAME_SETTINGS,
                                                              current_version=required_version)
        if settings_needs_update:
            tpl_logging.info("Update the settings component template to version %d.", required_version)
            self.client.set_component_template(name=COMPONENT_NAME_SETTINGS, body=body)
        else:
            tpl_logging.info("The version %d of the settings component template is up-to-date", required_version)

    def __update_dynamic_mapping_component(self):
        body = load_json_body_from_file(file_name="./config_files/component_dynamic_mappings.json")
        required_version = body['version']
        component_needs_update = self.__component_needs_update(component_name=COMPONENT_NAME_DYN_MAPPINGS,
                                                               current_version=required_version)

        if component_needs_update:
            tpl_logging.info("Update the dynamic mappings component template to version %d.", required_version)
            self.client.set_component_template(name=COMPONENT_NAME_DYN_MAPPINGS, body=body)
        else:
            tpl_logging.info("The version %d of the dynamic mappings component template is up-to-date",
                             required_version)

    def __update_index_template(self):
        body = load_json_body_from_file(file_name="./config_files/index_template_products.json")
        required_version = body['version']
        template_needs_update = self.__template_needs_update(template_name=INDEX_TEMPLATE_NAME,
                                                             current_version=required_version)

        if template_needs_update:
            tpl_logging.info("Update the template to version %d.", required_version)
            self.client.set_index_template(name=INDEX_TEMPLATE_NAME, body=body)
        else:
            tpl_logging.info("The version %d of the index template is up-to-date", required_version)

    def __template_needs_update(self, template_name: str, current_version):
        """ The template needs to update if there is no template or if the versions do not match """
        if not self.client.does_index_template_exist(name=template_name):
            tpl_logging.debug("The template with name '%s' is not found", template_name)
            return True

        response = self.client.get_index_template(name=template_name)
        tpl_logging.debug(response)

        templates = response['index_templates']
        if len(templates) != 1:
            raise Exception("We cannot have matching more than 1 template while looking for " + template_name)

        index_template = templates[0]['index_template']
        return not (index_template.get("version") == current_version)

    def __component_needs_update(self, component_name: str, current_version):
        """ The template needs to update if there is no template or if the versions do not match """
        tpl_logging.debug("Obtain the component template with name '%s'", component_name)
        if not self.client.does_component_template_exist(name=component_name):
            tpl_logging.debug("The component template with name '%s' is not found", component_name)
            return True

        response = self.client.get_component_template(name=component_name)
        tpl_logging.debug(response)

        components = response['component_templates']
        if len(components) != 1:
            raise Exception("We cannot have matching more than 1 component while looking for " + component_name)

        component_template = components[0]['component_template']
        return not (component_template.get("version") == current_version)
