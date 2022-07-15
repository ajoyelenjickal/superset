# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import logging

from flask import Response, request
from flask_appbuilder.api import expose
from flask_appbuilder.models.sqla.interface import SQLAInterface

from superset.constants import MODEL_API_RW_METHOD_PERMISSION_MAP
from superset.models.core import Comments
from superset.views.base_api import BaseSupersetModelRestApi, requires_json

logger = logging.getLogger(__name__)


class ChartCommentsRestApi(BaseSupersetModelRestApi):
    datamodel = SQLAInterface(Comments)
    class_permission_name = "Comments"
    method_permission_name = MODEL_API_RW_METHOD_PERMISSION_MAP

    resource_name = "comments"
    allow_browser_login = True
    include_route_methods = {"get_comments", "post_comments"}

    list_columns = [
        "id",
        "txt",
    ]

    add_columns = ["txt"]

    @expose("/<int:pk>/get_comments", methods=["GET"])
    def get_comments(self, pk: int) -> Response:
        """Get Chart comments
        ---
        get:
          description: Get Chart Comments.
          parameters:
          - in: path
            schema:
              type: integer
            name: pk
          responses:
            200:
              description: Comments Result
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message:
                        type: string
            400:
              $ref: '#/components/responses/400'
            401:
              $ref: '#/components/responses/401'
            404:
              $ref: '#/components/responses/404'
            500:
              $ref: '#/components/responses/500'
        """

        comment = self.datamodel.get(pk)
        if not comment:
            return self.response_404()

        return self.response(200, result={"id": comment.id, "comment": comment.txt})

    @expose("/post_comments", methods=["POST"])
    @requires_json
    def post_comments(self) -> Response:
        """Creates a new Comments
        ---
        post:
          description: >-
            Create a new Comments.
          requestBody:
            description: Comments schema
            required: true
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/{{self.__class__.__name__}}.post'
          responses:
            201:
              description: Comments added
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      id:
                        type: number
                      result:
                        $ref: '#/components/schemas/{{self.__class__.__name__}}.post'
            400:
              $ref: '#/components/responses/400'
            401:
              $ref: '#/components/responses/401'
            422:
              $ref: '#/components/responses/422'
            500:
              $ref: '#/components/responses/500'
        """
        try:
            comment = self.add_model_schema.load(request.json)
            self.datamodel.add(comment)
            return self.response(201, id=comment.id, result=comment.txt)
        except Exception as ex:
            logger.error(
                "Error creating model %s: %s",
                self.__class__.__name__,
                str(ex),
                exc_info=True,
            )
            return self.response_422(message=str(ex))
