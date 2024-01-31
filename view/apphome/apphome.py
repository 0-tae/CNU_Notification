from view.util.view_template_manager import template_manager
from view.util.block_builder import block_builder

ACTION_GROUP = "apphome_default"


class AppHomeObject:
    def __init__(
        self,
        __apphome_name__=ACTION_GROUP,
        __apphome__=None,
        __callback_id__=f"{ACTION_GROUP}-undefind_callback_id",
    ):
        self.__apphome_name__ = __apphome_name__
        self.__apphome__ = __apphome__
        self.__callback_id__ = __callback_id__

        template_manager.add_view_template(
            template_name=ACTION_GROUP,
            template_options=(
                "line_1_default",
                "line_2_default",
            ),
        )

    def create_apphome(self):
        view = self.get_base_view()

        template = template_manager.get_view_template_by_name(ACTION_GROUP)

        template.set_template_line(
            line="line_1_default",
            block=block_builder.create_block_header(f"안녕하세요, default 슬랙봇 서비스 입니다."),
        )

        template.set_template_line(
            line="line_2_default",
            block=block_builder.create_single_block_section(f"apphome을 추가 해주세요"),
        )

        return template_manager.apply_template(view=view, template=template)

    def get_base_view(self):
        print("Get initial View")

        view = {}
        view["blocks"] = []
        view["type"] = "home"
        view["callback_id"] = self.get_callback_id()
        view["private_metadata"] = ""

        return view

    def set_apphome(self, new_apphome):
        self.__apphome__ = new_apphome

    def get_apphome(self):
        if not self.__apphome__:
            return self.get_base_view()
        else:
            return self.__apphome__

    def set_callback_id(self, new_callback_id):
        self.__callback_id__ = new_callback_id

    def get_callback_id(self):
        return self.__callback_id__

    def set_apphome_name(self, new_apphome_name):
        self.__apphome_name__ = new_apphome_name

    def get_apphome_name(self):
        return self.__apphome_name__

    def set_view_component_properties(self, view: dict, key, value):
        view[key] = {"type": "plain_text", "text": value}

    def get_id(self):
        return str(id(self))[-5:]

    def action_id(action_type):
        return f"{ACTION_GROUP}-{action_type}"


original_object = AppHomeObject()
