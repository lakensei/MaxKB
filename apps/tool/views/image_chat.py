from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import Permission, Group, Operate, \
    RoleConstants, ViewPermission
from tool.serializers.chat_message_serializers import ChatMessageSerializer
from tool.swagger_api.chat_api import ChatApi


class ImageChat(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="图片对话",
                         operation_id="图片对话",
                         request_body=ChatApi.get_request_body_api(),
                         tags=["应用/会话"])
    @has_permissions(
        ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_KEY],
                       [lambda r, keywords: Permission(group=Group.TOOL, operate=Operate.USE)])
    )
    def post(self, request: Request):
        return ChatMessageSerializer(data=request.data).chat()
