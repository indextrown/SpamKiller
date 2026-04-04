# spamkillerpyml

`spamkillerpyml`은 SpamKiller 프로젝트 안에서 여러 버전의 스팸 문자 모델을 실험하는 폴더입니다.

## 폴더 구성

```text
spamkillerpyml/
├── .gitignore
├── README.md
├── requirements.txt
├── sample.csv
├── data/
│   ├── split_dataset.py
│   ├── split_summary.json
│   ├── train.csv
│   ├── validation.csv
│   └── test.csv
├── benchmarks/
│   ├── benchmark_mlmodels.py
│   └── last_benchmark.json
├── v0_default/
│   └── artifacts/
│       └── SpamKitMLV1.mlmodel
├── v1_sparse_linear/
│   ├── train.py
│   ├── predict.py
│   └── artifacts/
│       ├── metrics.json
│       ├── model.json
│       └── SpamKillerPyTextClassifier.mlmodel
├── v2_embedding/
│   ├── train.py
│   ├── predict.py
│   └── artifacts/
│       ├── classifier.joblib
│       ├── config.json
│       └── metrics.json
├── v3_embedding_coreml/
│   ├── train.py
│   ├── predict.py
│   └── artifacts/
│       ├── classifier.joblib
│       ├── config.json
│       ├── metrics.json
│       └── SpamKillerEmbeddingClassifier.mlmodel
└── v4_char_cnn_coreml/
    ├── train.py
    ├── predict.py
    └── artifacts/
        ├── config.json
        ├── metrics.json
        ├── vocab.json
        ├── weights.pt
        └── SpamKillerCharCNN.mlpackage
```

## 1. 가상환경 생성

`Python 3.13` 가상환경을 권장합니다.

```bash
cd spamkillerpyml
/opt/homebrew/opt/python@3.13/bin/python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python --version
```

## 2. 데이터 분할

`sample.csv`는 원본 데이터입니다. 이 파일을 바로 학습과 벤치마크에 같이 쓰지 않고, 먼저 아래처럼 분리해서 사용합니다.

```bash
cd spamkillerpyml
source .venv/bin/activate
python data/split_dataset.py
```

생성 파일:
- `data/train.csv`: 학습용
- `data/validation.csv`: 하이퍼파라미터 조정용
- `data/test.csv`: 최종 벤치마크용
- `data/split_summary.json`: 분할 결과 요약

기본 비율:
- train `70%`
- validation `15%`
- test `15%`

## 3. 버전별 역할

- `v0_default`: Xcode GUI(Create ML)로 직접 만든 문자열 입력 Core ML 모델
- `v1_sparse_linear`: 가장 단순한 기준선 모델. Core ML `.mlmodel` 생성 가능
- `v2_embedding`: 임베딩 성능을 비교하는 테스트 버전
- `v3_embedding_coreml`: 임베딩 기반이면서 실제 Core ML `.mlmodel` 까지 생성하는 버전
- `v4_char_cnn_coreml`: Python-only 문자 기반 CNN + Core ML export 버전

### 비교표

| 버전 | 입력 형태 | 핵심 기법 | `.mlmodel/.mlpackage` 생성 | 모바일 적용 난이도 | 상태 | 한줄 평가 |
|---|---|---|---|---|---|---|
| `v0_default` | 문자열 | Xcode GUI Create ML textClassifier | 가능 | 매우 쉬움 | 동작 확인 완료 | Apple 기본 흐름 비교군 |
| `v1_sparse_linear` | 토큰 카운트 딕셔너리 | 전통적 선형 분류기 | 가능 | 보통 | 동작 확인 완료 | 가볍고 단순한 기준선 |
| `v2_embedding` | 문자열 -> 임베딩 -> 분류 | 임베딩 + 로지스틱 회귀 | 불가 | 어려움 | 동작 확인 완료 | 성능 비교용 테스트 버전 |
| `v3_embedding_coreml` | 임베딩 벡터 | 임베딩 + 로지스틱 회귀 + Core ML export | 가능 | 보통~어려움 | 동작 확인 완료 | `.mlmodel`은 나오지만 문자열 직입력은 아님 |
| `v4_char_cnn_coreml` | 문자 ID 시퀀스 | 문자 기반 CNN + Core ML export | 가능 | 보통 | 동작 확인 완료 | Python-only 실전형 후보 |

