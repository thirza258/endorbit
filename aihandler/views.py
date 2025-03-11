from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from rest_framework.generics import ListAPIView
from .models import Product, ResponseModel
from .serializers import ProductSerializer
from .main import rag_index
import json
import re

class GetAllProduct(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
class ChatCommerceService(APIView):
    def post(self, request):
        # try:
            input_user = request.data['input_user']
            llm = init_chat_model("gpt-4o-mini", model_provider="openai")
            retrieved_product = rag_index.retrieve_documents(input_user, k=5)

            product_context = "\n\n".join([
                f"Product Name: {json.loads(doc)['product_name']}\n"
                f"Description: {json.loads(doc)['description']}\n"
                f"Price: {json.loads(doc)['retail_price']}\n"
                f"URL: {json.loads(doc)['product_url']}\n"
                f"Brand: {json.loads(doc)['brand']}"
                for doc in retrieved_product
            ])

            parser = JsonOutputParser(pydantic_object=ResponseModel)
            
            prompt = PromptTemplate(
                template="""
                You are an AI assistant using retrieved products from a database to help users with their shopping needs.
                You have access to a context that is a list of products with their respective details.
                The user will ask you questions about the products, and you will provide the answers or suggest products based on their needs.

                <RETRIEVED_PRODUCTS>
                {product_context}
                </RETRIEVED_PRODUCTS>

                <USER_INPUT>
                {input_user}
                </USER_INPUT>

                <AI_OUTPUT>
                Format your response as a valid JSON object **without comments** matching this schema:
                {format_instructions}
                </AI_OUTPUT>
                """,
                input_variables=["product_context", "input_user"],
                partial_variables={"format_instructions": parser.get_format_instructions()}
            )

            pipeline = prompt | llm | parser
            raw_response = pipeline.invoke({"input_user": input_user, "product_context": product_context})
            
            return Response({
                "status": 200,
                "message": "Success",
                "data": raw_response
            }, status=status.HTTP_200_OK)
        # except Exception as e:
        #     return Response({
        #         "status": 500,
        #         "message": "Internal server error",
        #         "data": str(e)
        #     }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)