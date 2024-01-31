from view.util.block_builder import block_builder
from view.util.view_template_manager import template_manager
from view.modals.modal import ModalObject

ACTION_GROUP = "apphome_not_verified_user"
DEVELOPER_NAME = "YongTaekBot"


class NotVerifiedUserModalObject(ModalObject):
    # 템플릿 매니저에 모달 뷰 템플릿을 정의
    def __init__(
        self,
        __modal_name__=ACTION_GROUP,
        __modal__=None,
        __modal_title__="사용자 인증",
        __callback_id__=f"{ACTION_GROUP}-modal_submit",
    ):
        super().__init__(__modal_name__, __modal__, __modal_title__, __callback_id__)

        template_manager.add_view_template(
            template_name=ACTION_GROUP,
            template_options=(
                "line_3_input_enterprise_name",  # 회사 이름 입력
                "line_4_input_user_email",  # 계정 이메일
                "line_5_button_send_code",  # 코드 전송 버튼
                "line_6_divider",  # 줄 나누기
                "line_7_input_code",  # 코드 입력
                "line_8_button_verify_code",  # 인증 하기 버튼
                "line_9_context_text",  # 인증에 성공 하거나, 인증 시간을 안내하거나, 유효성 검사 실패 시 나타나는 메시지
            ),
        )

    # 일정 등록 모달창을 생성함
    def create_modal(self):
        template = template_manager.get_view_template_by_name(ACTION_GROUP)

        template.set_template_line(
            line="line_3_input_enterprise_name",
            block=block_builder.create_input_text(
                label="기업명",
                action_id=self.action_id("input_enterprise_name"),
                optional=False,
            ),
        )
        template.set_template_line(
            line="line_4_input_user_email",
            block=block_builder.create_input_text(
                label="Exosphere ID(Email)",
                action_id=self.action_id("input_user_email"),
                optional=False,
            ),
        )
        template.set_template_line(
            line="line_5_button_send_code",
            block=block_builder.create_actions(
                actions=(
                    block_builder.create_button(
                        text="인증 코드 전송", action_id=self.action_id("send_code")
                    ),
                )
            ),
        )
        template.set_template_line(
            line="line_6_divider",
            block=block_builder.create_block_divider(),
        )
        template.set_template_line(
            line="line_7_input_code",
            block=block_builder.create_input_text(
                label="인증 코드", action_id=self.action_id("input_code"), optional=False
            ),
        )
        template.set_template_line(
            line="line_8_button_verify_code",
            block=block_builder.create_actions(
                actions=(
                    block_builder.create_button(
                        text="인증 하기", action_id=self.action_id("verify_code")
                    ),
                )
            ),
        )
        template.set_template_line(
            line="line_9_context_text",
            block=block_builder.create_single_block_context("인증 코드의 유효 시간은 3분 입니다."),
        )

        # base_view에 template에 쓰여진 blocks를 적용
        # base_view의 private_metadata를 통해 캐시를 등록
        # template_cache_id는 현재 인스턴스 주소 값의 일부
        modal = template_manager.apply_template(
            view=self.get_modal(),
            template=template,
            cache_id=self.get_modal()["private_metadata"],
        )

        # 현재 인스턴스의 modal을 변경
        self.set_modal(modal)

        return modal

    def update_modal_verified(self, original_view, text, code=None):
        updated_template = template_manager.get_view_template_by_name(ACTION_GROUP)

        updated_template.convert_view_to_template(view=original_view)

        updated_template.set_template_line(
            line="line_8_button_verify_code",
            block=block_builder.create_actions(
                actions=(
                    block_builder.create_button(
                        text="인증 하기",
                        action_id=self.action_id("verify_code"),
                        value=code,
                    ),
                )
            ),
        )

        updated_template.set_template_line(
            line="line_9_context_text",
            block=block_builder.create_single_block_context(text),
        )

        # base_view에 template에 쓰여진 blocks를 적용
        # base_view의 private_metadata를 통해 캐시를 등록
        # template_cache_id는 현재 인스턴스 주소 값의 일부
        modal = template_manager.apply_template(
            view=self.get_modal(),
            template=updated_template,
            cache_id=self.get_modal()["private_metadata"],
        )

        # 인스턴스의 modal을 변경하지 않음(정보 유지를 하지 않음)

        return modal

    def action_id(self, action_type):
        return f"{ACTION_GROUP}-{action_type}"


original_object = NotVerifiedUserModalObject()
