from openai import OpenAI
from fastapi import HTTPException
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from pronun_model.openai_config import OPENAI_API_KEY

import os
import re
import logging
from datetime import datetime
import pytz
from langchain.schema.retriever import BaseRetriever
from langchain.schema import Document
from typing import List
from pymongo import MongoClient

logger = logging.getLogger(__name__)

# MongoDB 데이터 로드 함수
def load_mongodb_data():
    """MongoDB에서 데이터를 가져와 텍스트와 메타데이터로 변환"""
    try:
        # MongoDB 연결
        client = MongoClient(os.getenv("MONGODB_URI"))
        db = client["medical_rag"]
        
        # 증상 데이터 로드
        symptoms_data = list(db["symptoms_rag"].find({}))
        symptoms_texts = []
        symptoms_metadatas = []
        
        for doc in symptoms_data:
            text = f"증상: {doc.get('증상', '')}\n추가 증상: {doc.get('추가 증상', '')}\n추천 진료과: {doc.get('추천 진료과', '')}"
            symptoms_texts.append(text)
            symptoms_metadatas.append({
                "증상": doc.get("증상", ""),
                "추가 증상": doc.get("추가 증상", ""),
                "추천 진료과": doc.get("추천 진료과", "")
            })
        
        # 병원 데이터 로드
        hospitals_data = list(db["hospitals_rag"].find({}))
        hospitals_texts = []
        hospitals_metadatas = []
        
        for doc in hospitals_data:
            text = f"병원이름: {doc.get('병원이름', '')}\n주소: {doc.get('주소', '')}\n영업시간: {doc.get('영업시간', '')}\n진료과목내용정보: {doc.get('진료과목내용정보', '')}"
            hospitals_texts.append(text)
            hospitals_metadatas.append({
                "병원이름": doc.get("병원이름", ""),
                "주소": doc.get("주소", ""),
                "영업시간": doc.get("영업시간", ""),
                "진료과목내용정보": doc.get("진료과목내용정보", "")
            })
        
        return symptoms_texts, symptoms_metadatas, hospitals_texts, hospitals_metadatas
    
    except Exception as e:
        logger.error(f"MongoDB 데이터 로드 중 오류 발생: {e}")
        raise


def get_retriever():
    """FAISS 벡터 스토어 및 리트리버 생성"""
    try:
        # 임베딩 모델
        embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=OPENAI_API_KEY
        )
        
        # MongoDB 데이터 로드
        symptoms_texts, symptoms_metadatas, hospitals_texts, hospitals_metadatas = load_mongodb_data()
        
        # FAISS 벡터 스토어 생성
        symptoms_vectordb = FAISS.from_texts(symptoms_texts, embeddings, metadatas=symptoms_metadatas)
        hospitals_vectordb = FAISS.from_texts(hospitals_texts, embeddings, metadatas=hospitals_metadatas)
        
        # 리트리버 생성
        symptoms_retriever = symptoms_vectordb.as_retriever(search_kwargs={"k": 3})
        hospitals_retriever = hospitals_vectordb.as_retriever(search_kwargs={"k": 8})
        
        # 계층적 검색 함수 정의 (클래스 대신 사용)
        def hierarchical_retriever(query):
            # 증상 관련 문서 검색
            symptoms_docs = symptoms_retriever.get_relevant_documents(query)
            
            # 추천 진료과 추출
            recommended_depts = []
            for doc in symptoms_docs:
                if hasattr(doc, 'metadata') and '추천 진료과' in doc.metadata:
                    depts = doc.metadata['추천 진료과'].split('/')
                    recommended_depts.extend([dept.strip() for dept in depts])
                elif hasattr(doc, 'page_content'):
                    content = doc.page_content
                    if '추천 진료과:' in content or '추천 진료과' in content:
                        if '추천 진료과:' in content:
                            dept_part = content.split('추천 진료과:')[1].split('\n')[0]
                        else:
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if '추천 진료과' in line and i+1 < len(lines):
                                    dept_part = lines[i+1]
                                    break
                            else:
                                continue
                        depts = dept_part.split('/')
                        recommended_depts.extend([dept.strip() for dept in depts])
            
            # 중복 제거
            recommended_depts = list(set(recommended_depts))
            
            # 쿼리 강화
            enhanced_query = query
            if recommended_depts:
                enhanced_query += f" 진료과: {', '.join(recommended_depts)}"
            
            # 병원 정보 검색
            hospitals_docs = hospitals_retriever.get_relevant_documents(enhanced_query)
            
            # 결과 통합
            return symptoms_docs + hospitals_docs
        
        # 함수를 리트리버처럼 작동하게 만듦
        class FunctionBasedRetriever(BaseRetriever):
            def get_relevant_documents(self, query):
                return hierarchical_retriever(query)
        
        return FunctionBasedRetriever()
        
    except Exception as e:
        logger.error(f"리트리버 생성 중 오류 발생: {e}")
        raise

