# Shopping Signal Analyzer

Amazon 리뷰 텍스트를 구조화된 고객 반응 신호로 변환하는, `pandas` 중심의 간단한 MVP 프로젝트입니다.

## 프로젝트 개요

이 프로젝트는 다음 작업을 수행합니다.

- 원본 리뷰 CSV를 안전하게 불러옵니다. 기본 입력 경로는 `data/raw/Amazon_Reviews.csv`입니다.
- 입력 컬럼명을 추론하고 아래 표준 컬럼으로 정규화합니다.
  `review_text`, `rating`, `date`, `category`, `sentiment_score`, `sentiment_label`
- 텍스트를 정제하고, 평점 문자열을 숫자로 파싱하며, 가능한 경우 리뷰 제목과 본문을 합칩니다.
- 정규화된 기준으로 완전 중복 리뷰를 제거합니다.
- 규칙 기반 카테고리 라벨링을 적용합니다.
- 긍정/부정 단어 수를 기반으로 규칙 기반 감정 점수와 라벨을 생성합니다.
- 처리 결과 CSV, 차트, 마크다운 인사이트 리포트를 저장합니다.
- 전체 흐름을 재현할 수 있는 노트북을 포함합니다.

## 프로젝트 구조

```text
Shopping-Signal-Analyzer/
|- data/
|  |- processed/
|  `- raw/
|     `- Amazon_Reviews.csv
|- notebooks/
|  `- shopping_signal_mvp.ipynb
|- reports/
|  |- figures/
|  `- insight_report.md
|- src/
|  |- __init__.py
|  |- feature_engineering.py
|  |- labeler.py
|  |- preprocess.py
|  |- sentiment.py
|  `- visualize.py
|- requirements.txt
`- README.md
```

## 설치

```bash
pip install -r requirements.txt
```

노트북과 출력 경로가 올바르게 동작하도록, 저장소 루트에서 명령을 실행하는 것을 권장합니다.

## 입력 데이터 처리 방식

이 파이프라인은 실제 리뷰 CSV처럼 컬럼명과 형식이 일정하지 않은 데이터도 처리할 수 있도록 설계되었습니다.

현재 지원하는 항목은 다음과 같습니다.

- `Review Text`, `Review Date`, `Date of Experience`, `Rating`, `Review Title` 같은 컬럼명 변형 처리
- `Rated 1 out of 5 stars` 같은 평점 문자열 파싱
- 가능한 경우 다른 후보 컬럼을 이용한 결측값 보완
- 기본 `pandas` CSV 엔진에서 실패할 때를 대비한 안전한 파싱 fallback
- 실제 `data/raw/Amazon_Reviews.csv` 또는 작은 데모 파일을 사용하는 노트북 실행 흐름

노트북은 아래 순서로 입력 파일을 탐색합니다.

- `data/raw/Amazon_Reviews.csv`
- `amazon_reviews.csv`
- `data/raw/amazon_reviews.csv`
- `data/raw/demo_amazon_reviews.csv`
- `Amazon_Reviews.csv`

## 현재 규칙 기반 카테고리

- `customer_service`
- `delivery_shipping`
- `refunds_returns`
- `account_access`
- `pricing_billing`
- `prime_membership`
- `product_quality`
- `order_management`
- `other`

## 노트북 실행

```bash
jupyter notebook notebooks/shopping_signal_mvp.ipynb
```

노트북 실행 흐름은 다음과 같습니다.

1. 리뷰 CSV 경로를 확인합니다.
2. 안전한 파싱 fallback과 함께 CSV를 불러옵니다.
3. 내부 표준 스키마에 맞게 컬럼명을 정규화합니다.
4. 카테고리와 감정 라벨을 생성합니다.
5. 처리 결과, 차트, 인사이트 리포트를 저장합니다.

리뷰 CSV를 찾지 못하면, 노트북은 `data/raw/demo_amazon_reviews.csv`에 작은 데모 파일을 생성합니다.

## 생성 산출물

노트북을 실행하면 아래 파일들이 생성됩니다.

- `data/processed/reviews_with_signals.csv`
- `data/processed/category_summary.csv`
- `data/processed/sentiment_summary.csv`
- `data/processed/monthly_sentiment_summary.csv`
- `reports/figures/category_review_count.png`
- `reports/figures/category_avg_sentiment.png`
- `reports/insight_report.md`

## MVP 메모

- 카테고리 라벨링은 규칙 기반이며, 현재 Amazon 리뷰 데이터셋에 맞춰 조정되어 있습니다.
- 감정 분석은 규칙 기반이며, 단어 수 기반 점수와 작은 평점 보정을 함께 사용합니다.
- 리포트는 차트와 동일한 summary 테이블을 바탕으로 생성됩니다.
- 코드는 과도하게 복잡하게 만들지 않고, 단순하고 모듈화된 구조를 유지합니다.
