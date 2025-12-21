//
//  SpamKillerTests.swift
//  SpamKillerTests
//
//  Created by 김동현 on 12/22/25.
//

import Testing
import SpamKillerMessageFilter
// API가 internal이 아니라 public 범위라 @testable 필요 없다이

struct MessageFilterTests {

    let ext = MessageFilterExtension()

    @Test("스팸 키워드가 포함된 메시지는 .junk로 분류된다")
    func spam_message_returns_junk() {
        let result = ext.classifyMessage(
            message: "무료 대출 안내드립니다",
            keywords: ["대출", "광고"]
        )
        #expect(result == .junk)
    }

    @Test("스팸 키워드가 없는 일반 메시지는 .allow로 분류된다")
    func normal_message_returns_allow() {
        let result = ext.classifyMessage(
            message: "오늘 저녁에 보자",
            keywords: ["대출", "광고"]
        )
        #expect(result == .allow)
    }

    @Test("스팸 키워드 목록이 비어 있으면 메시지는 항상 .allow로 분류된다")
    func empty_keywords_returns_allow() {
        let result = ext.classifyMessage(
            message: "무료 대출 안내",
            keywords: []
        )
        #expect(result == .allow)
    }
}
