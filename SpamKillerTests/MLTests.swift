//
//  SpamKillerMLTests.swift
//  SpamKillerTests
//u
//  Created by 김동현 on 12/22/25.
//

import Testing
import SpamKillerMessageFilter
import IdentityLookup

struct MLTests {
    let ext = MessageFilterExtension()
    
    @Test("ML 결과는 항상 유효한 action/subAction 조합을 반환한다")
    func ml_returns_valid_action_contract() {
        let result = ext.checkByML(message: "아무 의미 없는 테스트 문장")

        let validActions: [ILMessageFilterAction] = [
            .junk,
            .none
        ]

        #expect(validActions.contains(result.0))
        #expect(result.1 == .none)
    }
    
    @Test("같은 입력에 대해 ML 결과는 일관된다")
    func ml_same_input_returns_same_result() {
        let msg = "무료 대출 지금 가능"

        let r1 = ext.checkByML(message: msg)
        let r2 = ext.checkByML(message: msg)
        let r3 = ext.checkByML(message: msg)

        #expect(r1.0 == r2.0)
        #expect(r2.0 == r3.0)
    }
    
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