## 4. 공통 데이터

기본 학습 데이터는 [`sample.csv`](/Users/kimdonghyeon/2025/개발/앱출시/SpamKiller/SpamKiller/spamkillerpyml/sample.csv) 입니다.

```csv
text,label
무료 대출 상담 지금 바로 연락주세요,spam
오늘 회의는 3시에 시작합니다,ham
```

## 5. v1_sparse_linear

학습:

```bash
cd spamkillerpyml
source .venv/bin/activate
python v1_sparse_linear/train.py
```

예측:

```bash
cd spamkillerpyml
source .venv/bin/activate
python v1_sparse_linear/predict.py "무료 대출 상담 지금 바로 연락주세요"
```

생성 파일:
- `v1_sparse_linear/artifacts/model.json`
- `v1_sparse_linear/artifacts/metrics.json`
- `v1_sparse_linear/artifacts/SpamKillerPyTextClassifier.mlmodel`

## 6. v2_embedding

학습:

```bash
cd spamkillerpyml
source .venv/bin/activate
python v2_embedding/train.py
```

예측:

```bash
cd spamkillerpyml
source .venv/bin/activate
python v2_embedding/predict.py "무료 대출 상담 지금 바로 연락주세요"
```

생성 파일:
- `v2_embedding/artifacts/classifier.joblib`
- `v2_embedding/artifacts/config.json`
- `v2_embedding/artifacts/metrics.json`

## 7. v3_embedding_coreml

학습:

```bash
cd spamkillerpyml
source .venv/bin/activate
python v3_embedding_coreml/train.py
```

예측:

```bash
cd spamkillerpyml
source .venv/bin/activate
python v3_embedding_coreml/predict.py "무료 대출 상담 지금 바로 연락주세요"
```

생성 파일:
- `v3_embedding_coreml/artifacts/classifier.joblib`
- `v3_embedding_coreml/artifacts/config.json`
- `v3_embedding_coreml/artifacts/metrics.json`
- `v3_embedding_coreml/artifacts/SpamKillerEmbeddingClassifier.mlmodel`

## 8. v4_char_cnn_coreml

추천 상황:
- Python-only로 가고 싶을 때
- 모바일에서 임베딩 벡터화 대신 단순 문자 ID 전처리만 하고 싶을 때

학습:

```bash
cd spamkillerpyml
source .venv/bin/activate
python v4_char_cnn_coreml/train.py
```

예측:

```bash
cd spamkillerpyml
source .venv/bin/activate
python v4_char_cnn_coreml/predict.py "무료 대출 상담 지금 바로 연락주세요"
```

생성 파일:
- `v4_char_cnn_coreml/artifacts/config.json`
- `v4_char_cnn_coreml/artifacts/metrics.json`
- `v4_char_cnn_coreml/artifacts/vocab.json`
- `v4_char_cnn_coreml/artifacts/weights.pt`
- `v4_char_cnn_coreml/artifacts/SpamKillerCharCNN.mlpackage`

특징:
- Python-only
- 문자 기반 CNN
- Core ML export 가능
- 모바일에서는 문장을 문자 ID 배열로 바꾸는 정도의 전처리만 필요

## 9. mlmodel/mlpackage 벤치마크

`v0`, `v1`, `v3`, `v4` 산출물을 `data/test.csv` 기준으로 비교하는 스크립트:

```bash
cd /Users/kimdonghyeon/2025/개발/앱출시/SpamKiller/SpamKiller
./spamkillerpyml/.venv/bin/python spamkillerpyml/benchmarks/benchmark_mlmodels.py
```

실행하면 결과가 자동으로 `benchmarks/last_benchmark.json` 에 저장됩니다.

## 10. 빠른 실행 요약

```bash
cd spamkillerpyml
/opt/homebrew/opt/python@3.13/bin/python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python data/split_dataset.py
python v1_sparse_linear/train.py
python v2_embedding/train.py
python v3_embedding_coreml/train.py
python v4_char_cnn_coreml/train.py
```
