//
//  SpamKillerPolicyTests.swift
//  SpamKillerTests
//
//  Created by 김동현 on 12/22/25.
//

import Testing
import SpamKillerMessageFilter
import IdentityLookup

struct PolicyTests {

    let ext = MessageFilterExtension()

    @Test("빈 문자열은 정책에 의해 .none을 반환한다")
    func empty_message_policy() {
        let result = ext.applyPolicy(message: "")
        #expect(result?.0 == ILMessageFilterAction.none)
    }

    @Test("숫자만 있는 메시지는 정책에 의해 .none을 반환한다")
    func numbers_only_policy() {
        let result = ext.applyPolicy(message: "123456")
        #expect(result?.0 == ILMessageFilterAction.none)
    }

    @Test("아주 짧은 메시지는 정책에 의해 .none을 반환한다")
    func short_message_policy() {
        let result = ext.applyPolicy(message: "ㅎ")
        #expect(result?.0 == ILMessageFilterAction.none)
    }

    @Test("정상 메시지는 정책에 걸리지 않는다")
    func normal_message_passes_policy() {
        let result = ext.applyPolicy(message: "오늘 저녁 뭐 먹을까")
        #expect(result == nil)
    }
}
