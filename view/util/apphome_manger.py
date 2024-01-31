from domain.slack.slack_api import slackAPI
import domain.slack.slack_utils as util
import copy, glob, os, importlib
from domain.exosphere.exoshpere_api import exosphereApi
from domain.user.role import UserRole
from exception.exception_handling_decorator import handler

NOT_VERIFIED = "apphome-not_verified_user"
DEVELOPER_NAME = "Exosphere"


# Apphome은 View로 구성됨
class AppHomeManager:
    def __init__(self, __apphome_dict__=dict(), __cache_dict__=dict()):
        # apphome_dict : 앱홈 이름에 해당하는 apphomeObject 인스턴스를 등록 및 조회
        self.__apphome_dict__ = __apphome_dict__
        self.__cache_dict__ = __cache_dict__

        # 디렉토리 경로 설정
        directory_path = "view/apphome"  # 실제 디렉토리 경로로 변경

        # 디렉토리 안의 모든 .py 파일을 가져옴
        module_files = glob.glob(os.path.join(directory_path, "*.py"))

        # .py 확장자를 제거하고 모듈명만 추출
        module_names = [
            os.path.splitext(os.path.basename(file))[0] for file in module_files
        ]

        # module의 인스턴스 가져오기
        for module_name in module_names:
            try:
                module = importlib.import_module(f"view.apphome.{module_name}")
                object_name = "original_object"
                instance = getattr(module, object_name)
                self.add_apphome_object(instance)
            except ImportError as e:
                util.debug_message(f"Error: {e.args[1]}")

    def publish(self, view, user_id):
        slackAPI.app_home_publish(user_id=user_id, view=view)

    # 유저별 초기 Apphome 구성하기
    def init_app_home(self):
        user_list = slackAPI.get_user_list()
        for users in user_list:
            for user in users:
                user_id = user["user_id"]
                view = self.get_view_by_user(user_id)
                self.publish(view=view, user_id=user_id)

    # TODO: 여기에다 배치하는 것이 맞을까?
    # 유저별 role에 따라 view를 가져옴
    def get_view_by_user(self, user_id):
        apphome_name_by_role = {
            UserRole.MANAGER: None,
            UserRole.APPROVER: "apphome_approver",
            UserRole.BASIC: "apphome_basic_user",
            UserRole.NOT_VERIFIED: "apphome_not_verified_user",
        }

        # TODO: user_id를 엑소스피어 API를 조회하여 role을 알아냄
        # user_info = exosphereApi.read_user_by_slack_user_id(user_id)
        user_info = exosphereApi.get_user_info_by_id(slack_user_id=user_id)

        # TODO: 조회되지 않았다면 미인증 유저로 판단
        role = UserRole.NOT_VERIFIED if not user_info else user_info.role

        return self.get_apphome_by_name(
            apphome_name=apphome_name_by_role[role], cache_id=user_id
        )

    # 캐시를 조회하고 apphome을 가져오기
    def get_apphome_object_by_name(self, apphome_name, cache_id=None):
        apphome_object = self.__get_apphome_dict__().get(apphome_name)

        if not apphome_object:
            raise ValueError(
                f"해당하는 모달이 존재하지 않음 : {apphome_name}, apphomeObject를 apphomeManager에 등록하세요"
            )

        # 캐싱되어 있는 apphomeObject가 있다면 객체를 가져옴
        if self.__has_cache__(cache_id):
            apphome_object = self.__get_cache__(cache_id)

            # 캐시된 apphomeObject와 apphome_name이 같을 때 apphome을 가져옴
            if apphome_object.get_apphome_name() == apphome_name:
                return apphome_object

        # 캐싱 되어있지 않다면 apphomeObject Class의 초기 객체를 복사해서 가져옴
        apphome_object = copy.deepcopy(apphome_object)

        # 캐시 아이디가 주어졌다면, apphomeObject에 대한 캐시 업데이트
        if cache_id != None:
            self.__update_cache__(cache_id, apphome_object)

        return apphome_object

    def get_apphome_by_name(self, apphome_name, cache_id=None):
        apphome_object = self.__get_apphome_dict__().get(apphome_name)

        if not apphome_object:
            raise ValueError(f"해당하는 모달이 존재하지 않음 : {apphome_name}")

        # 캐싱되어 있는 apphomeObject가 있다면 객체를 가져옴
        if self.__has_cache__(cache_id):
            cached_apphome_object = self.__get_cache__(cache_id)

            # 캐시된 apphomeObject와 apphome_name이 같을 때 apphome을 가져옴
            if cached_apphome_object.get_apphome_name() == apphome_name:
                return cached_apphome_object.get_apphome()

        # 캐싱 되어있지 않다면 apphomeObject Class의 초기 객체를 복사해서 가져옴
        apphome_object = copy.deepcopy(apphome_object)

        # 캐시 아이디가 주어졌다면, apphomeObject에 대한 캐시 업데이트
        if cache_id != None:
            self.__update_cache__(cache_id, apphome_object)

        return apphome_object.create_apphome()

    # apphomeObject의 초기 객체를 등록
    def add_apphome_object(self, apphome):
        # ex) {"event" : CalendarEventapphome()}
        self.__get_apphome_dict__().update({apphome.get_apphome_name(): apphome})

    def __get_apphome_dict__(self) -> dict:
        return self.__apphome_dict__

    def __get_cache_dict__(self) -> dict:
        return self.__cache_dict__

    def __get_cache__(self, cache_id):
        if not cache_id:
            return None

        return self.__get_cache_dict__().get(cache_id)

    def __has_cache__(self, cache_id):
        return cache_id != None and self.__get_cache_dict__().get(cache_id) != None

    def __destroy_cache_all__(self):
        self.__get_cache_dict__().clear()

    def __destroy_cache__(self, cache_id):
        if self.__has_cache__(cache_id):
            return self.__get_cache_dict__().pop(cache_id)

    def __update_cache__(self, cache_id, apphome_object):
        self.__get_cache_dict__().update({cache_id: apphome_object})


@handler.http_error_handle
def execute_func_with_exception_handler(*args):
    (func, param) = args[0]
    return func(param)


apphome_manager = AppHomeManager()
apphome_manager.init_app_home()
