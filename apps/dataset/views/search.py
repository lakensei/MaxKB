import json
from collections import defaultdict

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import Permission, Group, Operate
from common.response import result
from common.swagger_api.common_api import CommonApi
from dataset.serializers.dataset_serializers import DataSetSerializers


class DocumentSearch(APIView):
    authentication_classes = [TokenAuth]

    @action(methods="GET", detail=False)
    @swagger_auto_schema(operation_summary="文档检索列表", operation_id="文档检索列表",
                         manual_parameters=CommonApi.HitTestApi.get_request_params_api(),
                         responses=result.get_api_array_response(CommonApi.HitTestApi.get_response_body_api()),
                         tags=["知识库"])
    @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.USE,
                                                    dynamic_tag=keywords.get('dataset_id')))
    def get(self, request: Request, dataset_id: str):
        hit_list = DataSetSerializers.HitSearch(data={'id': dataset_id, 'user_id': request.user.id,
                                                      "query_text": request.query_params.get("query_text"),
                                                      "top_number": request.query_params.get("top_number"),
                                                      'similarity': request.query_params.get('similarity'),
                                                      'search_mode': request.query_params.get('search_mode')}).search()
        # 根据document_id 分组
        res_list = []
        document_dict = defaultdict(list)
        for item in hit_list:
            document_dict[(item["document_id"], item["document_name"], item["document_meta"])].append({
                "similarity": item.get("similarity", 0),
                "comprehensive_score": item.get("comprehensive_score"),
                "content": item["content"],
                "title": item["title"],
            })
        for k, v in document_dict.items():
            v.sort(key=lambda x: x["similarity"], reverse=True)
            res_list.append({
                "document_id": k[0],
                "document_name": k[1],
                "document_meta": json.loads(k[2]),
                "paragraph_list": v
            })
        return result.success(res_list)
