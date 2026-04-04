# 🚫 SpamKiller - iOS 스팸 문자 필터링 앱

스팸 문자를 자동으로 차단하고 정크함으로 분류하는 iOS 애플리케이션입니다. 키워드 기반 필터링과 온디바이스 머신러닝 기술을 결합하여 사용자가 원하지 않는 메시지를 효율적으로 관리합니다.

---

## 📋 목차

- [프로젝트 개요](#프로젝트-개요)
- [주요 기능](#주요-기능)
- [시스템 아키텍처](#시스템-아키텍처)
- [기술 스택](#기술-스택)
- [프로젝트 구조](#프로젝트-구조)
- [핵심 모듈 설명](#핵심-모듈-설명)
  - [1. 메인 앱 (SpamKiller)](#1-메인-앱-spamkiller)
  - [2. 메시지 필터 확장 (SpamKillerMessageFilter)](#2-메시지-필터-확장-spamkillermessagefilter)
  - [3. 공유 모듈 (Shared)](#3-공유-모듈-shared)
  - [4. 테스트 스위트 (SpamKillerTests)](#4-테스트-스위트-spamkillertests)
- [설정 및 실행](#설정-및-실행)
- [사용 방법](#사용-방법)
- [개발 가이드](#개발-가이드)
  - [머신러닝 모델 개발 및 강화 가이드](#머신러닝-모델-개발-및-강화-가이드)
- [문제 해결](#문제-해결)

---

## 프로젝트 개요

**앱명**: SpamKiller  
**플랫폼**: iOS  
**최소 타겟**: iOS 15.0+  
**개발 언어**: Swift, SwiftUI  
**아키텍처 패턴**: MVVM (Model-View-ViewModel)

### 목표
- iOS 메시지 앱과 통합되어 **자동으로 스팸 메시지를 필터링**
- 사용자 정의 키워드를 통한 **우선 필터링**
- 온디바이스 AI(Core ML)를 통한 **고급 스팸 판정**
- 사용자 프라이버시 보호 (기기 내에서만 데이터 처리)

---

## 주요 기능

### 1️⃣ 키워드 기반 필터링
- 사용자가 직접 스팸 키워드 등록 및 관리
- 등록된 키워드가 포함된 메시지는 자동으로 정크함(Junk)으로 분류
- **UI**: MainView에서 직관적인 추가/삭제 인터페이스 제공

### 2️⃣ 로컬 AI 모드 (베타)
- 온디바이스 머신러닝(Core ML 모델)을 활용한 스팸 판정
- 사용자 데이터가 기기를 벗어나지 않음 (오프라인 처리)
- **설정**: SettingView에서 "로컬 AI 모드(베타 버전)" 토글로 활성화/비활성화
- SpamKitMLV1.mlpackage 모델 사용

### 3️⃣ 메시지 필터 확장 (Message Filter Extension)
- iOS의 IdentityLookup 프레임워크 통합
- 수신되는 모든 SMS/MMS에 대해 자동 필터링 적용
- OS 수준의 메시지 필터링으로 높은 신뢰도 보장

### 4️⃣ 기본 정책 필터링
- 빈 메시지: 제외
- 숫자만 있는 메시지: 제외
- 1글자 이하의 메시지: 제외
- 정상 메시지의 오분류 방지

---

## 시스템 아키텍처

### 전체 구조도

```
┌─────────────────────────────────────────────────────────────┐
│                    iOS Message System                       │
│                  (수신된 SMS/MMS)                           │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────▼──────────────┐
         │ IdentityLookup Framework │
         └───────────┬──────────────┘
                     │
    ┌────────────────▼────────────────────┐
    │ MessageFilterExtension              │
    │ (ILMessageFilterExtension)          │
    │                                    │
    │ 3계층 필터링:                       │
    │ ├─ 1. Policy (정책)               │
    │ ├─ 2. Keyword (키워드)            │
    │ └─ 3. ML (머신러닝)               │
    └────┬───────────────────────────────┘
         │
         ├─ ILMessageFilterAction.junk
         ├─ ILMessageFilterAction.allow
         └─ ILMessageFilterAction.none

         ↓ (App Group UserDefaults 공유)

┌─────────────────────────────────────────┐
│         SpamKiller App                  │
│         (메인 앱)                        │
│                                        │
│ ┌──────────────┐  ┌──────────────┐   │
│ │  MainView    │  │ SettingView  │   │
│ │ (키워드관리) │  │   (설정)     │   │
│ └──────┬───────┘  └──────┬───────┘   │
│        │                 │            │
│        └────────┬────────┘            │
│               │                      │
│   ┌───────────▼──────────┐          │
│   │ ContentViewModel     │          │
│   │ (@Published 상태)   │          │
│   └───────────┬──────────┘          │
│               │                     │
│   ┌───────────▼──────────┐         │
│   │ SharedStore          │         │
│   │ (Singleton)          │         │
│   └──────────────────────┘         │
│               │                    │
│   ┌───────────▼──────────┐        │
│   │UserDefaults(App Group)       │
│   │group.com.            │        │
│   │indextrown.SpamKiller│        │
│   └──────────────────────┘        │
└─────────────────────────────────────┘
```

### MVVM 계층 구조

```
┌─────────────────────────────────────┐
│  Views (UI Layer)                   │
│  ├─ SpamKillerApp (진입점)          │
│  ├─ TabBarView (탭 네비게이션)      │
│  ├─ MainView (키워드 목록)          │
│  ├─ SettingView (설정)              │
│  └─ HelpView (도움말)               │
└──────────────┬──────────────────────┘
               │ @EnvironmentObject
┌──────────────▼──────────────────────┐
│  ViewModels (Logic Layer)           │
│  └─ ContentViewModel                │
│     ├─ @Published keywords          │
│     ├─ @Published isOnDeviceEnabled │
│     ├─ loadKeywords()               │
│     └─ setOnDeviceEnabled()         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Data Layer                         │
│  ├─ SharedStore (싱글톤)            │
│  ├─ AppGroup (상수 모음)            │
│  └─ UserDefaults (App Group)        │
└─────────────────────────────────────┘
```

---

## 기술 스택

| 항목 | 기술 |
|------|------|
| **언어** | Swift 5.9+ |
| **UI 프레임워크** | SwiftUI |
| **데이터 저장** | UserDefaults (App Group) |
| **머신러닝** | Core ML (SpamKitMLV1.mlpackage) |
| **메시지 필터링** | IdentityLookup Framework |
| **아키텍처** | MVVM |
| **테스트** | Swift Testing (@Test macro) |
| **프로젝트 관리** | Xcode 프로젝트 파일 |

---

## 프로젝트 구조

```
SpamKiller/
│
├── SpamKiller (메인 앱)
│   ├── Sources/
│   │   ├── App/
│   │   │   └── SpamKillerApp.swift (진입점)
│   │   ├── View/
│   │   │   ├── TabBar.swift (탭 네비게이션)
│   │   │   ├── MainView.swift (키워드 목록)
│   │   │   ├── SettingView.swift (설정)
│   │   │   └── HelpView.swift (도움말)
│   │   └── ViewModel/
│   │       └── ContentViewModel.swift (상태 관리)
│   │
│   ├── Resources/
│   │   ├── Assets.xcassets/
│   │   │   ├── AppIcon.appiconset/
│   │   │   ├── AccentColor.colorset/
│   │   │   └── Help/ (help1, help2, help3 이미지)
│   │   │
│   ├── Info.plist (앱 메타데이터)
│   └── SpamKiller.entitlements (기능 권한)
│
├── SpamKillerMessageFilter (메시지 필터 확장)
│   ├── MessageFilterExtension.swift (핵심 필터 로직)
│   ├── MessageFilterExtensionSave.swift (백업 파일)
│   ├── SpamKitMLV1.mlpackage/ (머신러닝 모델)
│   │   ├── Manifest.json
│   │   └── Data/
│   │       └── com.apple.CoreML/
│   │           ├── SpamKitMLV1.mlmodel
│   │           ├── Metadata.json
│   │           └── FeatureDescriptions.json
│   ├── Info.plist
│   └── SpamKillerMessageFilter.entitlements
│
├── Shared (공유 모듈)
│   ├── AppGroup.swift (상수)
│   └── SharedStore.swift (싱글톤 저장소)
│
├── spamkillerpyml (Python 기반 모델 실험 폴더)
│   ├── sample.csv
│   ├── requirements.txt
│   ├── v1_sparse_linear/
│   │   ├── train.py
│   │   ├── predict.py
│   │   └── artifacts/
│   ├── v2_embedding/
│       ├── train.py
│       ├── predict.py
│       └── artifacts/
│   └── v3_embedding_coreml/
│       ├── train.py
│       ├── predict.py
│       └── artifacts/
│
├── SpamKillerTests (테스트)
│   ├── KeywordTests.swift (키워드 필터링 테스트)
│   ├── MLTests.swift (머신러닝 테스트)
│   └── PolicyTests.swift (정책 필터링 테스트)
│
└── SpamKiller.xcodeproj/ (Xcode 프로젝트)
    ├── project.pbxproj
    └── xcshareddata/

```

---

## Python 모델 실험 사용법

`spamkillerpyml` 폴더에는 버전별 Python 실험 코드가 들어 있습니다.

- `v1_sparse_linear`: 가볍고 빠른 선형 기준선 모델. 학습 후 Core ML `.mlmodel` 생성 가능
- `v2_embedding`: 임베딩 기반 테스트 모델. 의미 기반 성능 비교용
- `v3_embedding_coreml`: 임베딩 기반이면서 실제 Core ML `.mlmodel` 생성 버전
- `v4_createml_textclassifier`: Apple Create ML 기반 문자열 입력 텍스트 분류기 버전

### 버전 비교표

| 버전 | 입력 형태 | 핵심 기법 | `.mlmodel` 생성 | 모바일 적용 난이도 | 상태 | 한줄 평가 |
|---|---|---|---|---|---|---|
| `v1_sparse_linear` | 토큰 카운트 딕셔너리 | 전통적 선형 분류기 | 가능 | 보통 | 동작 확인 완료 | 가볍고 단순한 기준선 |
| `v2_embedding` | 문자열 -> 임베딩 -> 분류 | 임베딩 + 로지스틱 회귀 | 불가 | 어려움 | 동작 확인 완료 | 성능 비교용 테스트 버전 |
| `v3_embedding_coreml` | 임베딩 벡터 | 임베딩 + 로지스틱 회귀 + Core ML export | 가능 | 보통~어려움 | 동작 확인 완료 | `.mlmodel`은 나오지만 문자열 직입력은 아님 |
| `v4_createml_textclassifier` | 문자열 | Apple Create ML 텍스트 분류기 | 가능 | 매우 쉬움 | 스캐폴드 완료, 이 환경에서 학습 검증 미완료 | 모바일에서 가장 쓰기 편한 방향 |

### 공통 준비

```bash
cd spamkillerpyml
/opt/homebrew/opt/python@3.13/bin/python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### v1_sparse_linear 사용법

```bash
cd spamkillerpyml
source .venv/bin/activate
python v1_sparse_linear/train.py
python v1_sparse_linear/predict.py "광고) 한도 상향 대출 가능 안내"
```

생성 파일:

- `spamkillerpyml/v1_sparse_linear/artifacts/model.json`
- `spamkillerpyml/v1_sparse_linear/artifacts/metrics.json`
- `spamkillerpyml/v1_sparse_linear/artifacts/SpamKillerPyTextClassifier.mlmodel`

### v2_embedding 사용법

```bash
cd spamkillerpyml
source .venv/bin/activate
python v2_embedding/train.py
python v2_embedding/predict.py "광고) 한도 상향 대출 가능 안내"
```

생성 파일:

- `spamkillerpyml/v2_embedding/artifacts/classifier.joblib`
- `spamkillerpyml/v2_embedding/artifacts/config.json`
- `spamkillerpyml/v2_embedding/artifacts/metrics.json`

### v3_embedding_coreml 사용법

```bash
cd spamkillerpyml
source .venv/bin/activate
python v3_embedding_coreml/train.py
python v3_embedding_coreml/predict.py "광고) 한도 상향 대출 가능 안내"
```

생성 파일:

- `spamkillerpyml/v3_embedding_coreml/artifacts/classifier.joblib`
- `spamkillerpyml/v3_embedding_coreml/artifacts/config.json`
- `spamkillerpyml/v3_embedding_coreml/artifacts/metrics.json`
- `spamkillerpyml/v3_embedding_coreml/artifacts/SpamKillerEmbeddingClassifier.mlmodel`

자세한 설명은 [`spamkillerpyml/README.md`](/Users/kimdonghyeon/2025/개발/앱출시/SpamKiller/SpamKiller/spamkillerpyml/README.md) 를 보면 됩니다.

---

## 핵심 모듈 설명

### 1. 메인 앱 (SpamKiller)

#### 1.1 **SpamKillerApp.swift** - 진입점
```swift
@main
struct SpamKillerApp: App {
    init() {
        // UINavigationBar 전역 스타일 설정
        let appearance = UINavigationBarAppearance()
        appearance.configureWithDefaultBackground()
        UINavigationBar.appearance().standardAppearance = appearance
    }
    
    var body: some Scene {
        WindowGroup {
            TabBarView()
        }
    }
}
```

**역할**: 앱 초기화 및 루트 뷰 설정

---

#### 1.2 **TabBarView.swift** - 탭 네비게이션

```swift
struct TabBarView: View {
    @State private var selectedTab: Int = 1
    @StateObject private var viewModel = ContentViewModel()
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // 탭 1: MainView (키워드)
            MainView()
                .tabItem {
                    Label("키워드", systemImage: "xmark.circle")
                }
                .tag(1)
            
            // 탭 2: SettingView (설정)
            SettingView()
                .tabItem {
                    Label("설정", systemImage: "gear")
                }
                .tag(2)
        }
        .environmentObject(viewModel)
    }
}
```

**기능**:
- 탭 1: 키워드 관리 (MainView)
- 탭 2: 앱 설정 (SettingView)
- ContentViewModel을 환경 객체로 주입

---

#### 1.3 **MainView.swift** - 키워드 목록 관리

```swift
struct MainView: View {
    @EnvironmentObject var viewModel: ContentViewModel
    
    var body: some View {
        NavigationStack {
            List {
                Section(header: Text("스팸 분류 단어 · 정크함으로 이동")) {
                    if viewModel.keywords.isEmpty {
                        Text("등록된 스팸 단어가 없습니다.")
                            .foregroundColor(.gray)
                    } else {
                        ForEach(viewModel.keywords, id: \.self) { keyword in
                            Text(keyword)
                        }
                        .onDelete(perform: { offsets in
                            viewModel.removeKeywords(at: offsets)
                        })
                    }
                }
            }
            .navigationTitle("스팸킬러")
            .toolbar {
                // 하단 추가 버튼
                ToolbarItem(placement: .bottomBar) {
                    Button(action: { viewModel.showAddAlert = true }) {
                        Image(systemName: "plus.circle.fill")
                            .font(.system(size: 30))
                    }
                }
                
                // 우측 도움말 버튼
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("도움말") {
                        viewModel.showHelpView = true
                    }
                }
            }
        }
        .alert("새 키워드 추가", isPresented: $viewModel.showAddAlert) {
            TextField("예: 대출, 광고", text: $viewModel.newKeyword)
            Button("추가") {
                viewModel.addKeyword()
            }
            Button("취소", role: .cancel) { }
        }
        .fullScreenCover(isPresented: $viewModel.showHelpView) {
            HelpView(isPresented: $viewModel.showHelpView)
        }
    }
}
```

**주요 기능**:
- ✅ 등록된 스팸 키워드 목록 표시
- ✅ 스와이프로 키워드 삭제
- ✅ "+" 버튼으로 새 키워드 추가 (Alert)
- ✅ "도움말" 버튼으로 사용 방법 안내 (HelpView)

---

#### 1.4 **SettingView.swift** - 설정

```swift
struct SettingView: View {
    @EnvironmentObject var viewModel: ContentViewModel
    
    var body: some View {
        NavigationStack {
            List {
                Section(header: Text("AI 설정")) {
                    Toggle("로컬 AI 모드(베타 버전)", 
                           isOn: $viewModel.isOnDeviceEnabled)
                    Text("학습된 로컬 AI가 스팸을 차단합니다.")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
                
                Section(header: Text("앱 정보")) {
                    HStack {
                        Text("버전")
                        Spacer()
                        Text("1.0.0")
                            .foregroundColor(.gray)
                    }
                }
            }
            .navigationTitle("설정")
        }
    }
}
```

**기능**:
- AI 모드 토글 (로컬 AI 활성화/비활성화)
- 앱 버전 정보 표시

---

#### 1.5 **HelpView.swift** - 사용 방법 안내

```swift
struct HelpView: View {
    @Binding var isPresented: Bool
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    Text("스팸킬러 사용법")
                        .font(.title2)
                        .fontWeight(.bold)
                    
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Image("help1")
                                .resizable()
                                .frame(width: 70, height: 70)
                            Text("1. 설정을 클릭합니다.")
                        }
                        
                        HStack {
                            Image("help2")
                                .resizable()
                                .frame(width: 300, height: 70)
                            Text("2. message를 검색합니다.")
                        }
                        
                        HStack {
                            Image("help3")
                                .resizable()
                                .frame(width: 300, height: 70)
                            Text("3. 알 수 없는 연락처 및 스팸을 클릭합니다.")
                        }
                    }
                    
                    Button(action: { isPresented = false }) {
                        Text("닫기")
                            .frame(maxWidth: .infinity)
                            .frame(height: 50)
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                }
                .padding()
            }
            .navigationTitle("도움말")
        }
    }
}
```

**기능**:
- iOS 설정에서 SpamKiller 활성화하는 방법을 3단계로 안내
- 이미지 + 텍스트로 시각적 보조

---

#### 1.6 **ContentViewModel.swift** - 상태 관리

```swift
@MainActor
final class ContentViewModel: ObservableObject {
    @Published var keywords: [String] = []
    @Published var newKeyword: String = ""
    @Published var showAddAlert: Bool = false
    @Published var showHelpView: Bool = false
    @Published var isOnDeviceEnabled: Bool = false
    
    private let store = SharedStore.shared
    
    init() {
        loadKeywords()
        loadOnDeviceEnabledState()
    }
    
    // MARK: - Keyword Management
    func loadKeywords() {
        keywords = store.loadSpamKeywords()
    }
    
    func addKeyword() {
        guard !newKeyword.trimmingCharacters(in: .whitespaces).isEmpty else { return }
        store.addSpamKeyword(keyword: newKeyword)
        newKeyword = ""
        loadKeywords()
    }
    
    func removeKeywords(at offsets: IndexSet) {
        store.removeSpamKeywords(at: offsets)
        loadKeywords()
    }
    
    // MARK: - AI Toggle Management
    func loadOnDeviceEnabledState() {
        isOnDeviceEnabled = store.isOnDeviceEnabled()
    }
    
    func setOnDeviceEnabled(_ enabled: Bool) {
        store.setOnDeviceEnabled(enabled)
        isOnDeviceEnabled = enabled
    }
}
```

**역할**:
- `@Published` 프로퍼티로 UI 자동 업데이트
- SharedStore를 통한 데이터 영속성
- 비즈니스 로직 분리

---

### 2. 메시지 필터 확장 (SpamKillerMessageFilter)

#### 2.1 **MessageFilterExtension.swift** - 핵심 필터 로직

메시지 필터 확장은 **3계층 필터링** 전략을 사용합니다:

##### **계층 1: 정책 기반 필터링 (Policy)**

```swift
func applyPolicy(message: String) -> (ILMessageFilterAction, ILMessageFilterSubAction)? {
    // 빈 메시지
    if message.trimmingCharacters(in: .whitespaces).isEmpty {
        return (.none, .none)
    }
    
    // 너무 짧은 메시지
    if message.count <= 1 {
        return (.none, .none)
    }
    
    // 숫자만 있음
    let digits = message.filter { $0.isNumber }
    if digits.count == message.count {
        return (.none, .none)
    }
    
    return nil  // 정책 통과
}
```

**목적**: 명백한 정상/비정상 메시지를 빠르게 사전 필터링

---

##### **계층 2: 키워드 기반 필터링 (Rule-based)**

```swift
func checkByKeyword(message: String, keywords: [String]) 
    -> (ILMessageFilterAction, ILMessageFilterSubAction) {
    
    for keyword in keywords {
        if message.localizedCaseInsensitiveContains(keyword) {
            return (.junk, .none)  // 즉시 스팸 확정
        }
    }
    
    return (.none, .none)  // 키워드 미매칭
}
```

**목적**: 사용자 정의 키워드로 고정적인 스팸 패턴 차단

---

##### **계층 3: 머신러닝 필터링 (ML-based)**

```swift
func checkByML(message: String) -> (ILMessageFilterAction, ILMessageFilterSubAction) {
    guard let model = mlModel else {
        return (.none, .none)
    }
    
    do {
        let output = try model.prediction(text: message)
        if output.label == "spam" {
            return (.junk, .none)
        } else {
            return (.none, .none)
        }
    } catch {
        return (.none, .none)  // 모델 오류 시 판단 보류
    }
}
```

**목적**: 학습된 모델로 알려지지 않은 스팸 패턴 감지

---

##### **통합 필터 흐름**

```swift
func offlineAction(for queryRequest: ILMessageQueryRequest) -> ILMessageFilterAction {
    guard let messageBody = queryRequest.messageBody else {
        return .none
    }
    
    // ===== Step 1: 정책 체크 =====
    if let policyResult = applyPolicy(message: messageBody) {
        return policyResult.0
    }
    
    // ===== Step 2: 키워드 체크 =====
    let keywords = SharedStore.shared.loadSpamKeywords()
    let keywordResult = checkByKeyword(message: messageBody, keywords: keywords)
    if keywordResult.0 == .junk {
        return .junk  // 스팸 확정, 즉시 반환
    }
    
    // ===== Step 3: ML 체크 (토글 ON일 경우만) =====
    if SharedStore.shared.isOnDeviceEnabled() {
        let mlResult = checkByML(message: messageBody)
        if mlResult.0 != .none {
            return mlResult.0
        }
    }
    
    // 모든 필터 통과
    return .none
}
```

**흐름도**:

```
메시지 수신
    ↓
┌───────────────────────┐
│ Step 1: 정책 체크      │
└───┬─────────────────┬──┘
    │(제외)           │(통과)
    ↓                │
  .none              │
    ↓                ↓
반환            ┌──────────────┐
             │ Step 2: 키워드 │
             └───┬─────────┬──┘
          (스팸) │        │(스팸아님)
              ↓         │
            .junk       │
              ↓         ↓
            반환   ┌──────────────┐
              │ AI 토글  │
              │ 활성화?  │
              └───┬──────┬──┘
             (YES)│      │(NO)
                 ↓      ↓
             ┌─────┐   .none
             │ ML  │   (반환)
             └─┬───┘
              ↓
           (결과 반환)
```

---

#### 2.2 **머신러닝 모델 (SpamKitMLV1.mlpackage)**

| 항목 | 값 |
|------|-----|
| **모델명** | SpamKitMLV1 |
| **입력** | `text` (String): 메시지 본문 |
| **출력** | `label` (String): "spam" 또는 "ham" |
| **실행환경** | 온디바이스 (프라이버시 보호) |
| **학습 데이터** | 스팸/정상 메시지 데이터셋 |

**Metadata 예시**:
```json
{
  "inputs": [
    {
      "name": "text",
      "type": "string"
    }
  ],
  "outputs": [
    {
      "name": "label",
      "type": "string"
    }
  ]
}
```

---

### 3. 공유 모듈 (Shared)

#### 3.1 **AppGroup.swift** - 상수 정의

```swift
enum AppGroup {
    /// App Group 식별자 (메인 앱과 Extension 모두 사용)
    static let id = "group.com.indextrown.SpamKiller"
    
    enum Key {
        /// 스팸 키워드 배열 저장 키
        static let spamKeywordKey = "spam_keywords"
        
        /// 온디바이스 AI 활성화 여부 저장 키
        static let onDeviceEnabledKey = "on_device_enabled"
    }
}
```

**역할**:
- App Group 식별자 중앙화
- UserDefaults 키 타이핑 오류 방지
- 상수 공유

---

#### 3.2 **SharedStore.swift** - 싱글톤 저장소

```swift
final class SharedStore {
    static let shared = SharedStore()
    
    private let defaults: UserDefaults
    
    private init() {
        guard let ud = UserDefaults(suiteName: AppGroup.id) else {
            fatalError("App Group not configured")
        }
        self.defaults = ud
    }
    
    // MARK: - Spam Keywords
    
    /// 저장된 모든 스팸 키워드 로드
    func loadSpamKeywords() -> [String] {
        defaults.stringArray(forKey: AppGroup.Key.spamKeywordKey) ?? []
    }
    
    /// 특정 키워드 추가 (중복 제외)
    func addSpamKeyword(keyword: String) {
        let trimmed = keyword.trimmingCharacters(in: .whitespaces)
        guard !trimmed.isEmpty else { return }
        
        var keywords = loadSpamKeywords()
        if !keywords.contains(trimmed) {
            keywords.append(trimmed)
            defaults.set(keywords, forKey: AppGroup.Key.spamKeywordKey)
        }
    }
    
    /// 지정된 인덱스의 키워드 삭제
    func removeSpamKeywords(at offsets: IndexSet) {
        var keywords = loadSpamKeywords()
        keywords.remove(atOffsets: offsets)
        defaults.set(keywords, forKey: AppGroup.Key.spamKeywordKey)
    }
    
    // MARK: - AI Settings
    
    /// 온디바이스 AI 활성화 여부 조회
    func isOnDeviceEnabled() -> Bool {
        defaults.bool(forKey: AppGroup.Key.onDeviceEnabledKey)
    }
    
    /// 온디바이스 AI 활성화 상태 설정
    func setOnDeviceEnabled(_ enabled: Bool) {
        defaults.set(enabled, forKey: AppGroup.Key.onDeviceEnabledKey)
    }
}
```

**특징**:
- 싱글톤 패턴으로 앱 전체에서 동일한 인스턴스 사용
- App Group UserDefaults로 메인 앱과 Extension 간 데이터 공유
- 타입 안전한 API 제공

---

### 4. 테스트 스위트 (SpamKillerTests)

#### 4.1 **KeywordTests.swift** - 키워드 필터링 테스트

```swift
struct KeywordTests {
    let ext = MessageFilterExtension()
    
    @Test("스팸 키워드가 포함된 메시지는 .junk로 분류")
    func spam_message_returns_junk() {
        let message = "무료 대출 즉시 가능"
        let keywords = ["대출", "무료"]
        
        let result = ext.checkByKeyword(message: message, keywords: keywords)
        
        #expect(result.0 == .junk)
    }
    
    @Test("스팸 키워드가 없는 일반 메시지는 .allow로 분류")
    func normal_message_returns_allow() {
        let message = "내일 회의하자"
        let keywords = ["대출", "무료"]
        
        let result = ext.checkByKeyword(message: message, keywords: keywords)
        
        #expect(result.0 == .none)
    }
    
    @Test("스팸 키워드 목록이 비어있으면 메시지는 항상 .allow로 분류")
    func empty_keywords_returns_allow() {
        let message = "아무거나"
        let keywords: [String] = []
        
        let result = ext.checkByKeyword(message: message, keywords: keywords)
        
        #expect(result.0 == .none)
    }
}
```

**커버리지**:
- ✅ 키워드 매칭 성공
- ✅ 키워드 미매칭
- ✅ 공백 키워드 목록

---

#### 4.2 **MLTests.swift** - 머신러닝 테스트

```swift
struct MLTests {
    let ext = MessageFilterExtension()
    
    @Test("ML이 spam으로 분류한 메시지는 .junk를 반환")
    func ml_spam_message_returns_junk() {
        let spamMessage = "무료 대출 지금 가능"
        
        let result = ext.checkByML(message: spamMessage)
        
        #expect(result.0 == .junk)
    }
    
    @Test("ML이 ham으로 분류한 메시지는 .none을 반환")
    func ml_normal_message_returns_none() {
        let normalMessage = "내일 점심 시간 괜찮아?"
        
        let result = ext.checkByML(message: normalMessage)
        
        #expect(result.0 == .none)
    }
    
    @Test("같은 입력에 대해 ML 결과는 일관된다")
    func ml_same_input_returns_same_result() {
        let message = "테스트 메시지"
        
        let result1 = ext.checkByML(message: message)
        let result2 = ext.checkByML(message: message)
        
        #expect(result1.0 == result2.0)
    }
    
    @Test("ML은 여러 스팸 메시지를 junk로 분류")
    func ml_multiple_spam_messages_return_junk() {
        let spamMessages = [
            "무료 대출 지금 가능",
            "상품권 구매 기회",
            "클릭해서 상품받기"
        ]
        
        for message in spamMessages {
            let result = ext.checkByML(message: message)
            #expect(result.0 == .junk, "'\(message)' should be junk")
        }
    }
}
```

**커버리지**:
- ✅ 스팸 분류 정확도
- ✅ 정상 메시지 판정
- ✅ 일관성 검증
- ✅ 배치 테스트

---

#### 4.3 **PolicyTests.swift** - 정책 필터링 테스트

```swift
struct PolicyTests {
    let ext = MessageFilterExtension()
    
    @Test("빈 문자열은 정책에 의해 .none을 반환")
    func empty_message_policy() {
        let result = ext.applyPolicy(message: "")
        
        #expect(result?.0 == .none)
    }
    
    @Test("숫자만 있는 메시지는 정책에 의해 .none을 반환")
    func numbers_only_policy() {
        let result = ext.applyPolicy(message: "01012345678")
        
        #expect(result?.0 == .none)
    }
    
    @Test("아주 짧은 메시지는 정책에 의해 .none을 반환")
    func short_message_policy() {
        let result = ext.applyPolicy(message: "a")
        
        #expect(result?.0 == .none)
    }
    
    @Test("정상 메시지는 정책에 걸리지 않는다")
    func normal_message_passes_policy() {
        let result = ext.applyPolicy(message: "안녕하세요 반갑습니다")
        
        #expect(result == nil)
    }
}
```

**커버리지**:
- ✅ 엣지 케이스 처리
- ✅ 정상 메시지 통과

---

### 설정 및 실행

#### 필수 요구사항
- **Xcode**: 14.0 이상
- **macOS**: 12.0 이상
- **Swift**: 5.9 이상
- **iOS 대상**: 15.0 이상

#### 단계별 설정

**1. 프로젝트 열기**
```bash
cd /Users/kimdonghyeon/2025/개발/앱출시/SpamKiller/SpamKiller
open SpamKiller.xcodeproj
```

**2. 빌드 설정 확인**
- **Team ID** 설정 (Signing & Capabilities)
- **Bundle Identifier** 확인: `com.indextrown.SpamKiller`
- **App Group Entitlements** 활성화: `group.com.indextrown.SpamKiller`

**3. 빌드 진행**
```bash
xcodebuild -scheme SpamKiller -configuration Debug
```

**4. 시뮬레이터/기기에서 실행**
- Xcode에서 Run (⌘R) 또는
- Command Line:
```bash
xcodebuild -scheme SpamKiller -configuration Debug -destination 'platform=iOS Simulator,name=iPhone 15'
```

---

## 사용 방법

### 메인 앱 사용 방법

#### 1️⃣ **키워드 등록**

1. SpamKiller 앱 실행
2. "키워드" 탭 선택
3. **"+" 버튼** 클릭
4. 스팸 키워드 입력 (예: "대출", "광고", "추첨")
5. **"추가"** 버튼 클릭

#### 2️⃣ **키워드 삭제**

1. 삭제할 키워드를 **왼쪽으로 스와이프**
2. **"삭제"** 버튼 클릭

#### 3️⃣ **AI 모드 활성화**

1. "설정" 탭 선택
2. **"로컬 AI 모드(베타 버전)"** 토글 ON
3. 키워드와 함께 머신러닝으로 스팸 판정

---

### iOS 설정에서 SpamKiller 활성화

SpamKiller가 실제로 메시지를 필터링하려면 **메시지 앱 설정**에서 활성화해야 합니다:

1. **iOS 설정 앱** 실행
2. **메시지** → **알 수 없는 발신자 및 스팸** 선택
3. **SpamKiller** 토글 **ON**

이후 수신되는 메시지가 자동으로 필터링됩니다.

---

## 개발 가이드

### 로컬 개발 페이지

#### 키워드 추가 기능 확장

새로운 필터링 규칙을 추가하려면:

1. `SharedStore.swift`에 새 설정 추가:
```swift
enum Key {
    static let newFeatureKey = "new_feature"
}

func isNewFeatureEnabled() -> Bool {
    defaults.bool(forKey: AppGroup.Key.newFeatureKey)
}
```

2. `SettingView.swift`에 토글 추가:
```swift
Toggle("새 기능", isOn: $viewModel.isNewFeatureEnabled)
```

3. `ContentViewModel.swift`에 바인딩 추가:
```swift
@Published var isNewFeatureEnabled: Bool = false

func loadNewFeatureState() {
    isNewFeatureEnabled = store.isNewFeatureEnabled()
}
```

4. `MessageFilterExtension.swift`에서 필터링 로직 구현

---

#### 머신러닝 모델 개발 및 강화 가이드

##### **Step 1: 학습 데이터 준비**

스팸 판정 모델을 만들기 위해 다음과 같은 CSV 형식의 데이터를 준비합니다:

**파일명**: `spam_data.csv`
```csv
text,label
무료 대출 지금 가능,spam
상품권 구매 기회,spam
클릭해서 상품받기,spam
내일 점심 시간 어때,ham
회의 일정 변경입니다,ham
반갑습니다,ham
```

**데이터 구성**:
- `text`: 메시지 본문 (한국어)
- `label`: 분류 결과 ("spam" 또는 "ham")
- **최소 권장**: 스팸 500개 + 정상 500개
- **이상적**: 각 카테고리 1,000개 이상

---

##### **Step 2: Python에서 모델 학습 (scikit-learn 방식)**

**요구사항**:
```bash
pip install scikit-learn coremltools numpy pandas
```

**학습 스크립트** (`train_spam_model.py`):

```python
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import coremltools as ct

# 1. 데이터 로드
df = pd.read_csv('spam_data.csv')
X = df['text']
y = df['label']

# 2. 모델 파이프라인 구성
# (TF-IDF 벡터화 + Naive Bayes)
model = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
    ('classifier', MultinomialNB())
])

# 3. 모델 학습
model.fit(X, y)

# 4. scikit-learn 모델을 Core ML로 변환
ml_model = ct.converters.sklearn.convert(
    model,
    input_features='text'
)

# 5. 메타데이터 설정
ml_model.short_description = "Spam Classification Model"
ml_model.output_names = ['label']

# 6. 모델 저장
ml_model.save('SpamKitMLV1.mlmodel')

print("✅ 모델 생성 완료: SpamKitMLV1.mlmodel")
```

**실행**:
```bash
python train_spam_model.py
```

**출력**: `SpamKitMLV1.mlmodel` 생성

---

##### **Step 3: Create ML을 사용한 고급 학습 (GUI 방식)**

**방법 1: Xcode Create ML 활용 (쉬운 방식)**

1. Xcode 실행
2. **Window** → **Developer Tools** → **Create ML** 선택
3. **새 프로젝트** 생성
4. **Text Classification** 선택
5. **Training Data** → `spam_data.csv` 파일 선택
6. **모델 학습** 시작
7. **Accuracy** 확인 후 저장

**Method 2: 터미널에서 Create ML 사용**

```bash
# Create ML Command Line 도구 사용
python -m coremltools.models.create_ml create \
    --method classifier \
    --input-features text \
    --output-features label \
    --training-data spam_data.csv \
    --output-path SpamKitMLV1_v2.mlmodel
```

---

##### **Step 4: 모델 강화 및 성능 개선**

**방식 1: 모델 구조 개선**

더 정교한 분류를 위해 **Neural Network** 사용:

```python
# 고급 모델: Neural Network
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

model = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=2000, ngram_range=(1, 3))),
    ('scaler', StandardScaler(with_mean=False)),
    ('classifier', MLPClassifier(
        hidden_layer_sizes=(128, 64),
        max_iter=200,
        random_state=42,
        learning_rate_init=0.001
    ))
])

model.fit(X, y)

# Core ML로 변환
ml_model = ct.converters.sklearn.convert(model, input_features='text')
ml_model.save('SpamKitMLV1_v2.mlmodel')
```

**방식 2: 데이터 증강 (Data Augmentation)**

학습 데이터를 더 다양하게 생성:

```python
import random

def augment_text(text):
    """맞춤법, 띄어쓰기 변형을 통해 데이터 증강"""
    variations = [text]
    
    # 공백 추가/제거
    variations.append(text.replace(' ', ''))
    variations.append(' '.join(list(text)))
    
    # 단어 순서 뒤바꾸기
    words = text.split()
    if len(words) > 1:
        random.shuffle(words)
        variations.append(' '.join(words))
    
    return variations

# 원본 데이터에 증강 데이터 추가
augmented_data = []
for idx, row in df.iterrows():
    augmented_data.append(row)
    for aug_text in augment_text(row['text']):
        augmented_data.append({'text': aug_text, 'label': row['label']})

df_augmented = pd.DataFrame(augmented_data)
print(f"원본 데이터: {len(df)}, 증강 후: {len(df_augmented)}")
```

**방식 3: Transfer Learning**

기존의 사전 학습된 모델을 Fine-tuning:

```python
# Transformers 라이브러리 사용 (한국어 BERT)
from transformers import BertTokenizer, BertForSequenceClassification
import torch

# 한국어 학습된 BERT 모델 로드
model_name = "monologg/kobert"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)

# 학습 데이터로 Fine-tuning
# (학습 코드 생략 - 복잡함)

# ONNX → Core ML 변환
import coremltools as ct
ml_model = ct.convert(model, inputs=[...], outputs=[...])
ml_model.save('SpamKitMLV1_bert.mlmodel')
```

---

##### **Step 5: 모델 성능 평가**

```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# 테스트 세트로 평가
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

print(f"📊 모델 성능")
print(f"정확도 (Accuracy): {accuracy:.2%}")
print(f"정밀도 (Precision): {precision:.2%}")
print(f"재현율 (Recall): {recall:.2%}")
print(f"F1 스코어: {f1:.2%}")

# 목표: 정확도 90% 이상
if accuracy >= 0.90:
    print("✅ 배포 가능")
else:
    print("⚠️  모델 개선 필요")
```

**성능 목표**:
- Accuracy ≥ 90%
- Precision ≥ 88%
- Recall ≥ 85%

---

##### **Step 6: 프로젝트에 통합하기**

**프로젝트 구조**:
```
SpamKiller/
└── SpamKillerMessageFilter/
    ├── SpamKitMLV1.mlpackage/          ← 모델 디렉토리
    │   ├── Manifest.json               ← 메타데이터
    │   └── Data/
    │       └── com.apple.CoreML/
    │           ├── SpamKitMLV1.mlmodel ← 실제 모델
    │           ├── Metadata.json
    │           └── FeatureDescriptions.json
    ├── MessageFilterExtension.swift
    └── Info.plist
```

**Step 6.1: .mlmodel을 .mlpackage로 변환**

```bash
# .mlmodel 파일을 .mlpackage로 구성
mkdir -p SpamKitMLV1.mlpackage/Data/com.apple.CoreML

# 모델 파일 복사
cp SpamKitMLV1.mlmodel SpamKitMLV1.mlpackage/Data/com.apple.CoreML/

# Manifest.json 생성
cat > SpamKitMLV1.mlpackage/Manifest.json << 'EOF'
{
  "identifierPrefix": "com.apple.CoreML",
  "version": "1.0.0",
  "mkl": false,
  "hasProtos": false,
  "functions": [],
  "models": [
    {
      "specificationVersion": 7,
      "modelPackageVersion": 1
    }
  ]
}
EOF
```

**Step 6.2: Xcode에 추가**

1. Xcode 실행: `open SpamKiller.xcodeproj`
2. **SpamKillerMessageFilter** 타겟 선택
3. **Build Phases** → **Copy Bundle Resources** 확인
4. **+ 버튼** → `SpamKitMLV1.mlpackage` 폴더 추가

**Step 6.3: MessageFilterExtension.swift에서 사용**

```swift
import CoreML
import IdentityLookup

class MessageFilterExtension: ILMessageFilterExtensionHostProvider {
    private lazy var mlModel: SpamKitMLV1? = {
        try? SpamKitMLV1(configuration: MLModelConfiguration())
    }()
    
    func handleQueryRequest(
        _ queryRequest: ILMessageQueryRequest,
        context: ILMessageFilterExtensionContext,
        completion: @escaping (ILMessageFilterQueryResponse) -> Void
    ) {
        let response = ILMessageFilterQueryResponse()
        
        guard let messageBody = queryRequest.messageBody else {
            completion(response)
            return
        }
        
        // ML 모델로 예측
        if let model = mlModel {
            do {
                let output = try model.prediction(text: messageBody)
                response.action = output.label == "spam" ? .junk : .none
            } catch {
                response.action = .none
            }
        }
        
        completion(response)
    }
}
```

---

##### **Step 7: 모델 버전 관리 및 배포**

**버전 관리 전략**:

| 파일명 | 버전 | 설명 | 상태 |
|--------|------|------|------|
| `SpamKitMLV1.mlpackage` | 1.0 | 초기 Naive Bayes 모델 | 프로덕션 |
| `SpamKitMLV2.mlpackage` | 2.0 | 신경망 기반 모델 | 테스트 중 |
| `SpamKitMLV3_BERT.mlpackage` | 3.0 | 한국어 BERT 모델 | 개발 중 |

**모델 교체 프로세스**:

```bash
# 1. 기존 모델 백업
mv SpamKillerMessageFilter/SpamKitMLV1.mlpackage \
   SpamKillerMessageFilter/SpamKitMLV1_backup.mlpackage

# 2. 새 모델 적용
mv SpamKitMLV2.mlpackage \
   SpamKillerMessageFilter/SpamKitMLV1.mlpackage

# 3. Xcode에서 빌드 및 테스트
xcodebuild test -scheme SpamKillerTests

# 4. 문제 없으면 커밋
git add SpamKillerMessageFilter/SpamKitMLV1.mlpackage
git commit -m "feat: Update ML model to V2 (CNN-based, 92% accuracy)"

# 5. 실패하면 롤백
mv SpamKillerMessageFilter/SpamKitMLV1.mlpackage \
   SpamKillerMessageFilter/SpamKitMLV2_failed.mlpackage
mv SpamKillerMessageFilter/SpamKitMLV1_backup.mlpackage \
   SpamKillerMessageFilter/SpamKitMLV1.mlpackage
```

---

##### **Step 8: 모델 모니터링 및 재학습**

프로덕션 배포 후 모델 성능 모니터링:

```python
# 실제 사용 데이터 수집
# (UserDefaults에서 사용자 피드백 수집)

def monitor_model_accuracy(recent_messages, recent_labels):
    """최근 메시지로 모델 성능 평가"""
    predictions = model.predict(recent_messages)
    accuracy = sum(predictions == recent_labels) / len(recent_labels)
    
    # 성능이 85% 이하로 떨어지면 재학습 권장
    if accuracy < 0.85:
        print(f"⚠️  모델 성능 저하: {accuracy:.2%}")
        print("재학습이 필요합니다")
        return False
    
    return True

# 월 1회 또는 분기 1회 재학습
def retrain_model():
    """새로운 데이터로 모델 재학습"""
    # 1. 최근 3개월 데이터 수집
    recent_data = load_recent_feedback_data()
    
    # 2. 기존 학습 데이터와 병합
    combined_data = pd.concat([original_data, recent_data])
    
    # 3. 모델 재학습
    new_model = train_model(combined_data)
    
    # 4. 성능 검증
    if evaluate_model(new_model) > current_model_accuracy + 0.02:
        # 5. 새 모델 배포
        deploy_model(new_model)
        print("✅ 모델 업데이트 완료")
    else:
        print("⚠️  기존 모델이 더 좋으므로 유지")
```

---

#### 파일 위치 및 네이밍 컨벤션 정리

**프로젝트 내 위치**:
```
/Users/kimdonghyeon/2025/개발/앱출시/SpamKiller/SpamKiller/
    ↓
    SpamKillerMessageFilter/  ← Extension 타겟
        ↓
        SpamKitMLV1.mlpackage/  ← 모델 디렉토리 (중요!)
            ├── Manifest.json
            └── Data/
                └── com.apple.CoreML/
                    ├── SpamKitMLV1.mlmodel
                    ├── Metadata.json
                    └── FeatureDescriptions.json
```

**네이밍 컨벤션**:
- **모델명**: `SpamKitMLV{버전}`
- **형식**: `.mlpackage` (배포용) 또는 `.mlmodel` (개발 중)
- **버전**: V1 (기본), V2 (개선), V3 (major update)
- **예시**:
  - ✅ `SpamKitMLV1.mlpackage` (프로덕션)
  - ✅ `SpamKitMLV2_beta.mlpackage` (테스트)
  - ❌ `model.mlmodel` (비추천)
  - ❌ `spam_classifier_final_v3.mlpackage` (너무 김)

**Swift 코드에서 참조**:
```swift
// MessageFilterExtension.swift 내부
let model = try? SpamKitMLV1(configuration: MLModelConfiguration())
//                              ↑ 모델명과 일치해야 함
```

---

### 머신러닝 모델 업데이트 체크리스트

새로운 모델을 배포하기 전 확인사항:

- [ ] 모델 정확도 ≥ 90%
- [ ] 정밀도 ≥ 88%, 재현율 ≥ 85%
- [ ] 테스트 케이스 모두 통과 (`xcodebuild test`)
- [ ] 시뮬레이터에서 메시지 필터링 정상 작동
- [ ] 모델 파일이 `.mlpackage` 형식인지 확인
- [ ] `Manifest.json` 메타데이터 확인
- [ ] Xcode에서 타겟 빌드 설정 확인
- [ ] 기존 모델 백업 완료
- [ ] Git에 커밋 메세지 작성
- [ ] App Store 배포 준비

---

#### 테스트 작성 가이드

새 기능에 대한 테스트를 작성하려면:

```swift
struct NewFeatureTests {
    @Test("새 필터링 규칙이 올바르게 작동")
    func new_filtering_rule() {
        let ext = MessageFilterExtension()
        let result = ext.newFilteringLogic(message: "테스트")
        
        #expect(result == .expected_value)
    }
}
```

테스트 실행:
```bash
xcodebuild test -scheme SpamKillerTests
```

---

### 주요 파일 간 의존 관계

```
SpamKillerApp.swift (진입점)
    ↓
TabBarView.swift
    ├─→ MainView.swift
    │    ↓
    │    ContentViewModel.swift
    │    ↓
    │    SharedStore.swift ←────┐
    │                           │
    └─→ SettingView.swift       │
         ↓                       │
    ContentViewModel.swift ──────┘

MessageFilterExtension.swift
    ↓
SharedStore.swift
    ├─→ AppGroup.swift
    └─→ SpamKitMLV1.mlpackage
```

---

## 문제 해결

### 1. App Group이 제대로 구성되지 않았을 때

**증상**: Extension이 메인 앱의 키워드를 읽지 못함

**해결 방법**:
1. Xcode에서 **모든 타겟** 선택
2. **Signing & Capabilities** 탭 이동
3. **+ Capability** 클릭
4. **App Groups** 검색 및 추가
5. 모든 타겟에서 동일한 App Group ID 설정:
   ```
   group.com.indextrown.SpamKiller
   ```

---

### 2. 메시지가 필터링되지 않을 때

**점검사항**:
- [ ] iOS 설정 → 메시지 → 알 수 없는 발신자 및 스팸에서 SpamKiller 활성화 확인
- [ ] 키워드가 올바르게 추가되었는지 확인
- [ ] Core ML 모델이 Extension 타겟에 포함되었는지 확인

---

### 3. Universal Clipboard/iCloud Keychain 오류

**해결 방법**:
1. Xcode 설정 → Capabilities
2. iCloud 관련 기능 제거 (필요 없으면)

---

## 라이선스 및 기여

본 프로젝트는 개인 프로젝트입니다.

---

## 주요 참고 자료

### iOS 개발
- [Apple IdentityLookup Framework](https://developer.apple.com/documentation/identitylookup)
- [Core ML Documentation](https://developer.apple.com/machine-learning/core-ml/)
- [SwiftUI Documentation](https://developer.apple.com/xcode/swiftui/)
- [App Groups Entitlements](https://developer.apple.com/documentation/bundleresources/entitlements/com_apple_security_application-groups)

### 머신러닝 & 모델 개발
- [Core ML Tools (Python)](https://github.com/apple/coremltools)
- [Create ML (Xcode)](https://developer.apple.com/machine-learning/create-ml/)
- [scikit-learn Documentation](https://scikit-learn.org/)
- [Transformers - Hugging Face](https://huggingface.co/)
- [한국어 BERT (KoBERT)](https://github.com/SKTBrain/KoBERT)
- [TensorFlow to Core ML 변환](https://github.com/apple/coremltools)

### 데이터 처리
- [Pandas Documentation](https://pandas.pydata.org/)
- [NumPy Documentation](https://numpy.org/)
- [TF-IDF (scikit-learn)](https://scikit-learn.org/stable/modules/feature_extraction.html#tfidf-term-weighting)

---

## 🚀 CoreML 모델 파일 위치 & 네이밍 - 빠른 참조

### 📁 파일 위치 (절대 경로)

```
/Users/kimdonghyeon/2025/개발/앱출시/SpamKiller/SpamKiller/
└── SpamKillerMessageFilter/
    └── SpamKitMLV1.mlpackage/          ← 핵심: 여기에 모델 치사기!
        ├── Manifest.json
        └── Data/
            └── com.apple.CoreML/
                ├── SpamKitMLV1.mlmodel  ← 실제 AI 모델 파일
                ├── Metadata.json
                └── FeatureDescriptions.json
```

### 🔤 파일명 규칙

| 구성 요소 | 예시 | 설명 |
|----------|------|------|
| 기본명 | `SpamKit` | 프로젝트명 축약 |
| 모델타입 | `ML` | Machine Learning |
| 버전 | `V1`, `V2`, `V3` | 버전 번호 (필수!) |
| 확장자 | `.mlpackage` | iOS 배포용 (배포 시 사용) |

**올바른 이름**:
- ✅ `SpamKitMLV1.mlpackage` (프로덕션 사용 중)
- ✅ `SpamKitMLV2_neural.mlpackage` (테스트 버전)
- ✅ `SpamKitMLV3_bert.mlpackage` (새 버전 준비)

**잘못된 이름**:
- ❌ `model.mlpackage` (너무 일반적)
- ❌ `spam_classifier_final_v1_real_final.mlpackage` (너무 김)
- ❌ `SpamKitML.mlmodel` (확장자 틀림, .mlpackage 사용)

### 🔗 Swift 코드에서 참조

**파일명과 코드에서의 클래스명이 자동으로 일치해야 함**:

```swift
// SpamKillerMessageFilter/MessageFilterExtension.swift
import CoreML

class MessageFilterExtension {
    private lazy var mlModel: SpamKitMLV1? = {
        try? SpamKitMLV1(configuration: MLModelConfiguration())
        //    ↑ 파일명 'SpamKitMLV1.mlpackage'와 자동 매핑
    }()
}
```

### 🔄 모델 버전 업그레이드 프로세스

```bash
# 현재 상태
ls SpamKillerMessageFilter/
SpamKitMLV1.mlpackage  ← 프로덕션 사용 중

# 1단계: 새 모델 준비
python train_spam_model.py  # SpamKitMLV2.mlmodel 생성

# 2단계: .mlpackage 구조로 변환
# (Python 또는 Xcode Create ML에서 수행)

# 3단계: 기존 모델 백업
mv SpamKillerMessageFilter/SpamKitMLV1.mlpackage \
   SpamKillerMessageFilter/SpamKitMLV1_backup.mlpackage

# 4단계: 새 모델 적용
mv SpamKitMLV2.mlpackage \
   SpamKillerMessageFilter/SpamKitMLV1.mlpackage

# 5단계: 테스트
xcodebuild test -scheme SpamKillerTests

# 6단계 (성공 시): 커밋
git commit -m "feat: Update ML model V2 (92% accuracy)"

# 6단계 (실패 시): 롤백
rm -rf SpamKillerMessageFilter/SpamKitMLV1.mlpackage
mv SpamKillerMessageFilter/SpamKitMLV1_backup.mlpackage \
   SpamKillerMessageFilter/SpamKitMLV1.mlpackage
```

### 💾 학습 데이터 & 스크립트 저장 위치 (프로젝트 외부)

```bash
~/Desktop/SpamKiller_ML/  (또는 편한 곳)
├── spam_data.csv               ← 학습 데이터
├── train_spam_model.py         ← Python 학습 스크립트
├── evaluate_model.py           ← 성능 평가 스크립트
├── data_augmentation.py        ← 데이터 증강
└── models/
    ├── SpamKitMLV1.mlmodel     ← 생성된 모델 (v1)
    ├── SpamKitMLV2.mlmodel     ← 생성된 모델 (v2)
    └── SpamKitMLV2.mlpackage   ← .mlpackage로 변환 후
```

### 🎯 체크리스트: 모델 배포 전

```bash
# 1. 모델 파일 확인
ls -la SpamKillerMessageFilter/SpamKitMLV1.mlpackage
# 출력 예: SpamKitMLV1.mlpackage/ (디렉토리)

# 2. 내부 구조 확인
find SpamKillerMessageFilter/SpamKitMLV1.mlpackage -type f
# 출력에 .mlmodel 포함 확인

# 3. Xcode 빌드 확인
xcodebuild build -scheme SpamKillerMessageFilter
# 에러 없는지 확인

# 4. 테스트 실행
xcodebuild test -scheme SpamKillerTests
# 모든 테스트 PASS

# 5. Git 상태 확인
git status
# 'modified: SpamKillerMessageFilter/SpamKitMLV1.mlpackage' 표시됨

# 6. 커밋 & 푸시
git add SpamKillerMessageFilter/SpamKitMLV1.mlpackage
git commit -m "feat: Update spam detection model"
git push origin main
```

---

**마지막 업데이트**: 2026년 4월 4일  
**개발자**: Index Crown  
**앱 버전**: 1.0.0  
**문서 버전**: 2.0 (CoreML 모델 개발 가이드 추가)

---
