//
//  SharedStore.swift
//  SpamKiller
//
//  Created by 김동현 on 12/25/25.
//
//  App Group(UserDefaults)를 통한
//  메인 앱 ↔ 메시지 필터 Extension 간
//  공용 데이터 접근을 담당하는 단일 저장소
//

import SwiftUI

/// App Group 기반의 공용 저장소
/// - 역할:
///   - UserDefaults(App Group)에 대한 접근을 중앙화
///   - 메인 앱과 Message Filter Extension에서
///     동일한 API로 데이터를 읽고/쓰기 위함
/// - 설계 이유:
///   - 키 문자열 중복 방지
///   - 접근 로직 일관성 유지
///   - Extension / App 간 동작 차이 제거
final class SharedStore {
    /// 각 타깃마다 하나씩 존재하는 싱글톤이며, 저장소만 공유한다
    /// 실제로 공유되는 것은 App Group UserDefaults 데이터이다
    static let shared = SharedStore()
    
    /// 외부에서 인스턴스 생성을 막기 위한 private initializer
    /// - App Group이 설정되지 않은 경우는
    ///   앱 설정 자체가 잘못된 상태이므로 즉시 실패 처리
    private init() {
        guard let ud = UserDefaults(suiteName: AppGroup.id) else {
            fatalError("App Group not configured")
        }
        self.defaults = ud
    }
    
    // App Group UserDefaults
    private let defaults: UserDefaults
}

// MARK: - Spam Keywords
extension SharedStore {
    /// App Group에 저장된 스팸 키워드 목록을 읽어온다
    /// - 사용처:
    ///   - 메인 앱: 키워드 목록 UI 표시
    ///   - Extension: 메시지 스팸 판단 로직
    func loadSpamKeywords() -> [String] {
        defaults.stringArray(forKey: AppGroup.Key.spamKeywordKey) ?? []
    }
    
    /// 새로운 스팸 키워드를 추가한다
    /// - 정책:
    ///   - 공백만 있는 값은 무시
    ///   - 중복 키워드는 저장하지 않음
    func addSpamKeyword(keyword: String) {
        let trimmed = keyword.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }

        var list = loadSpamKeywords()
        guard !list.contains(trimmed) else { return }

        list.append(trimmed)
        defaults.set(list, forKey: AppGroup.Key.spamKeywordKey)
    }
    
    /// 선택된 인덱스의 스팸 키워드를 삭제한다
    func removeSpamKeywords(at offsets: IndexSet) {
        var list = loadSpamKeywords()
        list.remove(atOffsets: offsets)
        defaults.set(list, forKey: AppGroup.Key.spamKeywordKey)
    }
}

// MARK: - AI On-Device Toggle
extension SharedStore {
    /// 온디바이스(Core ML) 스팸 판별 기능 사용 여부
    /// - 값이 없을 경우 기본값은 false
    func isOnDeviceEnabled() -> Bool {
        defaults.bool(forKey: AppGroup.Key.onDeviceEnavledKey)
    }
    
    /// 온디바이스 AI 사용 여부를 저장한다
    /// - 메인 앱 설정 화면에서 토글로 제어
    /// - Extension은 이 값을 읽어 판단 로직 분기
    func setOnDeviceEnabled(_ enabled: Bool) {
        defaults.set(enabled, forKey: AppGroup.Key.onDeviceEnavledKey)
    }
}
