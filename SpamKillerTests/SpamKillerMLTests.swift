//
//  SpamKillerMLTests.swift
//  SpamKillerTests
//
//  Created by 김동현 on 12/22/25.
//

import Testing
import SpamKillerMessageFilter

struct SpamKillerMLTests {
    let ext = MessageFilterExtension()
    
    @Test("ML이 spam으로 분류한 메시지는 .junk를 반환한다")
    func ml_spam_message_returns_junk() {
        let result = ext.checkByML(message: "무료 대출 지금 가능")

        #expect(result.0 == .junk)
        #expect(result.1 == .none)
    }

    @Test("ML이 ham으로 분류한 메시지는 .none을 반환한다")
    func ml_normal_message_returns_none() {
        let result = ext.checkByML(message: "오늘 저녁 뭐 먹을까")

        #expect(result.0 == .none)
        #expect(result.1 == .none)
    }
}