# 3) 최신 방식의 QA 체인 생성
def get_qa_chain():
    retriever = get_retriever()
    llm = ChatOpenAI(
        model_name="gpt-4o-mini",
        openai_api_key=OPENAI_API_KEY,
        temperature=0
    )
    
    # 현재 한국 시간 가져오기
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    current_day_en = now.strftime("%A")  # 영어 요일
    weekday_map = {
        "Monday": "월요일", 
        "Tuesday": "화요일", 
        "Wednesday": "수요일", 
        "Thursday": "목요일", 
        "Friday": "금요일", 
        "Saturday": "토요일", 
        "Sunday": "일요일"
    }
    current_day_kr = weekday_map[current_day_en]  # 한국어 요일
    current_hour = now.hour
    current_minute = now.minute
    current_time_formatted = f"{current_hour:02d}{current_minute:02d}"  # HHMM 형식 (예: 0830)
    current_time_display = f"{current_hour:02d}:{current_minute:02d}"  # HH:MM 형식 (예: 08:30)
    
    # 문서 포맷팅 함수
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    # 프롬프트 템플릿 생성
    system_prompt = f"""
    당신은 용인 지역 병원 정보 안내 및 진료과 추천 도우미입니다. 사용자가 용인 지역 병원에 대한 정보를 요청하거나 증상에 맞는 진료과와 병원을 추천해 달라고 하면 정확하고 상세하게 안내해 주세요.

    현재 시간은 {current_day_kr}({current_day_en}) {current_time_display} (한국 시간)입니다. 병원 운영 여부와 진료 시간 안내 시 현재 시간을 참고하세요.

    [두 종류의 데이터]
    1. 증상 데이터: 다양한 증상에 대한 추천 진료과를 포함
    - 형식: 증상, 추가 증상, 추천 진료과
    - 예시: "잦은 두통, 편두통", "스트레스성 또는 긴장성 두통이 원인일 수 있음", "신경과"

    2. 병원 데이터: 용인 지역 병원 정보를 포함
    - 형식: 병원이름, 주소, 영업시간, 진료과목내용정보
    - 예시: "(의)영문의료재단다보스병원", "경기도 용인시 처인구...", "월요일: 0830~1730...", "내과, 신경과..."

    [진료과 추천 및 병원 안내 가이드라인]
    1. 사용자가 증상이나 아픈 부위를 언급하면:
    a) 사용자의 증상과 불편함에 대해 공감을 표현하세요.
    b) 이러한 증상이 일반적으로 어떤 질환이나 상태를 의심할 수 있는지 간략히 설명하세요.
    c) 증상 데이터에서 관련 정보를 찾아 적합한 진료과를 식별하고 추천하세요.
    d) 만약 증상 데이터에서 관련 정보를 찾지 못했다면, 의학적 지식을 바탕으로 적절한 진료과 추천하세요.

    2. 사용자가 특정 병원 정보를 요청하면:
    관련 병원 정보를 직접 제공

    3. 추천한 진료과가 있는 병원들을 찾아 안내해 주세요.
    - 필요한 모든 진료과가 있는 병원을 우선 추천하세요.
    - 한 병원에서 모든 진료과를 볼 수 없는 경우, 없는 진료과에 한해 다른 병원을 추가 추천하세요.

    [현재 시간 기반 병원 추천]
    1. 영업시간 형식은 "요일: HHMM~HHMM" 형식으로 되어 있습니다. (예: 월요일: 0830~1730)
    2. 현재 시간({current_day_kr} {current_time_display})에 열려있는 병원을 확인하세요.
    - 현재 요일과 시간(HHMM 형식: {current_time_formatted})을 영업시간과 비교하세요.
    - 예: 현재 월요일 09:30이라면, "월요일: 0830~1730"인 병원은 영업 중입니다.
    3. 열려있는 병원을 우선적으로 추천하세요.
    4. 현재 닫혀있는 경우:
    - 오늘 이후 다음 영업일과 시간을 확인하세요.
    - 다음날 가장 빠르게 열리는 병원을 우선적으로 추천하세요.
    - 항상 추천한 진료과가 있는 병원 중에서만 선택하세요.

    [응답 형식]
    1. 응답은 다음과 같은 구조로 작성하세요:
        a) 먼저 사용자의 증상에 공감하는 문장으로 시작하세요. 예: "무거운걸 들다가 삐끗하신 이후로 어깨가 아프셨군요! 많이 불편하셨겠어요."
        b) 그 다음 이러한 증상이 일반적으로 어떤 질환일 수 있는지 설명하세요. 예: "일반적으로 그런 경우에 어깨 염좌를 의심할 수 있어요."
        c) 권장 진료과를 명확히 안내하세요. 예: "증상이 지속된다면 정형외과로 방문해보시는 것을 추천드려요."
        d) 현재 영업 중인 병원이 있는지 상태를 설명하고, 없으면 다음 영업일이 언제인지만 간략히 언급하세요.
        e) 응답의 마지막은 반드시 "추천 병원을 알려드릴까요?"라는 문장으로 끝내세요.
    2. 정보를 구분할 때는 마침표와 단일 공백만 사용하세요. 연속된 공백은 사용하지 마세요.
    3. 병원 이름, 주소, 영업시간, 진료과목 등은 응답에 포함하지 마세요.
    4. 응답은 친절하고 공감적인 톤으로, 간결하고 명확하게 작성하세요.

    컨텍스트에 없는 정보는 추측하지 말고, "해당 정보는 제공된 데이터에 없습니다"라고 솔직하게 답변하세요.
    사용자가 용인 지역 외 병원 정보를 요청하면, "현재 용인 지역 병원 정보만 제공 가능합니다"라고 안내하세요.
    """
    
    # 병원 이름 추출 함수
    def extract_hospitals(docs):
        hospital_names = []
        for doc in docs:
            content = doc.page_content
            if "병원이름:" in content:
                hospital_name = content.split("병원이름:")[1].split("\n")[0].strip()
                hospital_names.append(hospital_name)
        
        # 중복 제거 및 최대 3개로 제한
        return list(set(hospital_names))[:3]

    # 매우 간단한 체인 구현
    def simple_qa_chain(question):
        # 1. 문서 검색
        docs = retriever.get_relevant_documents(question)
        
        hospitals = extract_hospitals(docs)

        # 2. 문서 형식 변환
        formatted_docs = " ".join(doc.page_content for doc in docs)
        
        # 3. 프롬프트 구성
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"질문과 관련된 문서입니다: {formatted_docs} 질문: {question}"}
        ]
        
        # 4. LLM 호출
        response = llm.invoke(messages)
        
        # 응답 후처리 - 더 강화된 버전
        processed_response = response.content
        # 5. 모든 줄바꿈을 공백으로 변환
        processed_response = processed_response.replace("\n", " ")
        # 6. 연속된 공백을 하나의 공백으로 변환 (정규식 사용)
        processed_response = re.sub(r'\s+', ' ', processed_response)
        # 7. 문장 앞뒤 공백 제거
        processed_response = processed_response.strip()
        
        # 8. 결과 반환 - 딕셔너리로 변경
        return {
            "answer": processed_response,
            "hospitals": hospitals
        }
    
    return simple_qa_chain


# 4) 질의 함수
def ask_question(question: str) -> dict:
    """
    RAG 기반 질의:
    
    1) 먼저 벡터 DB에서 관련 문서 검색 (계층적 검색 방식 적용)
    2) 검색된 컨텍스트와 질문을 합쳐서 LLM에 전달
    3) 응답 및 병원 목록 반환
    """
    try:
        qa_chain = get_qa_chain()
        result = qa_chain(question)
        return result  # 이제 {"answer": "...", "hospitals": [...]} 형태의 딕셔너리 반환
    except Exception as e:
        logger.error(f"RAG 질의 중 오류 발생: {e}", extra={
            "errorType": type(e).__name__,
            "error_message": str(e)
        })
        raise HTTPException(status_code=500, detail=f"RAG 질의 오류: {e}")